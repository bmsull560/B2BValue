"""
Model Context Protocol (MCP) Client for B2BValue Architecture.

This module implements the MCP client that agents use to interact with the
memory system according to the Global Rules for data integrity.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
import uuid
from datetime import datetime

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

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Model Context Protocol client that enforces data integrity rules
    and provides a unified interface for agents to interact with the
    memory system.
    
    This implementation adheres to the Global Rules:
    - Rule 1.1: Canonical Data Source - All agents read inputs from MCP
    - Rule 1.2: Output to MCP - All agent outputs written to MCP
    - Rule 1.3: Data Validation - Inputs validated against defined rules
    """
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize the MCP client.
        
        Args:
            memory_manager: Optional memory manager instance
        """
        self._memory_manager = memory_manager or MemoryManager()
        if not hasattr(self._memory_manager, '_working_memory'):
            # Initialize memory manager if not already initialized
            self._memory_manager.initialize()
            
        self._current_workflow_id: Optional[str] = None
        self._current_context_id: Optional[str] = None
        self._validation_rules: Dict[str, Dict[str, Any]] = {}
        
    def set_workflow_id(self, workflow_id: str) -> None:
        """Set the current workflow ID for context tracking."""
        self._current_workflow_id = workflow_id
        
    def get_workflow_id(self) -> Optional[str]:
        """Get the current workflow ID."""
        return self._current_workflow_id
        
    def set_validation_rules(self, rules: Dict[str, Dict[str, Any]]) -> None:
        """
        Set validation rules for data fields.
        
        Args:
            rules: Dictionary mapping field paths to validation rules
                  e.g. {"customer.revenue": {"type": "number", "min": 0}}
        """
        self._validation_rules = rules
        
    def _validate_data(self, data: Dict[str, Any], path_prefix: str = "") -> List[str]:
        """
        Validate data against defined validation rules.
        
        Args:
            data: Data to validate
            path_prefix: Current path prefix for nested fields
            
        Returns:
            List[str]: List of validation error messages, empty if valid
        """
        errors = []
        
        # Check each field in data
        for key, value in data.items():
            current_path = f"{path_prefix}.{key}" if path_prefix else key
            
            # If nested dict, recurse
            if isinstance(value, dict):
                nested_errors = self._validate_data(value, current_path)
                errors.extend(nested_errors)
                continue
                
            # Check if we have validation rules for this field
            if current_path in self._validation_rules:
                rule = self._validation_rules[current_path]
                
                # Type validation
                if "type" in rule:
                    expected_type = rule["type"]
                    if expected_type == "string" and not isinstance(value, str):
                        errors.append(f"Field {current_path} must be a string")
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        errors.append(f"Field {current_path} must be a number")
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        errors.append(f"Field {current_path} must be a boolean")
                    elif expected_type == "array" and not isinstance(value, list):
                        errors.append(f"Field {current_path} must be an array")
                        
                # Range validation for numbers
                if isinstance(value, (int, float)):
                    if "min" in rule and value < rule["min"]:
                        errors.append(f"Field {current_path} must be at least {rule['min']}")
                    if "max" in rule and value > rule["max"]:
                        errors.append(f"Field {current_path} must be at most {rule['max']}")
                        
                # Length validation for strings and arrays
                if isinstance(value, (str, list)):
                    if "minLength" in rule and len(value) < rule["minLength"]:
                        errors.append(f"Field {current_path} must have at least {rule['minLength']} items")
                    if "maxLength" in rule and len(value) > rule["maxLength"]:
                        errors.append(f"Field {current_path} must have at most {rule['maxLength']} items")
                        
                # Enum validation
                if "enum" in rule and value not in rule["enum"]:
                    errors.append(f"Field {current_path} must be one of: {', '.join(map(str, rule['enum']))}")
                    
                # Required fields
                if "required" in rule and rule["required"] and value is None:
                    errors.append(f"Field {current_path} is required")
                    
        return errors
    
    async def get_context(self, user_id: str = "system", role: str = "agent") -> Dict[str, Any]:
        """
        Get the current workflow context from working memory.
        
        Args:
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            Dict[str, Any]: Current workflow context
        """
        if not self._current_workflow_id:
            logger.warning("No workflow ID set, returning empty context")
            return {}
            
        # If we have a current context ID, retrieve it directly
        if self._current_context_id:
            entity = await self._memory_manager.retrieve(
                self._current_context_id, 
                MemoryTier.WORKING,
                user_id,
                role
            )
            if entity and isinstance(entity, ContextMemoryEntity):
                return entity.context_data
                
        # Otherwise, find the latest context for this workflow
        query = {"workflow_id": self._current_workflow_id}
        contexts = await self._memory_manager.search(
            query,
            MemoryTier.WORKING,
            limit=1,
            user_id=user_id,
            role=role
        )
        
        if contexts and isinstance(contexts[0], ContextMemoryEntity):
            self._current_context_id = contexts[0].id
            return contexts[0].context_data
            
        # No context found, create a new one
        new_context = ContextMemoryEntity(
            workflow_id=self._current_workflow_id,
            context_data={},
            version=1
        )
        self._current_context_id = await self._memory_manager.store(new_context, user_id, role)
        return {}
    
    async def update_context(self, agent_id: str, data: Dict[str, Any], 
                           user_id: str = "system", role: str = "agent") -> None:
        """
        Update the workflow context with agent outputs.
        
        Args:
            agent_id: ID of the agent providing the data
            data: Data to add to context
            user_id: ID of user performing the operation
            role: Role of the user
        """
        if not self._current_workflow_id:
            logger.error("Cannot update context: No workflow ID set")
            return
            
        # Validate data against rules
        errors = self._validate_data(data)
        if errors:
            logger.warning(f"Data validation errors from agent {agent_id}: {errors}")
            # In production, you might want to raise an exception here
            # For now, we'll log and continue
            
        # Get current context
        current_context = await self.get_context(user_id, role)
        
        # Create new context entity with updated data
        new_context = ContextMemoryEntity(
            workflow_id=self._current_workflow_id,
            context_data={**current_context, **data},
            parent_id=self._current_context_id,
            agent_id=agent_id,
            version=(current_context.get("version", 0) + 1) if current_context else 1
        )
        
        # Store updated context
        self._current_context_id = await self._memory_manager.store(new_context, user_id, role)
        logger.info(f"Context updated by agent {agent_id}, new context ID: {self._current_context_id}")
        
    async def start_workflow(self, workflow_name: str, user_id: Optional[str] = None,
                           customer_id: Optional[str] = None) -> str:
        """
        Start a new workflow and create initial records in memory.
        
        Args:
            workflow_name: Name of the workflow
            user_id: Optional user ID associated with the workflow
            customer_id: Optional customer ID associated with the workflow
            
        Returns:
            str: ID of the new workflow
        """
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())
        self._current_workflow_id = workflow_id
        
        # Create workflow record in episodic memory
        workflow = WorkflowMemoryEntity(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            workflow_status="started",
            start_time=datetime.utcnow(),
            user_id=user_id,
            customer_id=customer_id,
            stages=[]
        )
        
        # Set the correct memory tier for episodic memory
        workflow.tier = MemoryTier.EPISODIC
        
        # Store workflow in episodic memory
        await self._memory_manager.store(workflow, user_id="system", role="admin")
        
        # Create initial context in working memory
        initial_context = ContextMemoryEntity(
            workflow_id=workflow_id,
            context_data={
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "start_time": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "customer_id": customer_id
            },
            version=1
        )
        
        # Ensure context entity is set to working memory tier
        initial_context.tier = MemoryTier.WORKING
        
        self._current_context_id = await self._memory_manager.store(initial_context, user_id="system", role="admin")
        
        logger.info(f"Started workflow {workflow_name} with ID {workflow_id}")
        return workflow_id
        
    async def complete_workflow(self, status: str = "completed", 
                              result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a workflow as complete and update its status.
        
        Args:
            status: Final status of the workflow
            result: Optional result data
        """
        if not self._current_workflow_id:
            logger.error("Cannot complete workflow: No workflow ID set")
            return
            
        # Get current workflow from episodic memory
        query = {"workflow_id": self._current_workflow_id}
        workflows = await self._memory_manager.search(
            query,
            MemoryTier.EPISODIC,
            limit=1
        )
        
        if not workflows:
            logger.error(f"Workflow {self._current_workflow_id} not found in episodic memory")
            return
            
        workflow = workflows[0]
        if not isinstance(workflow, WorkflowMemoryEntity):
            logger.error(f"Invalid workflow entity type: {type(workflow)}")
            return
            
        # Get all context versions
        contexts = await self._memory_manager.search(
            {"workflow_id": self._current_workflow_id},
            MemoryTier.WORKING
        )
        context_ids = [context.id for context in contexts if isinstance(context, ContextMemoryEntity)]
        
        # Update workflow
        workflow.end_time = datetime.utcnow()
        workflow.workflow_status = status
        workflow.result = result or {}
        workflow.context_versions = context_ids
        
        # Ensure workflow is set to episodic memory tier
        workflow.tier = MemoryTier.EPISODIC
        
        # Store updated workflow
        await self._memory_manager.store(workflow, user_id="system", role="admin")
        
        logger.info(f"Completed workflow {self._current_workflow_id} with status {status}")
        
    async def store_knowledge(self, content: str, content_type: str,
                            source: str = "agent", confidence: float = 1.0,
                            references: List[str] = None,
                            sensitivity: DataSensitivity = DataSensitivity.INTERNAL,
                            user_id: str = "system", role: str = "agent") -> str:
        """
        Store knowledge in semantic memory.
        
        Args:
            content: Knowledge content
            content_type: Type of content (e.g., "text", "json", "code")
            source: Source of the knowledge
            confidence: Confidence score (0.0 to 1.0)
            references: Optional list of reference IDs
            sensitivity: Data sensitivity level
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            str: ID of the stored knowledge entity
        """
        entity = KnowledgeEntity(
            content=content,
            content_type=content_type,
            source=source,
            confidence=confidence,
            references=references or [],
            sensitivity=sensitivity,
            creator_id=user_id
        )
        
        entity_id = await self._memory_manager.store(entity, user_id, role)
        logger.info(f"Stored knowledge entity with ID {entity_id}")
        return entity_id
        
    async def create_relationship(self, from_id: str, to_id: str, relation_type: str,
                                strength: float = 1.0, bidirectional: bool = False,
                                properties: Dict[str, Any] = None,
                                user_id: str = "system", role: str = "agent") -> str:
        """
        Create a relationship between entities in the knowledge graph.
        
        Args:
            from_id: ID of the source entity
            to_id: ID of the target entity
            relation_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
            bidirectional: Whether relationship is bidirectional
            properties: Optional properties of the relationship
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            str: ID of the stored relationship entity
        """
        entity = RelationshipEntity(
            from_id=from_id,
            to_id=to_id,
            relation_type=relation_type,
            strength=strength,
            bidirectional=bidirectional,
            properties=properties or {},
            creator_id=user_id
        )
        
        entity_id = await self._memory_manager.store(entity, user_id, role)
        logger.info(f"Created relationship {relation_type} from {from_id} to {to_id}, ID: {entity_id}")
        return entity_id
        
    async def semantic_search(self, text: str, limit: int = 10,
                            user_id: str = "system", role: str = "agent") -> List[KnowledgeEntity]:
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
        return await self._memory_manager.semantic_search(text, limit, user_id, role)
        
    async def get_workflow_history(self, customer_id: Optional[str] = None,
                                 limit: int = 10, offset: int = 0,
                                 user_id: str = "system", 
                                 role: str = "agent") -> List[WorkflowMemoryEntity]:
        """
        Get workflow execution history.
        
        Args:
            customer_id: Optional filter for specific customer
            limit: Maximum number of results
            offset: Pagination offset
            user_id: ID of user performing the operation
            role: Role of the user
            
        Returns:
            List[WorkflowMemoryEntity]: Workflow history
        """
        return await self._memory_manager.get_workflow_history(
            customer_id, user_id, role, limit, offset
        )
