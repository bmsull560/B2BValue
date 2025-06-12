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
BValue