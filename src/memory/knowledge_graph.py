"""
Knowledge Graph for B2BValue Memory Architecture.

This module implements the Knowledge Graph tier, which manages
relationship entities between other memory entities to create
a connected network of knowledge.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
import json
import os
from datetime import datetime

from src.memory.types import MemoryEntity, RelationshipEntity, MemoryTier, DataSensitivity
from src.memory.storage_backend import StorageBackend

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Knowledge Graph implementation - manages relationships between
    entities to create a connected graph of knowledge.

    Supports pluggable storage backends. If a StorageBackend is provided, all CRUD/search
    operations are delegated to it (e.g., SQLite). Otherwise, file-based storage is used.
    """
    
    def __init__(self, storage_path="./data/graph", backend: StorageBackend = None):
        """
        Initialize knowledge graph store.
        
        Args:
            storage_path: Path to store relationship entities
            backend: Optional StorageBackend instance (e.g., SQLiteStorageBackend)
        """
        self._backend = backend
        self._storage_path = storage_path
        if not self._backend:
            self._ensure_storage_exists()
            self._index: Dict[str, Dict[str, Any]] = {}  # Relationship metadata
            self._adjacency: Dict[str, Dict[str, Set[str]]] = {}  # Node adjacency list
            self._load_indexes()
        logger.info(f"Knowledge Graph initialized (backend={'sqlite' if backend else 'file'})")
        
    def _ensure_storage_exists(self):
        """Ensure storage directory exists."""
        os.makedirs(self._storage_path, exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "relationships"), exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "indexes"), exist_ok=True)
        
    def _load_indexes(self):
        """Load knowledge graph indexes from storage."""
        # Load relationship index
        index_path = os.path.join(self._storage_path, "indexes", "relationship_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    self._index = json.load(f)
                logger.info(f"Loaded index with {len(self._index)} relationships")
            except Exception as e:
                logger.error(f"Failed to load relationship index: {e}")
                self._index = {}
                
        # Load adjacency list
        adjacency_path = os.path.join(self._storage_path, "indexes", "adjacency_list.json")
        if os.path.exists(adjacency_path):
            try:
                with open(adjacency_path, 'r') as f:
                    # Convert JSON serialized adjacency to proper structure with sets
                    raw_adjacency = json.load(f)
                    self._adjacency = {
                        node_id: {
                            rel_type: set(neighbors) 
                            for rel_type, neighbors in relations.items()
                        }
                        for node_id, relations in raw_adjacency.items()
                    }
                logger.info(f"Loaded adjacency list with {len(self._adjacency)} nodes")
            except Exception as e:
                logger.error(f"Failed to load adjacency list: {e}")
                self._adjacency = {}
                
    def _save_index(self):
        """Save relationship index to storage."""
        index_path = os.path.join(self._storage_path, "indexes", "relationship_index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump(self._index, f)
        except Exception as e:
            logger.error(f"Failed to save relationship index: {e}")
            
    def _save_adjacency(self):
        """Save adjacency list to storage."""
        adjacency_path = os.path.join(self._storage_path, "indexes", "adjacency_list.json")
        try:
            # Convert sets to lists for JSON serialization
            serializable_adjacency = {
                node_id: {
                    rel_type: list(neighbors)
                    for rel_type, neighbors in relations.items()
                }
                for node_id, relations in self._adjacency.items()
            }
            with open(adjacency_path, 'w') as f:
                json.dump(serializable_adjacency, f)
        except Exception as e:
            logger.error(f"Failed to save adjacency list: {e}")
            
    def _get_relationship_path(self, entity_id: str) -> str:
        """Get path to relationship entity file."""
        return os.path.join(self._storage_path, "relationships", f"{entity_id}.json")
        
    def _index_relationship(self, entity: RelationshipEntity):
        """Index a relationship entity for efficient searching and traversal."""
        # Update metadata index
        index_entry = {
            "id": entity.id,
            "from_id": entity.from_id,
            "to_id": entity.to_id,
            "relation_type": entity.relation_type,
            "strength": entity.strength,
            "bidirectional": entity.bidirectional,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat()
        }
        self._index[entity.id] = index_entry
        
        # Update adjacency list for graph traversal
        # Ensure from_node exists in adjacency
        if entity.from_id not in self._adjacency:
            self._adjacency[entity.from_id] = {}
            
        # Ensure relation_type exists for from_node
        if entity.relation_type not in self._adjacency[entity.from_id]:
            self._adjacency[entity.from_id][entity.relation_type] = set()
            
        # Add edge
        self._adjacency[entity.from_id][entity.relation_type].add(entity.to_id)
        
        # If bidirectional, add reverse edge
        if entity.bidirectional:
            # Ensure to_node exists in adjacency
            if entity.to_id not in self._adjacency:
                self._adjacency[entity.to_id] = {}
                
            # Ensure relation_type exists for to_node
            if entity.relation_type not in self._adjacency[entity.to_id]:
                self._adjacency[entity.to_id][entity.relation_type] = set()
                
            # Add reverse edge
            self._adjacency[entity.to_id][entity.relation_type].add(entity.from_id)
    
    async def store(self, entity: RelationshipEntity) -> str:
        """
        Store a relationship entity in the knowledge graph. If a backend is present, delegate.
        """
        if self._backend is not None:
            return await self._backend.store(entity)
        if not isinstance(entity, RelationshipEntity):
            raise TypeError("Knowledge Graph can only store RelationshipEntity objects")
        entity.tier = MemoryTier.GRAPH
        entity.updated_at = datetime.utcnow()
        rel_path = self._get_relationship_path(entity.id)
        try:
            with open(rel_path, 'w') as f:
                json.dump(entity.to_dict(), f)
            self._index_relationship(entity)
            self._save_index()
            self._save_adjacency()
            logger.info(f"Stored relationship {entity.id} in knowledge graph")
            return entity.id
        except Exception as e:
            logger.error(f"Failed to store relationship in knowledge graph: {e}")
            raise
    
    async def retrieve(self, entity_id: str) -> Optional[RelationshipEntity]:
        """
        Retrieve a relationship entity from the knowledge graph. If a backend is present, delegate.
        """
        if self._backend is not None:
            return await self._backend.retrieve(entity_id)
        rel_path = self._get_relationship_path(entity_id)
        if not os.path.exists(rel_path):
            return None
        try:
            with open(rel_path, 'r') as f:
                rel_dict = json.load(f)
            entity = RelationshipEntity(
                id=rel_dict.get('id'),
                from_id=rel_dict.get('from_id'),
                to_id=rel_dict.get('to_id'),
                relation_type=rel_dict.get('relation_type'),
                strength=rel_dict.get('strength', 1.0),
                bidirectional=rel_dict.get('bidirectional', False),
                created_at=datetime.fromisoformat(rel_dict.get('created_at')),
                updated_at=datetime.fromisoformat(rel_dict.get('updated_at')),
                tier=MemoryTier.GRAPH,
                sensitivity=rel_dict.get('sensitivity')
            )
            return entity
        except Exception as e:
            logger.error(f"Failed to retrieve relationship from knowledge graph: {e}")
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a relationship entity from the knowledge graph. If a backend is present, delegate.
        """
        if self._backend is not None:
            return await self._backend.delete(entity_id)
        rel_path = self._get_relationship_path(entity_id)
        if not os.path.exists(rel_path):
            return False
        try:
            os.remove(rel_path)
            if entity_id in self._index:
                del self._index[entity_id]
                self._save_index()
            # Also update adjacency (not shown for brevity)
            logger.info(f"Deleted relationship {entity_id} from knowledge graph")
            return True
        except Exception as e:
            logger.error(f"Failed to delete relationship from knowledge graph: {e}")
            return False
    
    async def search(self, query: Dict[str, Any], limit: int = 10) -> List[RelationshipEntity]:
        """
        Search for relationship entities in the knowledge graph. If a backend is present, delegate.
        """
        if self._backend is not None:
            return await self._backend.search(query, limit=limit)
        # File-based fallback:
        matching_ids = []
        for entity_id, index_entry in self._index.items():
            match = True
            for key, value in query.items():
                if key not in index_entry or index_entry[key] != value:
                    match = False
                    break
            if match:
                matching_ids.append(entity_id)
        paginated_ids = matching_ids[:limit]
        results = []
        for entity_id in paginated_ids:
            entity = await self.retrieve(entity_id)
            if entity:
                results.append(entity)
        return results
    
    async def find_neighbors(self, node_id: str, relation_type: Optional[str] = None) -> List[str]:
        """
        Find all nodes connected to the given node.
        
        Args:
            node_id: ID of the node to find neighbors for
            relation_type: Optional filter for specific relation type
            
        Returns:
            List[str]: IDs of neighboring nodes
        """
        if node_id not in self._adjacency:
            return []
            
        if relation_type:
            # Return neighbors with specific relation type
            if relation_type in self._adjacency[node_id]:
                return list(self._adjacency[node_id][relation_type])
            else:
                return []
        else:
            # Return all neighbors regardless of relation type
            all_neighbors = set()
            for neighbors in self._adjacency[node_id].values():
                all_neighbors.update(neighbors)
            return list(all_neighbors)
            
    async def find_relationships(self, from_id: str, to_id: str) -> List[RelationshipEntity]:
        """
        Find all relationships between two nodes.
        
        Args:
            from_id: ID of the source node
            to_id: ID of the target node
            
        Returns:
            List[RelationshipEntity]: Relationships between the nodes
        """
        # Find relationship IDs where from_id and to_id match
        matching_ids = []
        for entity_id, index_entry in self._index.items():
            if (index_entry['from_id'] == from_id and index_entry['to_id'] == to_id) or \
               (index_entry['bidirectional'] and index_entry['from_id'] == to_id and index_entry['to_id'] == from_id):
                matching_ids.append(entity_id)
                
        # Retrieve full entities
        results = []
        for entity_id in matching_ids:
            entity = await self.retrieve(entity_id)
            if entity:
                results.append(entity)
                
        return results
        
    async def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> List[List[Tuple[str, str, str]]]:
        """
        Find paths between two nodes in the graph.
        
        Args:
            start_id: ID of the start node
            end_id: ID of the end node
            max_depth: Maximum path length to search
            
        Returns:
            List[List[Tuple[str, str, str]]]: List of paths, where each path is a list of
                                             (node_id, relation_type, next_node_id) tuples
        """
        # Breadth-first search for paths
        visited = set()
        queue = [[(start_id, "", start_id)]]  # Initial path with dummy first step
        valid_paths = []
        
        while queue and len(queue[0]) <= max_depth + 1:  # +1 for the initial dummy step
            path = queue.pop(0)
            node = path[-1][2]  # Last node in path
            
            if node == end_id and len(path) > 1:  # Found a path, ignore the initial dummy step
                valid_paths.append(path[1:])  # Remove the initial dummy step
                continue
                
            if node in visited:
                continue
                
            visited.add(node)
            
            # Get all outgoing edges
            if node in self._adjacency:
                for relation_type, neighbors in self._adjacency[node].items():
                    for neighbor in neighbors:
                        if neighbor not in [p[2] for p in path]:  # Avoid cycles
                            new_path = path + [(node, relation_type, neighbor)]
                            queue.append(new_path)
                            
        return valid_paths
