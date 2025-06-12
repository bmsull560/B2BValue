# B2

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