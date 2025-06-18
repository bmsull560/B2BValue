# B2BValue: AI Business Value Model

## Overview
B2BValue is an AI-powered business value modeling platform with a comprehensive multi-tiered memory architecture. It enables enterprise-grade memory, knowledge management, and agent orchestration for advanced business analysis, ROI modeling, and strategic decision support.

- **Multi-tiered Memory:** Working, Episodic, Semantic, and Knowledge Graph tiers for context, history, knowledge, and relationships.
- **Agent Ecosystem:** Specialized agents for cost reduction, ROI, risk, productivity, and more.
- **Security & Compliance:** Role-based access, audit logging, and cryptographic checksums.
- **MCP Compliance:** Strict Model Context Protocol for agent data integrity and traceability.

## Architecture
```
+---------------------+
|   Working Memory    | <-- Ephemeral context
+---------------------+
|   Episodic Memory   | <-- Workflow histories
+---------------------+
|   Semantic Memory   | <-- Knowledge, embeddings, semantic search
+---------------------+
|   Knowledge Graph   | <-- Entity relationships, graph analytics
+---------------------+
```

## Quickstart
1. **Clone and set up venv:**
   ```bash
   git clone https://github.com/bmsull560/B2BValue.git
   cd B2BValue
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run tests:**
   ```bash
   python -m unittest discover
   ```

## Usage Example
See `Examples/memory_integration_example.py` for a full agent-memory workflow.

## Monitoring & Alerting
- All critical memory operations and errors are logged to `logs/critical.log` for monitoring and alerting.
- Standard logs are output via Python logging.

## Pluggable Storage Backends
- Default: File-based storage for all memory tiers.
- **Experimental:** Pluggable backend interface (`src/memory/storage_backend.py`) with a minimal SQLite backend for rapid prototyping and extension.

## Enabling Semantic Embeddings
By default, semantic search uses random vectors for compatibility. For real semantic search:
1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Install the embedding model:
   ```bash
   pip install sentence-transformers
   ```
3. The system will automatically use a transformer model for all future semantic search operations.

## Reproducible Environment Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Enable pre-commit hooks for linting and formatting:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
4. Run tests:
   ```bash
   pytest
   ```


## Reproducible Environment Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Enable pre-commit hooks for linting and formatting:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Enabling Semantic Embeddings

By default, semantic search uses random vectors for compatibility. For real semantic search:

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Install the embedding model:
   ```bash
   pip install sentence-transformers
   ```
3. The system will automatically use a transformer model for all future semantic search operations.

BValue