#!/usr/bin/env python3
"""
B2BValue Memory Integration Example

This script demonstrates how to use the B2BValue memory architecture
with agents to create a simple workflow that follows the Model Context
Protocol (MCP) rules.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.memory import MemoryManager, DataSensitivity
from src.agents.core.mcp_client import MCPClient
from src.agents.core.agent_base import BaseAgent, AgentResult, AgentStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("memory_example")

# Example agent that adheres to MCP rules
class ExampleAgent(BaseAgent):
    """Example agent that demonstrates memory integration."""
    
    def __init__(self, agent_id: str, mcp_client: MCPClient, config: Dict[str, Any]):
        super().__init__(agent_id, mcp_client, config)
        
    async def execute(self, inputs: Dict[str, Any]) -> AgentResult:
        """Execute agent logic and store results in MCP."""
        logger.info(f"Agent {self.agent_id} executing with inputs: {inputs}")
        
        # Simulate some processing time
        await asyncio.sleep(1)
        
        # Get workflow context from MCP (following Rule 1.1)
        context = inputs.get("workflow_context", {})
        logger.info(f"Agent {self.agent_id} retrieved context: {context}")
        
        # Simulate agent processing
        result_data = {
            f"{self.agent_id}_result": f"Processed at {datetime.utcnow().isoformat()}",
            f"{self.agent_id}_confidence": 0.95,
            "processed_inputs": list(inputs.keys())
        }
        
        # Return result (will be written to MCP by execute_with_resilience)
        return AgentResult(
            status=AgentStatus.COMPLETED,
            data=result_data,
            execution_time_ms=1000,
            confidence_score=0.95
        )

async def run_example_workflow():
    """Run an example workflow using the memory architecture."""
    logger.info("Starting example workflow")
    
    # Create data directories if they don't exist
    os.makedirs("./data/working/entities", exist_ok=True)
    os.makedirs("./data/working/indexes", exist_ok=True)
    os.makedirs("./data/episodic/entities", exist_ok=True)
    os.makedirs("./data/episodic/indexes", exist_ok=True)
    os.makedirs("./data/semantic/entities", exist_ok=True)
    os.makedirs("./data/semantic/indexes", exist_ok=True)
    os.makedirs("./data/graph/entities", exist_ok=True)
    os.makedirs("./data/graph/indexes", exist_ok=True)
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    memory_manager.initialize()
    
    # Create MCP client
    mcp_client = MCPClient(memory_manager)
    
    # Start a new workflow
    workflow_id = await mcp_client.start_workflow(
        workflow_name="Example Workflow",
        user_id="example_user",
        customer_id="example_customer"
    )
    logger.info(f"Started workflow with ID: {workflow_id}")
    
    # Create and run first agent
    agent1 = ExampleAgent("data_collector", mcp_client, {"timeout_seconds": 10})
    result1 = await agent1.execute_with_resilience({
        "input_data": "Sample input for first agent"
    })
    logger.info(f"Agent 1 result: {result1}")
    
    # Create and run second agent that builds on first agent's results
    agent2 = ExampleAgent("data_processor", mcp_client, {"timeout_seconds": 10})
    result2 = await agent2.execute_with_resilience({
        "additional_input": "Sample input for second agent"
    })
    logger.info(f"Agent 2 result: {result2}")
    
    # Store some knowledge in semantic memory
    knowledge_id = await mcp_client.store_knowledge(
        content="This is an example knowledge entity that demonstrates semantic memory storage.",
        content_type="text",
        source="example_workflow",
        confidence=0.9,
        sensitivity=DataSensitivity.INTERNAL
    )
    logger.info(f"Stored knowledge with ID: {knowledge_id}")
    
    # Create a relationship in the knowledge graph
    relationship_id = await mcp_client.create_relationship(
        from_id=workflow_id,
        to_id=knowledge_id,
        relation_type="generated",
        strength=0.8,
        bidirectional=False,
        properties={"timestamp": datetime.utcnow().isoformat()}
    )
    logger.info(f"Created relationship with ID: {relationship_id}")
    
    # Complete the workflow
    await mcp_client.complete_workflow(
        status="completed",
        result={"summary": "Example workflow completed successfully"}
    )
    logger.info("Workflow completed")
    
    # Demonstrate semantic search
    search_results = await mcp_client.semantic_search("example knowledge")
    logger.info(f"Semantic search found {len(search_results)} results")
    
    # Demonstrate workflow history retrieval
    history = await mcp_client.get_workflow_history(customer_id="example_customer")
    logger.info(f"Found {len(history)} workflow history records")
    
    return workflow_id

if __name__ == "__main__":
    asyncio.run(run_example_workflow())
