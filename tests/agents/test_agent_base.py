import unittest
from src.agents.core.agent_base import BaseAgent, AgentResult, AgentStatus
from src.agents.core.mcp_client import MCPClient
from src.memory import MemoryManager

class DummyAgent(BaseAgent):
    def __init__(self, agent_id, mcp_client, config):
        super().__init__(agent_id, mcp_client, config)
    async def execute(self, inputs):
        # Simulate agent logic with error handling
        if 'fail' in inputs:
            raise ValueError("Simulated agent failure")
        return AgentResult(
            status=AgentStatus.SUCCESS,
            data={"echo": inputs},
            execution_time_ms=5,
            confidence_score=1.0
        )

class TestAgentBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mm = MemoryManager()
        self.mm.initialize()
        self.mcp = MCPClient(self.mm)
        self.agent = DummyAgent("dummy", self.mcp, {})

    async def test_execute_success(self):
        result = await self.agent.execute({"foo": "bar"})
        self.assertEqual(result.status, AgentStatus.SUCCESS)
        self.assertIn("echo", result.data)
        self.assertEqual(result.data["echo"], {"foo": "bar"})

    async def test_execute_failure(self):
        with self.assertRaises(ValueError):
            await self.agent.execute({"fail": True})

    async def test_execute_empty_input(self):
        result = await self.agent.execute({})
        self.assertEqual(result.status, AgentStatus.SUCCESS)
        self.assertIn("echo", result.data)
        self.assertEqual(result.data["echo"], {})

    async def test_execute_none_input(self):
        with self.assertRaises(TypeError):
            await self.agent.execute(None)

    async def test_execute_invalid_input_type(self):
        with self.assertRaises(TypeError):
            await self.agent.execute("invalid input")

    async def test_execute_input_with_invalid_keys(self):
        result = await self.agent.execute({"invalid_key": "value"})
        self.assertEqual(result.status, AgentStatus.SUCCESS)
        self.assertIn("echo", result.data)
        self.assertEqual(result.data["echo"], {"invalid_key": "value"})

if __name__ == "__main__":
    unittest.main()
