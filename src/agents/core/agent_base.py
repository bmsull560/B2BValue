from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import logging

# Import our real MCP client
from src.agents.core.mcp_client import MCPClient

class CircuitBreakerOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.open = False
    async def __aenter__(self):
        if self.open:
            raise CircuitBreakerOpen()
        return self
    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.open = True
        else:
            self.failures = 0
            self.open = False

class RetryPolicy:
    def __init__(self, max_attempts=3, backoff_factor=2):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
    async def execute(self, func, *args, **kwargs):
        attempt = 0
        while attempt < self.max_attempts:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt == self.max_attempts:
                    raise e
                await asyncio.sleep(self.backoff_factor ** attempt)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: Optional[Any] = None

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class AgentResult:
    status: AgentStatus
    data: Dict[str, Any]
    execution_time_ms: int
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    confidence_score: Optional[float] = None
    error_details: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, mcp_client: MCPClient, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.mcp_client = mcp_client
        self.config = config
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            reset_timeout=config.get('reset_timeout', 60)
        )
        self.retry_policy = RetryPolicy(
            max_attempts=config.get('max_retries', 3),
            backoff_factor=config.get('backoff_factor', 2)
        )
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        pass
    async def execute_with_resilience(self, inputs: Dict[str, Any]) -> AgentResult:
        start_time = time.time()
        try:
            validation_result = await self.validate_inputs(inputs)
            if not validation_result.is_valid:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    data={},
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    error_details=f"Input validation failed: {validation_result.errors}"
                )
            async with self.circuit_breaker:
                result = await self.retry_policy.execute(
                    self._execute_with_context,
                    inputs
                )
                if result.status == AgentStatus.COMPLETED:
                    await self.update_context(result.data)
                return result
        except CircuitBreakerOpen:
            return AgentResult(
                status=AgentStatus.FAILED,
                data={},
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_details="Circuit breaker open - service unavailable"
            )
        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                data={},
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_details=str(e)
            )
    async def _execute_with_context(self, inputs: Dict[str, Any]) -> AgentResult:
        context = await self.get_context()
        execution_context = {
            **inputs,
            "workflow_context": context,
            "agent_id": self.agent_id,
            "execution_timestamp": time.time()
        }
        try:
            result = await asyncio.wait_for(
                self.execute(execution_context),
                timeout=self.config.get('timeout_seconds', 300)
            )
            return result
        except asyncio.TimeoutError:
            return AgentResult(
                status=AgentStatus.TIMEOUT,
                data={},
                execution_time_ms=self.config.get('timeout_seconds', 300) * 1000,
                error_details="Agent execution timeout"
            )
    async def get_context(self) -> Dict[str, Any]:
        return await self.mcp_client.get_context()
    async def update_context(self, data: Dict[str, Any]) -> None:
        await self.mcp_client.update_context(self.agent_id, data)
    async def validate_inputs(self, inputs: Dict[str, Any]) -> ValidationResult:
        return ValidationResult(is_valid=True, errors=[])  # Placeholder

# Simple LRU cache for demonstration
class LRUCache(dict):
    def __init__(self, maxsize=100):
        super().__init__()
        self.maxsize = maxsize
        self._order = []
    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._order.remove(key)
        self._order.append(key)
        return value
    def __setitem__(self, key, value):
        if key in self:
            self._order.remove(key)
        elif len(self._order) >= self.maxsize:
            oldest = self._order.pop(0)
            del self[oldest]
        super().__setitem__(key, value)
        self._order.append(key)
    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

# LLMAgent: for LLM-powered agents
class LLMAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_client: MCPClient, config: Dict[str, Any]):
        super().__init__(agent_id, mcp_client, config)
        self.llm_client = None  # Placeholder for actual LLM client
        self.prompt_cache = LRUCache(maxsize=config.get('prompt_cache_size', 100))
    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        start_time = time.time()
        try:
            prompt = await self._build_prompt(inputs)
            cache_key = self._generate_cache_key(prompt)
            cached_result = self.prompt_cache.get(cache_key)
            if cached_result and self.config.get('enable_cache', True):
                return AgentResult(
                    status=AgentStatus.COMPLETED,
                    data=cached_result,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    tokens_used=0,
                    cost_usd=0.0
                )
            # Placeholder LLM call
            response = {"output": "LLM response", "confidence": 0.9}
            parsed_output = await self._parse_and_validate_response(response)
            if parsed_output.get('confidence', 0.0) > 0.8:
                self.prompt_cache[cache_key] = parsed_output
            return AgentResult(
                status=AgentStatus.COMPLETED,
                data=parsed_output,
                execution_time_ms=int((time.time() - start_time) * 1000),
                tokens_used=100,
                cost_usd=0.02,
                confidence_score=parsed_output.get('confidence', 0.0)
            )
        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                data={},
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_details=str(e)
            )
    async def _build_prompt(self, inputs: Dict[str, Any]) -> str:
        return f"Prompt with context: {inputs}"
    def _generate_cache_key(self, prompt: str) -> str:
        return str(hash(prompt))
    async def _parse_and_validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder parsing/validation
        return response

# CalculationAgent: for rule-based/calculative agents
class CalculationAgent(BaseAgent):
    def __init__(self, agent_id: str, mcp_client: MCPClient, config: Dict[str, Any]):
        super().__init__(agent_id, mcp_client, config)
        self.rules_engine = config.get('rules_engine')  # Placeholder
    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        start_time = time.time()
        try:
            context = inputs.get('workflow_context', {})
            baseline_metrics = context.get('baseline_metrics', {})
            enriched_data = context.get('enriched_data', {})
            # Placeholder for calculation logic
            calculation_result = {"result": 42, "confidence": 0.95}
            return AgentResult(
                status=AgentStatus.COMPLETED,
                data=calculation_result,
                execution_time_ms=int((time.time() - start_time) * 1000),
                confidence_score=calculation_result.get('confidence', 0.0)
            )
        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                data={},
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_details=str(e)
            )
