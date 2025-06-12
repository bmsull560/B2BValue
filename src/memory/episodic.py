"""
Episodic Memory for B2BValue Memory Architecture.

This module implements the Episodic Memory tier, which provides
persistent storage for completed workflow execution histories.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import os

from src.memory.types import MemoryEntity, WorkflowMemoryEntity, MemoryTier

logger = logging.getLogger(__name__)

class EpisodicMemory:
    """
    Episodic Memory implementation - stores complete workflow execution histories
    for audit, analysis, and learning purposes.
    
    This is a persistent store with indexing capabilities.
    """
    
    def __init__(self, storage_path="./data/episodic"):
        """
        Initialize episodic memory store.
        
        Args:
            storage_path: Path to store workflow histories
        """
        self._storage_path = storage_path
        self._ensure_storage_exists()
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
        logger.info("Episodic Memory initialized")
        
    def _ensure_storage_exists(self):
        """Ensure storage directory exists."""
        os.makedirs(self._storage_path, exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "workflows"), exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "indexes"), exist_ok=True)
        
    def _load_index(self):
        """Load workflow index from storage."""
        index_path = os.path.join(self._storage_path, "indexes", "workflow_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    self._index = json.load(f)
                logger.info(f"Loaded index with {len(self._index)} workflow entries")
            except Exception as e:
                logger.error(f"Failed to load workflow index: {e}")
                # Initialize empty index if loading fails
                self._index = {}
                
    def _save_index(self):
        """Save workflow index to storage."""
        index_path = os.path.join(self._storage_path, "indexes", "workflow_index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump(self._index, f)
        except Exception as e:
            logger.error(f"Failed to save workflow index: {e}")
    
    def _get_workflow_path(self, entity_id: str) -> str:
        """Get path to workflow file."""
        return os.path.join(self._storage_path, "workflows", f"{entity_id}.json")
        
    def _index_workflow(self, entity: WorkflowMemoryEntity):
        """Index a workflow for efficient searching."""
        index_entry = {
            "id": entity.id,
            "workflow_id": entity.workflow_id,
            "workflow_name": entity.workflow_name,
            "workflow_status": entity.workflow_status,
            "start_time": entity.start_time.isoformat(),
            "customer_id": entity.customer_id if entity.customer_id else None,
            "user_id": entity.user_id if entity.user_id else None
        }
        
        if entity.end_time:
            index_entry["end_time"] = entity.end_time.isoformat()
            
        self._index[entity.id] = index_entry
        self._save_index()
    
    async def store(self, entity: WorkflowMemoryEntity) -> str:
        """
        Store a workflow entity in episodic memory.
        
        Args:
            entity: The workflow entity to store
            
        Returns:
            str: ID of the stored entity
        """
        # Ensure entity is of correct type
        if not isinstance(entity, WorkflowMemoryEntity):
            raise TypeError("Episodic Memory can only store WorkflowMemoryEntity objects")
            
        # Ensure entity is assigned to episodic memory tier
        entity.tier = MemoryTier.EPISODIC
        
        # Update timestamp
        entity.updated_at = datetime.utcnow()
        
        # Store entity to file
        workflow_path = self._get_workflow_path(entity.id)
        try:
            with open(workflow_path, 'w') as f:
                json.dump(entity.to_dict(), f)
                
            # Update index for efficient searching
            self._index_workflow(entity)
            
            logger.info(f"Stored workflow {entity.workflow_id} in episodic memory")
            return entity.id
        except Exception as e:
            logger.error(f"Failed to store workflow in episodic memory: {e}")
            raise
    
    async def retrieve(self, entity_id: str) -> Optional[WorkflowMemoryEntity]:
        """
        Retrieve a workflow entity from episodic memory.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Optional[WorkflowMemoryEntity]: The retrieved entity or None if not found
        """
        workflow_path = self._get_workflow_path(entity_id)
        if not os.path.exists(workflow_path):
            return None
            
        try:
            with open(workflow_path, 'r') as f:
                workflow_dict = json.load(f)
                
            # Convert dict back to entity
            workflow = WorkflowMemoryEntity(
                id=workflow_dict.get('id'),
                created_at=datetime.fromisoformat(workflow_dict.get('created_at')),
                updated_at=datetime.fromisoformat(workflow_dict.get('updated_at')),
                creator_id=workflow_dict.get('creator_id'),
                workflow_id=workflow_dict.get('workflow_id'),
                workflow_name=workflow_dict.get('workflow_name'),
                workflow_status=workflow_dict.get('workflow_status'),
                start_time=datetime.fromisoformat(workflow_dict.get('start_time')),
                end_time=datetime.fromisoformat(workflow_dict.get('end_time')) if workflow_dict.get('end_time') else None,
                context_versions=workflow_dict.get('context_versions', []),
                stages=workflow_dict.get('stages', []),
                result=workflow_dict.get('result'),
                user_id=workflow_dict.get('user_id'),
                customer_id=workflow_dict.get('customer_id'),
                version=workflow_dict.get('version', 1),
                sensitivity=workflow_dict.get('sensitivity'),
                tier=MemoryTier.EPISODIC
            )
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to retrieve workflow from episodic memory: {e}")
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a workflow entity from episodic memory.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        workflow_path = self._get_workflow_path(entity_id)
        if not os.path.exists(workflow_path):
            return False
            
        try:
            # Remove file
            os.remove(workflow_path)
            
            # Remove from index
            if entity_id in self._index:
                del self._index[entity_id]
                self._save_index()
                
            return True
        except Exception as e:
            logger.error(f"Failed to delete workflow from episodic memory: {e}")
            return False
    
    async def search(self, query: Dict[str, Any], limit: int = 10, offset: int = 0) -> List[WorkflowMemoryEntity]:
        """
        Search for workflow entities in episodic memory.
        
        Args:
            query: Search criteria as key-value pairs
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List[WorkflowMemoryEntity]: Matching entities
        """
        # First filter by index for efficiency
        matching_ids = []
        for entity_id, index_entry in self._index.items():
            match = True
            for key, value in query.items():
                if key not in index_entry or index_entry[key] != value:
                    match = False
                    break
                    
            if match:
                matching_ids.append(entity_id)
                
        # Apply pagination
        paginated_ids = matching_ids[offset:offset+limit]
        
        # Retrieve full entities
        results = []
        for entity_id in paginated_ids:
            entity = await self.retrieve(entity_id)
            if entity:
                results.append(entity)
                
        return results
