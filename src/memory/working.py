"""
Working Memory for B2BValue Memory Architecture.

This module implements the Working Memory tier, which provides ephemeral
context storage during workflow execution. It uses an in-memory store with
optional persistence for recovery purposes.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import time
from datetime import datetime

from src.memory.types import MemoryEntity, ContextMemoryEntity, MemoryTier

logger = logging.getLogger(__name__)

class WorkingMemory:
    """
    Working Memory implementation - the most ephemeral tier that stores
    active context for running workflows.
    
    This is primarily an in-memory store with optional persistence for recovery.
    """
    
    def __init__(self, persistence_path=None):
        """
        Initialize working memory store.
        
        Args:
            persistence_path: Optional path to persist memory for recovery
        """
        self._store: Dict[str, ContextMemoryEntity] = {}
        self._persistence_path = persistence_path
        logger.info("Working Memory initialized")
        
        # Recovery from persistence if path provided
        if self._persistence_path:
            try:
                self._recover_from_persistence()
            except Exception as e:
                logger.error(f"Failed to recover working memory: {e}")
        
    def _recover_from_persistence(self):
        """Recover working memory from persistence file."""
        try:
            import os
            if os.path.exists(self._persistence_path):
                with open(self._persistence_path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        entity_dict = item
                        entity = ContextMemoryEntity(
                            id=entity_dict.get('id'),
                            created_at=datetime.fromisoformat(entity_dict.get('created_at')),
                            updated_at=datetime.fromisoformat(entity_dict.get('updated_at')),
                            creator_id=entity_dict.get('creator_id'),
                            context_data=entity_dict.get('context_data', {}),
                            workflow_id=entity_dict.get('workflow_id'),
                            stage_id=entity_dict.get('stage_id'),
                            agent_id=entity_dict.get('agent_id'),
                            version=entity_dict.get('version', 1)
                        )
                        self._store[entity.id] = entity
                logger.info(f"Recovered {len(self._store)} items from working memory persistence")
        except Exception as e:
            logger.error(f"Error recovering working memory: {e}")
            raise
            
    def _persist(self):
        """Persist working memory to file if configured."""
        if not self._persistence_path:
            return
            
        try:
            entities_json = [entity.to_dict() for entity in self._store.values()]
            with open(self._persistence_path, 'w') as f:
                json.dump(entities_json, f)
        except Exception as e:
            logger.error(f"Failed to persist working memory: {e}")
    
    def _clean_expired(self):
        """Remove expired entries based on TTL."""
        current_time = time.time()
        expired_ids = []
        
        for entity_id, entity in self._store.items():
            if entity.ttl and entity.created_at.timestamp() + entity.ttl < current_time:
                expired_ids.append(entity_id)
                
        for entity_id in expired_ids:
            del self._store[entity_id]
            
        if expired_ids:
            logger.info(f"Removed {len(expired_ids)} expired entries from working memory")
    
    async def store(self, entity: ContextMemoryEntity) -> str:
        """
        Store a context entity in working memory.
        
        Args:
            entity: The context entity to store
            
        Returns:
            str: ID of the stored entity
        """
        # Ensure entity is of correct type
        if not isinstance(entity, ContextMemoryEntity):
            raise TypeError("Working Memory can only store ContextMemoryEntity objects")
            
        # Ensure entity is assigned to working memory tier
        entity.tier = MemoryTier.WORKING
        
        # For existing entities, increment version
        if entity.id in self._store:
            entity.version = self._store[entity.id].version + 1
            
        # Update timestamp
        entity.updated_at = datetime.utcnow()
        
        # Store entity
        self._store[entity.id] = entity
        
        # Clean expired entries periodically
        self._clean_expired()
        
        # Persist if configured
        self._persist()
        
        return entity.id
    
    async def retrieve(self, entity_id: str) -> Optional[ContextMemoryEntity]:
        """
        Retrieve a context entity from working memory.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Optional[ContextMemoryEntity]: The retrieved entity or None if not found
        """
        self._clean_expired()  # Clean expired entries first
        return self._store.get(entity_id)
    
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a context entity from working memory.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        if entity_id not in self._store:
            return False
            
        del self._store[entity_id]
        self._persist()
        return True
    
    async def search(self, query: Dict[str, Any], limit: int = 10, offset: int = 0) -> List[ContextMemoryEntity]:
        """
        Search for context entities in working memory.
        
        Args:
            query: Search criteria as key-value pairs
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List[ContextMemoryEntity]: Matching entities
        """
        self._clean_expired()  # Clean expired entries first
        
        results = []
        for entity in self._store.values():
            match = True
            for key, value in query.items():
                # Handle nested keys with dot notation (e.g., "context_data.customer_id")
                if "." in key:
                    parts = key.split(".")
                    obj = entity
                    for part in parts[:-1]:
                        if hasattr(obj, part) and isinstance(getattr(obj, part), dict):
                            obj = getattr(obj, part)
                        else:
                            match = False
                            break
                    if match and (parts[-1] not in obj or obj[parts[-1]] != value):
                        match = False
                # Handle direct attributes
                elif not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    
            if match:
                results.append(entity)
                
        # Apply pagination
        return results[offset:offset+limit]
