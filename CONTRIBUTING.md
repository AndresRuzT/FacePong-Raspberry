# Contributing to FacePong

Thank you for contributing to FacePong! This project is developed for academic and scientific research applications, adhering to high software engineering standards.

## Code of Conduct

Please maintain an inclusive, respectful, and constructive environment.

## Development Workflow

1. Fork or branch from `main` or `develop`.
2. Create a virtual environment using Python 3.11+:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```
3. Implement your changes following PEP 8, strict type hints, and complete docstrings.
4. Run tests and linting:
   ```bash
   ruff check .
   ruff format --check .
   mypy src/
   pytest
   ```
5. Commit using **Conventional Commits**:
   - `feat(...)`: New feature or capability
   - `fix(...)`: Bug fix
   - `perf(...)`: Performance optimization
   - `refactor(...)`: Code refactoring without behavioral change
   - `test(...)`: Adding or updating test suites
   - `docs(...)`: Documentation updates
   - `chore(...)`: Maintenance and dependency updates

## Architecture Principles

- **Separation of Concerns:** Vision inference must never run inside the Pygame rendering loop.
- **Minimal Allocation:** Avoid large allocations or matrix deepcopies inside the high-frequency tick loop.
- **Input Independence:** All gameplay mechanics must interact solely with `InputAdapter` abstractions.
