"""
B2BValue Memory Architecture
----------------------------
A multi-tiered memory and knowledge system for enterprise agent architectures.

This module provides a comprehensive memory system with:
1. Working Memory - Ephemeral context during workflow execution
2. Episodic Memory - Short-term storage of complete workflow executions
3. Semantic Memory - Long-term knowledge store with vector embeddings
4. Knowledge Graph - Relationship mapping between entities

All components adhere to the Model Context Protocol (MCP) and enterprise governance requirements.
"""

from src.memory.core import MemoryManager
from src.memory.working import WorkingMemory
from src.memory.episodic import EpisodicMemory
from src.memory.semantic import SemanticMemory
from src.memory.knowledge_graph import KnowledgeGraph
from src.memory.types import (
    MemoryEntity, 
    ContextMemoryEntity,
    WorkflowMemoryEntity,
    KnowledgeEntity,
    RelationshipEntity,
    MemoryAccess, 
    DataSensitivity,
    MemoryTier,
    AuditLogEntry,
    MemoryAccessControl
)

__all__ = [
    'MemoryManager', 
    'WorkingMemory', 
    'EpisodicMemory', 
    'SemanticMemory', 
    'KnowledgeGraph',
    'MemoryEntity',
    'ContextMemoryEntity',
    'WorkflowMemoryEntity',
    'KnowledgeEntity',
    'RelationshipEntity',
    'MemoryAccess',
    'DataSensitivity',
    'MemoryTier',
    'AuditLogEntry',
    'MemoryAccessControl'
]
