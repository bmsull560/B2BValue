#!/usr/bin/env python3
"""
B2BValue Memory Integration Tests

This module contains integration tests for the B2BValue memory architecture,
ensuring compliance with Global Rules and proper integration with agents.
"""

import asyncio
import os
import sys
import unittest
import tempfile
import shutil
import json
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.memory import (
    MemoryManager, 
    MemoryEntity, 
    ContextMemoryEntity, 
    WorkflowMemoryEntity,
    KnowledgeEntity,
    RelationshipEntity,
    MemoryTier,
    MemoryAccess,
    DataSensitivity
)
from src.agents.core.mcp_client import MCPClient
from src.agents.core.agent_base import BaseAgent, AgentResult, AgentStatus

class TestAgent(BaseAgent):
    """Test agent for memory integration testing."""
    
    def __init__(self, agent_id: str, mcp_client: MCPClient, config: Dict[str, Any]):
        super().__init__(agent_id, mcp_client, config)
        self.test_data = config.get("test_data", {})
        
    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        """Execute test agent logic."""
        # Get workflow context from MCP (following Rule 1.1)
        context = inputs.get("workflow_context", {})
        
        # Generate result data
        result_data = {
            f"{self.agent_id}_result": self.test_data.get("result", "Test result"),
            f"{self.agent_id}_timestamp": datetime.utcnow().isoformat(),
            "processed_inputs": list(inputs.keys())
        }
        
        # Return result (will be written to MCP by execute_with_resilience)
        return AgentResult(
            status=AgentStatus.COMPLETED,
            data=result_data,
            execution_time_ms=100,
            confidence_score=0.95
        )

class MemoryIntegrationTest(unittest.TestCase):
    """Integration tests for memory system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for memory storage
        self.test_dir = tempfile.mkdtemp()
        self.working_dir = os.path.join(self.test_dir, "working")
        self.episodic_dir = os.path.join(self.test_dir, "episodic")
        self.semantic_dir = os.path.join(self.test_dir, "semantic")
        self.graph_dir = os.path.join(self.test_dir, "graph")
        
        # Create subdirectories
        for dir_path in [self.working_dir, self.episodic_dir, self.semantic_dir, self.graph_dir]:
            os.makedirs(os.path.join(dir_path, "entities"), exist_ok=True)
            os.makedirs(os.path.join(dir_path, "indexes"), exist_ok=True)
        
        # Initialize memory manager with test directories
        self.memory_manager = MemoryManager(
            working_memory_path=self.working_dir,
            episodic_memory_path=self.episodic_dir,
            semantic_memory_path=self.semantic_dir,
            knowledge_graph_path=self.graph_dir
        )
        self.memory_manager.initialize()
        
        # Create MCP client
        self.mcp_client = MCPClient(self.memory_manager)
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directories
        shutil.rmtree(self.test_dir)
        
    def test_rule_1_1_canonical_data_source(self):
        """Test Rule 1.1 - Canonical Data Source."""
        async def run_test():
            # Start workflow
            workflow_id = await self.mcp_client.start_workflow(
                workflow_name="Test Workflow",
                user_id="test_user"
            )
            
            # Store test data in context
            test_data = {"test_key": "test_value"}
            await self.mcp_client.update_context("test_agent", test_data)
            
            # Create agent that reads from MCP
            agent = TestAgent("reader_agent", self.mcp_client, {})
            
            # Execute agent
            result = await agent.execute_with_resilience({})
            
            # Verify agent read from MCP
            self.assertIn("workflow_context", result.data["processed_inputs"])
            
            # Verify workflow completion
            await self.mcp_client.complete_workflow()
            
            return workflow_id
            
        workflow_id = asyncio.run(run_test())
        self.assertIsNotNone(workflow_id)
        
    def test_rule_1_2_output_to_mcp(self):
        """Test Rule 1.2 - Output to MCP."""
        async def run_test():
            # Start workflow
            workflow_id = await self.mcp_client.start_workflow(
                workflow_name="Test Workflow",
                user_id="test_user"
            )
            
            # Create agent with test data
            test_data = {"result": "specific_test_value"}
            agent = TestAgent("writer_agent", self.mcp_client, {"test_data": test_data})
            
            # Execute agent
            await agent.execute_with_resilience({})
            
            # Verify data was written to MCP
            context = await self.mcp_client.get_context()
            self.assertIn("writer_agent_result", context)
            self.assertEqual(context["writer_agent_result"], "specific_test_value")
            
            # Complete workflow
            await self.mcp_client.complete_workflow()
            
            return workflow_id
            
        workflow_id = asyncio.run(run_test())
        self.assertIsNotNone(workflow_id)
        
    def test_rule_1_3_data_validation(self):
        """Test Rule 1.3 - Data Validation."""
        async def run_test():
            # Start workflow
            workflow_id = await self.mcp_client.start_workflow(
                workflow_name="Test Workflow",
                user_id="test_user"
            )
            
            # Set validation rules
            self.mcp_client.set_validation_rules({
                "test_number": {"type": "number", "min": 0, "max": 100},
                "test_string": {"type": "string", "minLength": 3}
            })
            
            # Test valid data
            valid_data = {"test_number": 50, "test_string": "valid"}
            await self.mcp_client.update_context("test_agent", valid_data)
            
            # Get context and verify data was stored
            context = await self.mcp_client.get_context()
            self.assertEqual(context["test_number"], 50)
            self.assertEqual(context["test_string"], "valid")
            
            # Complete workflow
            await self.mcp_client.complete_workflow()
            
            return workflow_id
            
        workflow_id = asyncio.run(run_test())
        self.assertIsNotNone(workflow_id)
        
    def test_rule_1_4_immutability_of_records(self):
        """Test Rule 1.4 - Immutability of Records."""
        async def run_test():
            # Start workflow
            workflow_id = await self.mcp_client.start_workflow(
                workflow_name="Test Workflow",
                user_id="test_user"
            )
            
            # Create initial data
            initial_data = {"test_key": "initial_value"}
            await self.mcp_client.update_context("agent1", initial_data)
            
            # Get context ID after first update
            context1 = await self.mcp_client.get_context()
            context1_id = self.mcp_client._current_context_id
            
            # Update with new data
            updated_data = {"test_key": "updated_value"}
            await self.mcp_client.update_context("agent2", updated_data)
            
            # Get context ID after second update
            context2 = await self.mcp_client.get_context()
            context2_id = self.mcp_client._current_context_id
            
            # Verify context IDs are different (new record created)
            self.assertNotEqual(context1_id, context2_id)
            
            # Verify latest context has updated value
            self.assertEqual(context2["test_key"], "updated_value")
            
            # Complete workflow
            await self.mcp_client.complete_workflow()
            
            # Get workflow history
            workflows = await self.memory_manager.search(
                {"workflow_id": workflow_id},
                MemoryTier.EPISODIC,
                limit=1
            )
            workflow = workflows[0]
            
            # Verify workflow has context versions
            self.assertIsNotNone(workflow.context_versions)
            self.assertGreaterEqual(len(workflow.context_versions), 2)
            
            return workflow_id
            
        workflow_id = asyncio.run(run_test())
        self.assertIsNotNone(workflow_id)
        
    def test_memory_tiers_integration(self):
        """Test integration between all memory tiers."""
        async def run_test():
            # Start workflow
            workflow_id = await self.mcp_client.start_workflow(
                workflow_name="Integration Test",
                user_id="test_user",
                customer_id="test_customer"
            )
            
            # 1. Working Memory - Context data
            await self.mcp_client.update_context("test_agent", {
                "customer_name": "Test Customer",
                "project_value": 100000
            })
            
            # 2. Semantic Memory - Knowledge entity
            knowledge_id = await self.mcp_client.store_knowledge(
                content="Test customer is interested in AI solutions",
                content_type="text",
                source="sales_meeting",
                confidence=0.9
            )
            
            # 3. Knowledge Graph - Create relationship
            relationship_id = await self.mcp_client.create_relationship(
                from_id=workflow_id,
                to_id=knowledge_id,
                relation_type="references",
                strength=0.8
            )
            
            # 4. Complete workflow (updates Episodic Memory)
            await self.mcp_client.complete_workflow(
                status="completed",
                result={"outcome": "success"}
            )
            
            # Verify data in each tier
            
            # Working Memory - Context
            context = await self.mcp_client.get_context()
            self.assertEqual(context["customer_name"], "Test Customer")
            
            # Episodic Memory - Workflow
            workflows = await self.memory_manager.search(
                {"workflow_id": workflow_id},
                MemoryTier.EPISODIC,
                limit=1
            )
            self.assertEqual(len(workflows), 1)
            self.assertEqual(workflows[0].workflow_status, "completed")
            
            # Semantic Memory - Knowledge
            knowledge = await self.memory_manager.retrieve(knowledge_id, MemoryTier.SEMANTIC)
            self.assertIsNotNone(knowledge)
            self.assertEqual(knowledge.content, "Test customer is interested in AI solutions")
            
            # Knowledge Graph - Relationship
            relationship = await self.memory_manager.retrieve(relationship_id, MemoryTier.KNOWLEDGE_GRAPH)
            self.assertIsNotNone(relationship)
            self.assertEqual(relationship.from_id, workflow_id)
            self.assertEqual(relationship.to_id, knowledge_id)
            
            return workflow_id
            
        workflow_id = asyncio.run(run_test())
        self.assertIsNotNone(workflow_id)
        
    def test_semantic_search(self):
        """Test semantic search functionality."""
        async def run_test():
            # Store multiple knowledge entities
            knowledge_ids = []
            for i in range(5):
                knowledge_id = await self.mcp_client.store_knowledge(
                    content=f"Knowledge entity {i} about {'AI' if i % 2 == 0 else 'business value'}",
                    content_type="text",
                    source="test"
                )
                knowledge_ids.append(knowledge_id)
                
            # Perform semantic search
            results = await self.mcp_client.semantic_search("AI knowledge")
            
            # Verify results
            self.assertGreaterEqual(len(results), 1)
            
            return knowledge_ids
            
        knowledge_ids = asyncio.run(run_test())
        self.assertEqual(len(knowledge_ids), 5)
        
    def test_workflow_history(self):
        """Test workflow history retrieval."""
        async def run_test():
            # Create multiple workflows for same customer
            customer_id = "history_test_customer"
            workflow_ids = []
            
            for i in range(3):
                workflow_id = await self.mcp_client.start_workflow(
                    workflow_name=f"History Test {i}",
                    user_id="test_user",
                    customer_id=customer_id
                )
                workflow_ids.append(workflow_id)
                
                # Add some context data
                await self.mcp_client.update_context("test_agent", {
                    "iteration": i,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Complete workflow
                await self.mcp_client.complete_workflow(
                    status="completed",
                    result={"iteration": i}
                )
                
            # Get workflow history for customer
            history = await self.mcp_client.get_workflow_history(customer_id=customer_id)
            
            # Verify history
            self.assertEqual(len(history), 3)
            
            return workflow_ids
            
        workflow_ids = asyncio.run(run_test())
        self.assertEqual(len(workflow_ids), 3)
        
if __name__ == "__main__":
    unittest.main()
