import unittest
import asyncio
from src.agents.core.mcp_client import MCPClient
from src.memory.core import MemoryManager
from src.memory.types import KnowledgeEntity, MemoryTier
from datetime import datetime

class TestAgentMemoryIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mm = MemoryManager()
        self.mm.initialize()
        self.mcp = MCPClient(self.mm)

    async def test_agent_store_and_search_knowledge(self):
        entity = KnowledgeEntity(
            id="agent-know-1",
            content="AI agent integration test.",
            content_type="text",
            creator_id="agent",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sensitivity=None,
            tier=MemoryTier.SEMANTIC
        )
        await self.mcp.store_knowledge(entity, user_id="agent")
        results = await self.mcp.semantic_search("integration test", limit=1)
        self.assertTrue(any("integration test" in r.content or "AI agent" in r.content for r in results))

if __name__ == "__main__":
    unittest.main()
