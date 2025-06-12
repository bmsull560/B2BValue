# Entity Schemas for B2BValue Memory System

Below are the schemas for all major memory entities. All fields are required unless marked optional.

## ContextMemoryEntity
| Field         | Type           | Description                                   |
|-------------- |---------------|-----------------------------------------------|
| id            | str            | Unique entity ID                              |
| workflow_id   | str            | Associated workflow ID                        |
| version       | int            | Context version number                        |
| data          | dict           | Context data                                  |
| created_at    | datetime       | Creation timestamp                            |
| updated_at    | datetime       | Last update timestamp                         |
| creator_id    | str            | User/agent who created                        |
| sensitivity   | DataSensitivity| Data sensitivity level                        |
| tier          | MemoryTier     | Memory tier (should be WORKING)               |
| ...           | ...            | See source for full base fields               |

## WorkflowMemoryEntity
| Field         | Type           | Description                                   |
|-------------- |---------------|-----------------------------------------------|
| id            | str            | Unique entity ID                              |
| workflow_id   | str            | Workflow identifier                           |
| workflow_name | str            | Name of the workflow                          |
| workflow_status| str           | Status (created/completed/...)                |
| start_time    | datetime       | Workflow start time                           |
| end_time      | datetime?      | Workflow end time                             |
| user_id       | str?           | User who started workflow                     |
| customer_id   | str?           | Customer ID                                   |
| context_versions| list[str]    | List of context entity IDs                    |
| stages        | list[dict]     | Workflow stages                               |
| result        | dict?          | Workflow result                               |
| ...           | ...            | See source for full base fields               |

## KnowledgeEntity
| Field         | Type           | Description                                   |
|-------------- |---------------|-----------------------------------------------|
| id            | str            | Unique entity ID                              |
| content       | str            | Knowledge content                             |
| content_type  | str            | Type (text/json/code/...)                     |
| vector_embedding| list[float]? | Semantic embedding vector                     |
| source        | str            | Originating agent or process                  |
| confidence    | float          | Confidence score                              |
| references    | list[str]      | Reference IDs                                 |
| ...           | ...            | See source for full base fields               |

## RelationshipEntity
| Field         | Type           | Description                                   |
|-------------- |---------------|-----------------------------------------------|
| id            | str            | Unique entity ID                              |
| from_id       | str            | Source entity ID                              |
| to_id         | str            | Target entity ID                              |
| relation_type | str            | Relationship type                             |
| strength      | float          | Relationship strength                         |
| bidirectional | bool           | Is the relationship bidirectional?            |
| properties    | dict           | Additional properties                         |
| ...           | ...            | See source for full base fields               |

---

**Note:** See `src/memory/types.py` for authoritative field definitions and types. This document is for quick reference and onboarding.
