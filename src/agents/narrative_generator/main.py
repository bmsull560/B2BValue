import os
import yaml
from typing import Dict, Any
import asyncio
from src.agents.core.agent_base import LLMAgent, MCPClient, AgentResult

class NarrativeGeneratorAgent(LLMAgent):
    def __init__(self, agent_definition_path: str, mcp_client: MCPClient, config: Dict[str, Any]):
        self.definition = self._load_definition(agent_definition_path)
        agent_id = self.definition.get('agent_id', 'narrative_generator')
        super().__init__(agent_id, mcp_client, config)
        print(f"Initialized agent: {self.agent_id}")

    def _load_definition(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Agent definition file not found at: {path}")
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        print(f"Executing {self.agent_id}...")
        result = {"narrative": "This is a generated business case narrative."}
        return AgentResult(status=None, data=result, execution_time_ms=100)
