"""
Types and enumerations for the B2BValue Memory Architecture.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid


class DataSensitivity(Enum):
    """Defines sensitivity levels for data in memory system."""
    PUBLIC = auto()       # Can be shared freely
    INTERNAL = auto()     # Internal to organization
    RESTRICTED = auto()   # Limited access within organization
    CONFIDENTIAL = auto() # Highly sensitive business data
    
    
class MemoryAccess(Enum):
    """Defines access control levels for memory entities."""
    READ = auto()
    WRITE = auto()
    DELETE = auto()
    ADMIN = auto()


class MemoryTier(Enum):
    """Defines the tier/layer where memory is stored."""
    WORKING = auto()  # Ephemeral, in-memory during workflow
    EPISODIC = auto() # Persisted workflow histories
    SEMANTIC = auto() # Long-term knowledge
    GRAPH = auto()    # Relationship data


@dataclass
class MemoryEntity:
    """Base class for all memory entities in the system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    creator_id: str = field(default="system")
    sensitivity: DataSensitivity = field(default=DataSensitivity.INTERNAL)
    tier: MemoryTier = field(default=MemoryTier.WORKING)
    ttl: Optional[int] = field(default=None)  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    version: int = field(default=1)
    checksum: Optional[str] = field(default=None)  # For integrity verification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        result = {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "creator_id": self.creator_id,
            "sensitivity": self.sensitivity.name,
            "tier": self.tier.name,
            "version": self.version,
            "metadata": self.metadata,
            "tags": self.tags,
        }
        
        if self.ttl is not None:
            result["ttl"] = self.ttl
        
        if self.checksum is not None:
            result["checksum"] = self.checksum
            
        return result


@dataclass
class ContextMemoryEntity(MemoryEntity):
    """Represents a context object in working memory."""
    context_data: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = field(default=None)
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stage_id: Optional[str] = field(default=None)
    agent_id: Optional[str] = field(default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        result = super().to_dict()
        result.update({
            "context_data": self.context_data,
            "workflow_id": self.workflow_id,
        })
        
        if self.parent_id is not None:
            result["parent_id"] = self.parent_id
            
        if self.stage_id is not None:
            result["stage_id"] = self.stage_id
            
        if self.agent_id is not None:
            result["agent_id"] = self.agent_id
            
        return result


@dataclass
class WorkflowMemoryEntity(MemoryEntity):
    """Represents a complete workflow execution history."""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = field(default="Unnamed Workflow")
    workflow_status: str = field(default="created")
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    customer_id: Optional[str] = None
    context_versions: List[str] = field(default_factory=list)  # List of context entity IDs
    stages: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        result = super().to_dict()
        result.update({
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "workflow_status": self.workflow_status,
            "start_time": self.start_time.isoformat(),
            "context_versions": self.context_versions,
            "stages": self.stages,
        })
        
        if self.end_time is not None:
            result["end_time"] = self.end_time.isoformat()
            
        if self.result is not None:
            result["result"] = self.result
            
        if self.user_id is not None:
            result["user_id"] = self.user_id
            
        if self.customer_id is not None:
            result["customer_id"] = self.customer_id
            
        return result


@dataclass
class KnowledgeEntity(MemoryEntity):
    """Represents a knowledge item in semantic memory."""
    content: str = field(default="")
    content_type: str = field(default="text")
    vector_embedding: Optional[List[float]] = None
    source: str = field(default="system")
    confidence: float = field(default=1.0)
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        result = super().to_dict()
        result.update({
            "content": self.content,
            "content_type": self.content_type,
            "source": self.source,
            "confidence": self.confidence,
            "references": self.references,
        })
        
        if self.vector_embedding is not None:
            result["vector_embedding"] = self.vector_embedding
            
        return result


@dataclass
class RelationshipEntity(MemoryEntity):
    """Represents a relationship between entities in the knowledge graph."""
    from_id: str = field(default="")
    to_id: str = field(default="")
    relation_type: str = field(default="related_to")
    strength: float = field(default=1.0)
    bidirectional: bool = field(default=False)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        result = super().to_dict()
        result.update({
            "from_id": self.from_id,
            "to_id": self.to_id,
            "relation_type": self.relation_type,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "properties": self.properties,
        })
        return result


@dataclass
class MemoryAccessControl:
    """Defines access control for memory entities."""
    entity_id: str
    roles: Dict[str, List[MemoryAccess]]
    user_overrides: Dict[str, List[MemoryAccess]] = field(default_factory=dict)
    
    def can_access(self, user_id: str, role: str, access_type: MemoryAccess) -> bool:
        """Check if a user with a given role can access entity with specified access type."""
        # Check user-specific overrides first
        if user_id in self.user_overrides and access_type in self.user_overrides[user_id]:
            return True
            
        # Then check role-based permissions
        return role in self.roles and access_type in self.roles[role]


@dataclass
class AuditLogEntry:
    """Represents an entry in the audit log."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    entity_id: str = field(default="")
    action: str = field(default="")
    user_id: str = field(default="system")
    details: Dict[str, Any] = field(default_factory=dict)
    prev_checksum: Optional[str] = field(default=None)
    new_checksum: Optional[str] = field(default=None)
