import unittest
from src.memory import MemoryManager, ContextMemoryEntity, WorkflowMemoryEntity, KnowledgeEntity, RelationshipEntity, MemoryTier, DataSensitivity
from datetime import datetime

class TestMemoryValidation(unittest.TestCase):
    def setUp(self):
        self.mm = MemoryManager()
        self.mm.initialize()

    def test_context_entity_validation(self):
        entity = ContextMemoryEntity(
            workflow_id="wf1", version=1, data={"foo": "bar"}
        )
        entity.tier = MemoryTier.WORKING
        entity.sensitivity = DataSensitivity.INTERNAL
        # Should not raise
        self.mm._validate_entity(entity)

    def test_missing_required_field(self):
        entity = ContextMemoryEntity(
            workflow_id="wf1", version=1, data={}
        )
        entity.tier = MemoryTier.WORKING
        entity.sensitivity = DataSensitivity.INTERNAL
        del entity.workflow_id
        with self.assertRaises(AttributeError):
            self.mm._validate_entity(entity)

    def test_invalid_type(self):
        entity = KnowledgeEntity(
            content=123,  # should be str
        )
        entity.tier = MemoryTier.SEMANTIC
        entity.sensitivity = DataSensitivity.INTERNAL
        with self.assertRaises(AssertionError):
            self.mm._validate_entity(entity)

    def test_relationship_validation(self):
        entity = RelationshipEntity(
            from_id="a", to_id="b", relation_type="related_to"
        )
        entity.tier = MemoryTier.GRAPH
        entity.sensitivity = DataSensitivity.INTERNAL
        self.mm._validate_entity(entity)

if __name__ == "__main__":
    unittest.main()
