"""
Semantic Memory for B2BValue Memory Architecture.

This module implements the Semantic Memory tier, which provides
long-term knowledge storage with vector embeddings and semantic search.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import os
import numpy as np
from datetime import datetime

from src.memory.types import MemoryEntity, KnowledgeEntity, MemoryTier, DataSensitivity

logger = logging.getLogger(__name__)

class SemanticMemory:
    """
    Semantic Memory implementation - stores knowledge entities with
    vector embeddings for semantic search and retrieval.
    
    This is a persistent store optimized for semantic similarity search.
    """
    
    def __init__(self, storage_path="./data/semantic", embedding_dim=384):
        """
        Initialize semantic memory store.
        
        Args:
            storage_path: Path to store knowledge entities
            embedding_dim: Dimension of vector embeddings
        """
        self._storage_path = storage_path
        self._embedding_dim = embedding_dim
        self._ensure_storage_exists()
        self._entity_index: Dict[str, Dict[str, Any]] = {}
        self._embedding_index = None
        self._load_indexes()
        logger.info("Semantic Memory initialized")
        
    def _ensure_storage_exists(self):
        """Ensure storage directory exists."""
        os.makedirs(self._storage_path, exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "entities"), exist_ok=True)
        os.makedirs(os.path.join(self._storage_path, "indexes"), exist_ok=True)
        
    def _load_indexes(self):
        """Load knowledge indexes from storage."""
        # Load entity index
        entity_index_path = os.path.join(self._storage_path, "indexes", "entity_index.json")
        if os.path.exists(entity_index_path):
            try:
                with open(entity_index_path, 'r') as f:
                    self._entity_index = json.load(f)
                logger.info(f"Loaded index with {len(self._entity_index)} knowledge entities")
            except Exception as e:
                logger.error(f"Failed to load knowledge entity index: {e}")
                self._entity_index = {}
                
        # Load embeddings index if available
        embeddings_path = os.path.join(self._storage_path, "indexes", "embeddings.npy")
        embeddings_id_path = os.path.join(self._storage_path, "indexes", "embedding_ids.json")
        if os.path.exists(embeddings_path) and os.path.exists(embeddings_id_path):
            try:
                # Load embeddings matrix
                embeddings = np.load(embeddings_path)
                
                # Load mapping of embeddings to entity IDs
                with open(embeddings_id_path, 'r') as f:
                    embedding_ids = json.load(f)
                    
                self._embedding_index = {
                    'embeddings': embeddings,
                    'ids': embedding_ids
                }
                logger.info(f"Loaded embedding index with {len(embedding_ids)} vectors")
            except Exception as e:
                logger.error(f"Failed to load embeddings index: {e}")
                self._embedding_index = None
                
    def _save_entity_index(self):
        """Save entity index to storage."""
        entity_index_path = os.path.join(self._storage_path, "indexes", "entity_index.json")
        try:
            with open(entity_index_path, 'w') as f:
                json.dump(self._entity_index, f)
        except Exception as e:
            logger.error(f"Failed to save entity index: {e}")
            
    def _save_embedding_index(self):
        """Save embedding index to storage."""
        if not self._embedding_index:
            return
            
        embeddings_path = os.path.join(self._storage_path, "indexes", "embeddings.npy")
        embeddings_id_path = os.path.join(self._storage_path, "indexes", "embedding_ids.json")
        
        try:
            # Save embeddings matrix
            np.save(embeddings_path, self._embedding_index['embeddings'])
            
            # Save mapping of embeddings to entity IDs
            with open(embeddings_id_path, 'w') as f:
                json.dump(self._embedding_index['ids'], f)
        except Exception as e:
            logger.error(f"Failed to save embeddings index: {e}")
            
    def _get_entity_path(self, entity_id: str) -> str:
        """Get path to knowledge entity file."""
        return os.path.join(self._storage_path, "entities", f"{entity_id}.json")
        
    def _index_entity(self, entity: KnowledgeEntity):
        """Index a knowledge entity for efficient searching."""
        # Basic metadata index
        index_entry = {
            "id": entity.id,
            "content_type": entity.content_type,
            "source": entity.source,
            "confidence": entity.confidence,
            "tags": entity.tags,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
            "has_embedding": entity.vector_embedding is not None
        }
        
        self._entity_index[entity.id] = index_entry
        self._save_entity_index()
        
        # Update embedding index if entity has embeddings
        if entity.vector_embedding:
            self._update_embedding_index(entity)
            
    def _update_embedding_index(self, entity: KnowledgeEntity):
        """Update the embedding index with a new entity vector."""
        if not entity.vector_embedding:
            return
            
        # Ensure embedding is the correct dimension
        if len(entity.vector_embedding) != self._embedding_dim:
            logger.warning(f"Embedding dimension mismatch: expected {self._embedding_dim}, got {len(entity.vector_embedding)}")
            return
            
        # Initialize embedding index if not exists
        if not self._embedding_index:
            self._embedding_index = {
                'embeddings': np.array([entity.vector_embedding], dtype=np.float32),
                'ids': [entity.id]
            }
        else:
            # Check if entity already exists in index
            if entity.id in self._embedding_index['ids']:
                # Update existing embedding
                idx = self._embedding_index['ids'].index(entity.id)
                self._embedding_index['embeddings'][idx] = entity.vector_embedding
            else:
                # Append new embedding
                new_embedding = np.array([entity.vector_embedding], dtype=np.float32)
                self._embedding_index['embeddings'] = np.vstack([self._embedding_index['embeddings'], new_embedding])
                self._embedding_index['ids'].append(entity.id)
                
        # Save updated index
        self._save_embedding_index()
        
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text using a language model.

        Attempts to use sentence-transformers if available, otherwise falls back to random vectors.
        
        Args:
            text: Text to embed
        Returns:
            List[float]: Vector embedding
        """
        try:
            try:
                from sentence_transformers import SentenceTransformer
                # Cache model as class attribute for efficiency
                if not hasattr(self, '_st_model'):
                    self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
                embedding = self._st_model.encode([text])[0]
                # Ensure correct dimension
                if hasattr(embedding, 'shape') and embedding.shape[0] != self._embedding_dim:
                    logger.warning(f"Embedding dimension mismatch: got {embedding.shape[0]}, expected {self._embedding_dim}")
                    # Pad or truncate as needed
                    if embedding.shape[0] > self._embedding_dim:
                        embedding = embedding[:self._embedding_dim]
                    else:
                        import numpy as np
                        embedding = np.pad(embedding, (0, self._embedding_dim - embedding.shape[0]), 'constant')
                embedding = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                logger.info(f"Generated real embedding for text of length {len(text)}")
                return embedding
            except ImportError:
                logger.warning("sentence-transformers not installed; falling back to random embeddings. To enable real semantic search, install sentence-transformers.")
            except Exception as e:
                logger.error(f"Failed to generate real embedding: {e}; falling back to random embedding.")

            # Fallback: random normalized vector
            import numpy as np
            random_vector = np.random.rand(self._embedding_dim)
            embedding = (random_vector / np.linalg.norm(random_vector)).tolist()
            logger.info(f"Generated random embedding for text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * self._embedding_dim  # Return zero vector on failure
    
    async def store(self, entity: KnowledgeEntity) -> str:
        """
        Store a knowledge entity in semantic memory.
        
        Args:
            entity: The knowledge entity to store
            
        Returns:
            str: ID of the stored entity
        """
        # Ensure entity is of correct type
        if not isinstance(entity, KnowledgeEntity):
            raise TypeError("Semantic Memory can only store KnowledgeEntity objects")
            
        # Ensure entity is assigned to semantic memory tier
        entity.tier = MemoryTier.SEMANTIC
        
        # Update timestamp
        entity.updated_at = datetime.utcnow()
        
        # Generate embedding if content exists but embedding doesn't
        if entity.content and not entity.vector_embedding:
            entity.vector_embedding = self._generate_embedding(entity.content)
            
        # Store entity to file
        entity_path = self._get_entity_path(entity.id)
        try:
            with open(entity_path, 'w') as f:
                json.dump(entity.to_dict(), f)
                
            # Update indexes
            self._index_entity(entity)
            
            logger.info(f"Stored knowledge entity {entity.id} in semantic memory")
            return entity.id
        except Exception as e:
            logger.error(f"Failed to store knowledge entity in semantic memory: {e}")
            raise
    
    async def retrieve(self, entity_id: str) -> Optional[KnowledgeEntity]:
        """
        Retrieve a knowledge entity from semantic memory.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Optional[KnowledgeEntity]: The retrieved entity or None if not found
        """
        entity_path = self._get_entity_path(entity_id)
        if not os.path.exists(entity_path):
            return None
            
        try:
            with open(entity_path, 'r') as f:
                entity_dict = json.load(f)
                
            # Convert dict back to entity
            entity = KnowledgeEntity(
                id=entity_dict.get('id'),
                created_at=datetime.fromisoformat(entity_dict.get('created_at')),
                updated_at=datetime.fromisoformat(entity_dict.get('updated_at')),
                creator_id=entity_dict.get('creator_id'),
                sensitivity=DataSensitivity[entity_dict.get('sensitivity')] if 'sensitivity' in entity_dict else DataSensitivity.INTERNAL,
                content=entity_dict.get('content'),
                content_type=entity_dict.get('content_type'),
                source=entity_dict.get('source'),
                confidence=entity_dict.get('confidence', 1.0),
                references=entity_dict.get('references', []),
                vector_embedding=entity_dict.get('vector_embedding'),
                version=entity_dict.get('version', 1),
                tier=MemoryTier.SEMANTIC,
                tags=entity_dict.get('tags', [])
            )
            return entity
            
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge entity from semantic memory: {e}")
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """
        Delete a knowledge entity from semantic memory.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        entity_path = self._get_entity_path(entity_id)
        if not os.path.exists(entity_path):
            return False
            
        try:
            # Remove file
            os.remove(entity_path)
            
            # Remove from entity index
            if entity_id in self._entity_index:
                del self._entity_index[entity_id]
                self._save_entity_index()
                
            # Remove from embedding index
            if self._embedding_index and entity_id in self._embedding_index['ids']:
                idx = self._embedding_index['ids'].index(entity_id)
                self._embedding_index['embeddings'] = np.delete(self._embedding_index['embeddings'], idx, axis=0)
                self._embedding_index['ids'].pop(idx)
                self._save_embedding_index()
                
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge entity from semantic memory: {e}")
            return False
    
    async def search(self, query: Dict[str, Any], limit: int = 10, offset: int = 0) -> List[KnowledgeEntity]:
        """
        Search for knowledge entities in semantic memory by metadata.
        
        Args:
            query: Search criteria as key-value pairs
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List[KnowledgeEntity]: Matching entities
        """
        # First filter by index for efficiency
        matching_ids = []
        for entity_id, index_entry in self._entity_index.items():
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
    
    async def semantic_search(self, text: str, limit: int = 10) -> List[KnowledgeEntity]:
        """
        Perform semantic (similarity) search for knowledge entities.
        
        Args:
            text: Text to search for semantically similar content
            limit: Maximum number of results
            
        Returns:
            List[KnowledgeEntity]: Semantically similar entities
        """
        if not self._embedding_index or len(self._embedding_index['ids']) == 0:
            logger.warning("No embeddings available for semantic search")
            return []
            
        try:
            # Generate embedding for search text
            query_embedding = self._generate_embedding(text)
            
            # Convert to numpy array for efficient computation
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # Compute cosine similarity with all embeddings
            # Cosine similarity = dot product of normalized vectors
            similarities = np.dot(self._embedding_index['embeddings'], query_vector)
            
            # Get top k results
            top_k_indices = np.argsort(-similarities)[:limit]
            top_k_ids = [self._embedding_index['ids'][idx] for idx in top_k_indices]
            
            # Retrieve entities
            results = []
            for entity_id in top_k_ids:
                entity = await self.retrieve(entity_id)
                if entity:
                    results.append(entity)
                    
            return results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
