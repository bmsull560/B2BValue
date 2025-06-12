"""
Core Memory Manager for B2BValue Memory Architecture.

This module provides the central orchestrator for all memory tiers:
- Working Memory (ephemeral context)
- Episodic Memory (workflow history)
- Semantic Memory (knowledge store)
- Knowledge Graph (entity relationships)

The MemoryManager enforces security, compliance, and data governance policies.
"""

import logging
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Union, Type
from datetime import datetime
import asyncio

from src.memory.types import (
    MemoryEntity, ContextMemoryEntity, WorkflowMemoryEntity, 
    KnowledgeEntity, RelationshipEntity, MemoryTier,
    DataSensitivity, MemoryAccess, MemoryAccessControl, AuditLogEntry
)

# Configure logging
logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Central orchestrator for the B2BValue Memory Architecture.
    
    This class manages all memory tiers and provides a unified interface
    for storing, retrieving, and managing memory entities across the system.
    """
    
    def __init__(self):
        """Initialize the memory manager with all memory tier handlers."""
        self._working_memory = None  # Will be set when modules are loaded
        self._episodic_memory = None
        self._semantic_memory = None
        self._knowledge_graph = None
        self._audit_log = []
        self._access_controls: Dict[str, MemoryAccessControl] = {}
        
    def initialize(self, working_memory=None, episodic_memory=None, 
                  semantic_memory=None, knowledge_graph=None):
        """Initialize memory tier handlers."""
        from src.memory.working import WorkingMemory
        from src.memory.episodic import EpisodicMemory
        from src.memory.semantic import SemanticMemory
        from src.memory.knowledge_graph import KnowledgeGraph
        
        self._working_memory = working_memory or WorkingMemory()
        self._episodic_memory = episodic_memory or EpisodicMemory()
        self._semantic_memory = semantic_memory or SemanticMemory()
        self._knowledge_graph = knowledge_graph or KnowledgeGraph()
        
        logger.info("Memory Manager initialized with all tiers")
    
    def _calculate_checksum(self, entity: MemoryEntity) -> str:
        """Calculate a cryptographic checksum for a memory entity."""
        # Convert entity to JSON string representation
        entity_dict = entity.to_dict()
        # Remove existing checksum if present to avoid circular reference
        if 'checksum' in entity_dict:
            del entity_dict['checksum']
            
        # Sort keys to ensure consistent serialization
        entity_json = json.dumps(entity_dict, sort_keys=True)
        # Calculate SHA-256 hash
        return hashlib.sha256(entity_json.encode('utf-8')).hexdigest()
    
    def _log_audit_event(self, entity_id: str, action: str, 
                        user_id: str, details: Dict[str, Any],
                        prev_checksum: Optional[str] = None,
                        new_checksum: Optional[str] = None):
        """Log an audit event for a memory operation."""
        audit_entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            details=details,
            prev_checksum=prev_checksum,
            new_checksum=new_checksum
        )
        self._audit_log.append(audit_entry)
        
        # In production, this would write to a secure audit log store
        logger.info(f"Audit: {action} on {entity_id} by {user_id}")
    
    def _check_access(self, entity_id: str, user_id: str, 
                     role: str, access_type: MemoryAccess) -> bool:
        """Check if user has required access to memory entity."""
        if entity_id not in self._access_controls:
            # Default to restricted if no specific ACL is defined
            return False
        return self._access_controls[entity_id].can_access(user_id, role, access_type)

    def _validate_entity(self, entity: MemoryEntity):
        """Validate entity fields and types according to schema."""
        # Basic type and required field checks for all entities
        assert hasattr(entity, 'id') and isinstance(entity.id, str), "Entity must have string 'id'"
        assert hasattr(entity, 'created_at'), "Entity must have 'created_at' timestamp"
        assert hasattr(entity, 'updated_at'), "Entity must have 'updated_at' timestamp"
        assert hasattr(entity, 'creator_id') and isinstance(entity.creator_id, str), "Entity must have string 'creator_id'"
        assert hasattr(entity, 'sensitivity'), "Entity must have 'sensitivity'"
        assert hasattr(entity, 'tier'), "Entity must have 'tier'"
        # ContextMemoryEntity
        if isinstance(entity, ContextMemoryEntity):
            assert hasattr(entity, 'workflow_id') and isinstance(entity.workflow_id, str), "Context must have workflow_id as str"
            assert hasattr(entity, 'version') and isinstance(entity.version, int), "Context must have version as int"
            assert hasattr(entity, 'data') and isinstance(entity.data, dict), "Context must have data as dict"
        # WorkflowMemoryEntity
        if isinstance(entity, WorkflowMemoryEntity):
            assert hasattr(entity, 'workflow_id') and isinstance(entity.workflow_id, str), "Workflow must have workflow_id as str"
            assert hasattr(entity, 'workflow_name') and isinstance(entity.workflow_name, str), "Workflow must have workflow_name as str"
            assert hasattr(entity, 'workflow_status') and isinstance(entity.workflow_status, str), "Workflow must have workflow_status as str"
            assert hasattr(entity, 'start_time'), "Workflow must have start_time"
        # KnowledgeEntity
        if isinstance(entity, KnowledgeEntity):
            assert hasattr(entity, 'content') and isinstance(entity.content, str), "Knowledge must have content as str"
            assert hasattr(entity, 'content_type') and isinstance(entity.content_type, str), "Knowledge must have content_type as str"
            assert hasattr(entity, 'source') and isinstance(entity.source, str), "Knowledge must have source as str"
            assert hasattr(entity, 'confidence') and isinstance(entity.confidence, float), "Knowledge must have confidence as float"
            assert hasattr(entity, 'references') and isinstance(entity.references, list), "Knowledge must have references as list"
        # RelationshipEntity
        if isinstance(entity, RelationshipEntity):
            assert hasattr(entity, 'from_id') and isinstance(entity.from_id, str), "Relationship must have from_id as str"
            assert hasattr(entity, 'to_id') and isinstance(entity.to_id, str), "Relationship must have to_id as str"
            assert hasattr(entity, 'relation_type') and isinstance(entity.relation_type, str), "Relationship must have relation_type as str"
            assert hasattr(entity, 'strength') and isinstance(entity.strength, float), "Relationship must have strength as float"
            assert hasattr(entity, 'bidirectional') and isinstance(entity.bidirectional, bool), "Relationship must have bidirectional as bool"
            assert hasattr(entity, 'properties') and isinstance(entity.properties, dict), "Relationship must have properties as dict"
        # Add more entity-type checks as needed
        # (See docs/entity_schemas.md for full schema)
    
    def set_access_control(self, access_control: MemoryAccessControl):
        """Set access control for a memory entity."""
        self._access_controls[access_control.entity_id] = access_control
    
    async def store(self, entity: MemoryEntity, user_id: str = "system", 
                  role: str = "admin") -> str:
        """
        Store an entity in the appropriate memory tier.
        
        Args:
            entity: The memory entity to store
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            str: ID of the stored entity
            
        Raises:
            PermissionError: If user lacks write access
        """
        # For new entities, no access check is needed
        is_new = not entity.id or entity.id not in self._access_controls
        
        if not is_new and not self._check_access(
            entity.id, user_id, role, MemoryAccess.WRITE
        ):
            raise PermissionError(f"User {user_id} with role {role} lacks write access to entity {entity.id}")
            
        # Validate entity before storing
        self._validate_entity(entity)  # Validate entity schema
        
        # Calculate checksum for integrity verification
        entity.updated_at = datetime.utcnow()
        prev_checksum = entity.checksum
        entity.checksum = self._calculate_checksum(entity)
        
        # Store in appropriate memory tier
        if entity.tier == MemoryTier.WORKING:
            entity_id = await self._working_memory.store(entity)
        elif entity.tier == MemoryTier.EPISODIC:
            entity_id = await self._episodic_memory.store(entity)
        elif entity.tier == MemoryTier.SEMANTIC:
            entity_id = await self._semantic_memory.store(entity)
        elif entity.tier == MemoryTier.GRAPH:
            entity_id = await self._knowledge_graph.store(entity)
        else:
            raise ValueError(f"Unknown memory tier: {entity.tier}")
            
        # Log audit event
        self._log_audit_event(
            entity_id=entity_id,
            action="store",
            user_id=user_id,
            details={"tier": entity.tier.name},
            prev_checksum=prev_checksum,
            new_checksum=entity.checksum
        )
        
        # Setup default access control if this is a new entity
        if is_new:
            access_control = MemoryAccessControl(
                entity_id=entity_id,
                roles={"admin": list(MemoryAccess)}  # Admin has all access by default
            )
            self.set_access_control(access_control)
            
        return entity_id
        
    async def retrieve(self, entity_id: str, tier: MemoryTier,
                     user_id: str = "system", role: str = "admin") -> Optional[MemoryEntity]:
        """
        Retrieve a memory entity by ID from the specified tier.
        
        Args:
            entity_id: ID of the entity to retrieve
            tier: Memory tier to search in
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            Optional[MemoryEntity]: The retrieved entity or None if not found
            
        Raises:
            PermissionError: If user lacks read access
        """
        if not self._check_access(entity_id, user_id, role, MemoryAccess.READ):
            raise PermissionError(f"User {user_id} with role {role} lacks read access to entity {entity_id}")
            
        # Retrieve from appropriate memory tier
        if tier == MemoryTier.WORKING:
            entity = await self._working_memory.retrieve(entity_id)
        elif tier == MemoryTier.EPISODIC:
            entity = await self._episodic_memory.retrieve(entity_id)
        elif tier == MemoryTier.SEMANTIC:
            entity = await self._semantic_memory.retrieve(entity_id)
        elif tier == MemoryTier.GRAPH:
            entity = await self._knowledge_graph.retrieve(entity_id)
        else:
            raise ValueError(f"Unknown memory tier: {tier}")
            
        if entity:
            # Verify integrity
            current_checksum = entity.checksum
            calculated_checksum = self._calculate_checksum(entity)
            
            if current_checksum != calculated_checksum:
                logger.warning(f"Checksum mismatch for entity {entity_id}! Possible tampering detected.")
                # In production, this would trigger security alerts
            
            # Log audit event
            self._log_audit_event(
                entity_id=entity_id,
                action="retrieve",
                user_id=user_id,
                details={"tier": tier.name}
            )
            
        return entity
    
    async def delete(self, entity_id: str, tier: MemoryTier,
                   user_id: str = "system", role: str = "admin") -> bool:
        """
        Delete a memory entity by ID from the specified tier.
        
        Args:
            entity_id: ID of the entity to delete
            tier: Memory tier to delete from
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            bool: True if deleted successfully, False otherwise
            
        Raises:
            PermissionError: If user lacks delete access
        """
        if not self._check_access(entity_id, user_id, role, MemoryAccess.DELETE):
            raise PermissionError(f"User {user_id} with role {role} lacks delete access to entity {entity_id}")
            
        # Get entity for audit trail before deletion
        entity = await self.retrieve(entity_id, tier, user_id, role)
        if not entity:
            return False
            
        # Delete from appropriate memory tier
        if tier == MemoryTier.WORKING:
            success = await self._working_memory.delete(entity_id)
        elif tier == MemoryTier.EPISODIC:
            success = await self._episodic_memory.delete(entity_id)
        elif tier == MemoryTier.SEMANTIC:
            success = await self._semantic_memory.delete(entity_id)
        elif tier == MemoryTier.GRAPH:
            success = await self._knowledge_graph.delete(entity_id)
        else:
            raise ValueError(f"Unknown memory tier: {tier}")
            
        if success:
            # Log audit event
            self._log_audit_event(
                entity_id=entity_id,
                action="delete",
                user_id=user_id,
                details={"tier": tier.name, "entity_type": type(entity).__name__}
            )
            
            # Remove access controls
            if entity_id in self._access_controls:
                del self._access_controls[entity_id]
                
        return success
    
    async def search(self, query: Dict[str, Any], tier: MemoryTier,
                    limit: int = 10, offset: int = 0,
                    user_id: str = "system", role: str = "admin") -> List[MemoryEntity]:
        """
        Search for memory entities matching the query in the specified tier.
        
        Args:
            query: Search criteria
            tier: Memory tier to search in
            limit: Maximum number of results
            offset: Pagination offset
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[MemoryEntity]: Matching entities
        """
        # Search appropriate memory tier
        if tier == MemoryTier.WORKING:
            results = await self._working_memory.search(query, limit, offset)
        elif tier == MemoryTier.EPISODIC:
            results = await self._episodic_memory.search(query, limit, offset)
        elif tier == MemoryTier.SEMANTIC:
            results = await self._semantic_memory.search(query, limit, offset)
        elif tier == MemoryTier.GRAPH:
            results = await self._knowledge_graph.search(query, limit, offset)
        else:
            raise ValueError(f"Unknown memory tier: {tier}")
            
        # Filter by access control
        filtered_results = []
        for entity in results:
            if self._check_access(entity.id, user_id, role, MemoryAccess.READ):
                filtered_results.append(entity)
                
        # Log audit event
        self._log_audit_event(
            entity_id="search",
            action="search",
            user_id=user_id,
            details={"tier": tier.name, "query": query, "result_count": len(filtered_results)}
        )
            
        return filtered_results
    
    async def semantic_search(self, text: str, limit: int = 10,
                            user_id: str = "system", role: str = "admin") -> List[KnowledgeEntity]:
        """
        Perform semantic search on knowledge entities.
        
        Args:
            text: Text to search for semantically similar content
            limit: Maximum number of results
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[KnowledgeEntity]: Semantically similar entities
        """
        results = await self._semantic_memory.semantic_search(text, limit)
        
        # Filter by access control
        filtered_results = []
        for entity in results:
            if self._check_access(entity.id, user_id, role, MemoryAccess.READ):
                filtered_results.append(entity)
                
        # Log audit event
        self._log_audit_event(
            entity_id="semantic_search",
            action="semantic_search",
            user_id=user_id,
            details={"query": text, "result_count": len(filtered_results)}
        )
            
        return filtered_results
    
    async def get_context_history(self, workflow_id: str, 
                                user_id: str = "system", 
                                role: str = "admin") -> List[ContextMemoryEntity]:
        """
        Get the history of context changes for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[ContextMemoryEntity]: Context history
        """
        # Search for context entities belonging to workflow
        query = {"workflow_id": workflow_id}
        context_entities = await self._working_memory.search(query)
        
        # Filter by access control
        filtered_results = []
        for entity in context_entities:
            if self._check_access(entity.id, user_id, role, MemoryAccess.READ):
                filtered_results.append(entity)
                
        # Sort by version number
        filtered_results.sort(key=lambda e: e.version)
        
        return filtered_results
    
    async def get_workflow_history(self, customer_id: Optional[str] = None,
                                 user_id: str = "system",
                                 role: str = "admin",
                                 limit: int = 10,
                                 offset: int = 0) -> List[WorkflowMemoryEntity]:
        """
        Get workflow execution history.
        
        Args:
            customer_id: Optional filter for specific customer
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[WorkflowMemoryEntity]: Workflow history
        """
        # Construct query
        query = {}
        if customer_id:
            query["customer_id"] = customer_id
            
        # Get workflow history
        workflows = await self._episodic_memory.search(query, limit, offset)
        
        # Filter by access control
        filtered_results = []
        for entity in workflows:
            if self._check_access(entity.id, user_id, role, MemoryAccess.READ):
                filtered_results.append(entity)
                
        return filtered_results
    
    async def get_entity_relationships(self, entity_id: str,
                                     user_id: str = "system",
                                     role: str = "admin") -> List[RelationshipEntity]:
        """
        Get relationships for a specific entity.
        
        Args:
            entity_id: ID of the entity
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[RelationshipEntity]: Relationships
        """
        if not self._check_access(entity_id, user_id, role, MemoryAccess.READ):
            raise PermissionError(f"User {user_id} with role {role} lacks read access to entity {entity_id}")
            
        # Get relationships
        return await self._knowledge_graph.get_entity_relationships(entity_id)
    
    async def get_audit_log(self, entity_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          action: Optional[str] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> List[AuditLogEntry]:
        """
        Get audit log entries matching the filters.
        
        Args:
            entity_id: Optional filter for specific entity
            user_id: Optional filter for specific user
            action: Optional filter for specific action
            start_time: Optional filter for start time
            end_time: Optional filter for end time
            
        Returns:
            List[AuditLogEntry]: Matching audit log entries
        """
        # In production, this would query a secure audit log database
        # Here we filter the in-memory audit log
        filtered_log = self._audit_log
        
        if entity_id:
            filtered_log = [entry for entry in filtered_log if entry.entity_id == entity_id]
            
        if user_id:
            filtered_log = [entry for entry in filtered_log if entry.user_id == user_id]
            
        if action:
            filtered_log = [entry for entry in filtered_log if entry.action == action]
            
        if start_time:
            filtered_log = [entry for entry in filtered_log if entry.timestamp >= start_time]
            
        if end_time:
            filtered_log = [entry for entry in filtered_log if entry.timestamp <= end_time]
            
        return filtered_log
