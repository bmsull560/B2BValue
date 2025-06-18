import unittest
import asyncio
from src.memory.semantic import SemanticMemory
from src.memory.types import KnowledgeEntity, MemoryTier
from datetime import datetime

class TestSemanticMemory(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.memory = SemanticMemory(storage_path="./test_data/semantic_test", embedding_dim=384)

    async def asyncTearDown(self):
        import shutil
        shutil.rmtree("./test_data/semantic_test", ignore_errors=True)

    async def test_store_and_retrieve_entity(self):
        entity = KnowledgeEntity(
            id="test1",
            content="Business value AI memory test.",
            content_type="text",
            creator_id="tester",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sensitivity=None,
            tier=MemoryTier.SEMANTIC
        )
        await self.memory.store(entity)
        retrieved = await self.memory.retrieve("test1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "Business value AI memory test.")
        self.assertIsInstance(retrieved.vector_embedding, list)
        self.assertEqual(len(retrieved.vector_embedding), 384)

    async def test_semantic_search(self):
        entity1 = KnowledgeEntity(
            id="ent1",
            content="AI for business value.",
            content_type="text",
            creator_id="tester",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sensitivity=None,
            tier=MemoryTier.SEMANTIC
        )
        entity2 = KnowledgeEntity(
            id="ent2",
            content="Enterprise memory architecture.",
            content_type="text",
            creator_id="tester",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sensitivity=None,
            tier=MemoryTier.SEMANTIC
        )
        await self.memory.store(entity1)
        await self.memory.store(entity2)
        results = await self.memory.semantic_search("business value", limit=2)
        self.assertTrue(any("business value" in r.content for r in results) or len(results) > 0)

    async def test_embedding_fallback(self):
        entity = KnowledgeEntity(
            id="fallback",
            content="Fallback embedding test.",
            content_type="text",
            creator_id="tester",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            sensitivity=None,
            tier=MemoryTier.SEMANTIC
        )
        # Simulate missing sentence-transformers by patching import
        import builtins
        orig_import = builtins.__import__
        def fake_import(name, *args, **kwargs):
            if name == 'sentence_transformers':
                raise ImportError()
            return orig_import(name, *args, **kwargs)
        builtins.__import__ = fake_import
        await self.memory.store(entity)
        builtins.__import__ = orig_import
        retrieved = await self.memory.retrieve("fallback")
        self.assertIsInstance(retrieved.vector_embedding, list)
        self.assertEqual(len(retrieved.vector_embedding), 384)

if __name__ == "__main__":
    unittest.main()
