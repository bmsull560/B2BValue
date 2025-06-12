# B2BValue Memory Architecture

## Overview

The B2BValue Memory Architecture is a comprehensive multi-tiered memory system designed for the B2BValue AI-powered Business Value Model. It provides enterprise-grade memory capabilities for AI agents, ensuring data integrity, security, and compliance with the Model Context Protocol (MCP).

## Architecture

The memory system consists of four specialized tiers:

1. **Working Memory** (`working.py`)
   - Ephemeral context during workflow execution
   - In-memory storage with optional persistence
   - TTL-based expiration for temporary data
   - Fast access for active workflows

2. **Episodic Memory** (`episodic.py`)
   - Persistent storage of complete workflow execution histories
   - File-based storage with indexing
   - Captures entire workflow lifecycles
   - Supports historical analysis and auditing

3. **Semantic Memory** (`semantic.py`)
   - Long-term knowledge store with vector embeddings
   - Enables semantic search capabilities
   - Stores structured knowledge entities
   - Supports metadata-based and semantic retrieval

4. **Knowledge Graph** (`knowledge_graph.py`)
   - Stores relationships between entities
   - Supports graph analytics and complex queries
   - Bidirectional relationship management
   - Path finding and graph traversal

## Core Components

- **Memory Manager** (`core.py`) - Central orchestrator for all memory tiers
  - Enforces access control and security policies
  - Manages audit logging and data integrity
  - Provides unified API for memory operations
  - Coordinates cross-tier operations

- **Memory Types** (`types.py`) - Defines data structures and enumerations
  - Memory entity base classes and specialized subclasses
  - Access control and data sensitivity levels
  - Audit log entry structures
  - Memory tier enumerations

## MCP Integration

The Model Context Protocol (MCP) is implemented through the `MCPClient` class, which ensures:

1. **Rule 1.1 - Canonical Data Source**: All agents read inputs exclusively from the MCP
2. **Rule 1.2 - Output to MCP**: All agent outputs are written back to the MCP
3. **Rule 1.3 - Data Validation**: Inputs are validated against defined rules
4. **Rule 1.4 - Immutability of Records**: Data is treated as immutable with versioning

## Usage

### Basic Memory Operations

```python
from src.memory import MemoryManager, MemoryTier, KnowledgeEntity

# Initialize memory manager
memory_manager = MemoryManager()
memory_manager.initialize()

# Store a knowledge entity
entity = KnowledgeEntity(
    content="Important business knowledge",
    content_type="text",
    source="research"
)
entity_id = await memory_manager.store(entity)

# Retrieve an entity
retrieved_entity = await memory_manager.retrieve(entity_id, MemoryTier.SEMANTIC)

# Search for entities
results = await memory_manager.search({"source": "research"}, MemoryTier.SEMANTIC)

# Delete an entity
await memory_manager.delete(entity_id, MemoryTier.SEMANTIC)
```

### Agent Integration with MCP

```python
from src.agents.core.mcp_client import MCPClient
from src.agents.core.agent_base import BaseAgent, AgentResult, AgentStatus

# Create MCP client
mcp_client = MCPClient(memory_manager)

# Start a workflow
workflow_id = await mcp_client.start_workflow(
    workflow_name="Business Case Generation",
    user_id="analyst_123",
    customer_id="customer_456"
)

# Create an agent that uses MCP
class BusinessCaseAgent(BaseAgent):
    async def execute(self, inputs):
        # Get context from MCP (Rule 1.1)
        context = inputs.get("workflow_context", {})
        
        # Process data
        result_data = {"roi": 2.5, "payback_period": 18}
        
        # Return result (will be written to MCP by execute_with_resilience)
        return AgentResult(
            status=AgentStatus.COMPLETED,
            data=result_data,
            execution_time_ms=1000
        )

# Execute agent
agent = BusinessCaseAgent("roi_calculator", mcp_client, {})
result = await agent.execute_with_resilience({
    "additional_inputs": "value"
})

# Complete workflow
await mcp_client.complete_workflow(
    status="completed",
    result={"summary": "Business case completed"}
)
```

### Semantic Search

```python
# Store knowledge with embeddings
knowledge_id = await mcp_client.store_knowledge(
    content="AI solutions can increase productivity by 30%",
    content_type="text",
    source="research_paper",
    confidence=0.9
)

# Perform semantic search
results = await mcp_client.semantic_search("productivity improvements")
```

### Knowledge Graph Operations

```python
# Create entities
customer_id = await mcp_client.store_knowledge(
    content={"name": "Acme Corp", "industry": "Manufacturing"},
    content_type="json",
    source="crm"
)

product_id = await mcp_client.store_knowledge(
    content={"name": "AI Optimizer", "category": "Productivity"},
    content_type="json",
    source="product_catalog"
)

# Create relationship
relationship_id = await mcp_client.create_relationship(
    from_id=customer_id,
    to_id=product_id,
    relation_type="interested_in",
    strength=0.7,
    bidirectional=False
)

# Find paths between entities
paths = await memory_manager.find_paths(
    start_id=customer_id,
    end_id=product_id,
    max_depth=3
)
```

## Security and Compliance

The memory system implements:

- **Access Control**: Role-based access control for all memory operations
- **Data Sensitivity**: Classification of data sensitivity levels
- **Audit Logging**: Comprehensive logging of all memory operations
- **Data Integrity**: Cryptographic checksums to verify data integrity

## Testing

Run the comprehensive test suite to verify memory functionality:

```bash
python -m unittest discover -s tests/memory
```

## Example Applications

See the `Examples` directory for sample applications:

- `memory_integration_example.py`: Demonstrates basic memory operations and agent integration

## Next Steps

1. Replace the semantic embedding placeholder with a real embedding model
2. Implement monitoring and alerting for memory operations
3. Enhance documentation with more usage examples
4. Develop additional integration tests for agent-memory interactions
