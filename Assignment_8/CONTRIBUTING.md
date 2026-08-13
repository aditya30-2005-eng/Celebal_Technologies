# Contributing to E-Commerce Order Analytics System

Thank you for considering a contribution. This document describes the
guidelines that keep the repository consistent and maintainable.

## Development Setup

1. Clone the repository and create a virtual environment.

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate  # Linux / macOS
   ```

2. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Run the full pipeline to generate a fresh database.

   ```bash
   python run_pipeline.py
   ```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) throughout.
- Use type hints on all public function and method signatures.
- Prefer `pathlib.Path` over hard-coded strings.
- Keep functions small (under ~50 lines where practical).
- Centralise configuration in `config.py`; avoid magic numbers in modules.
- Use the standard `logging` module instead of `print()`.
- Add meaningful docstrings for classes and public functions only.

## Testing

- All new behaviour must ship with tests under `tests/`.
- Run the full suite before opening a pull request.

  ```bash
  pytest -v
  ```

## SQL Guidelines

- Every query in `sql/` must execute against the schema in `sql/schema.sql`.
- Use uppercase SQL keywords and explicit column aliases.
- Add a short human-readable comment at the top of each file describing
  the business question the query answers.

## Branching and Commits

- Create a feature branch with a descriptive name, e.g. `feature/rfm-report`.
- Use conventional commit messages, for example
  `feat: add yearly revenue report`.

## Pull Requests

- Keep pull requests focused on a single concern.
- Reference the issue or requirement being addressed.
- Include a short summary and, when relevant, sample output.

## Reporting Issues

When opening an issue, include the command that failed, the expected output,
the actual output, and the Python version in use.

