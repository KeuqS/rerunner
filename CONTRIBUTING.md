# Contributing to Rerunner

Thank you for your interest in contributing to **Rerunner**! We are building the industry standard for deterministic AI agent testing, replay, and CI/CD pipelines.

Whether you're fixing a bug, adding an SDK transport adapter, optimizing request matching, or improving documentation, your contributions are welcome.

---

## Code of Conduct

All contributors and participants must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to security@rerunner.dev.

---

## Development Setup

We recommend using [uv](https://github.com/astral-sh/uv) or a standard Python virtual environment (Python 3.11+ required).

```bash
# 1. Clone the repository
git clone https://github.com/your-org/rerunner.git
cd rerunner

# 2. Create and activate a virtual environment
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install in editable mode with development dependencies
pip install -e ".[dev]"
```

---

## Code Quality Standards

We enforce strict quality standards identical to leading AI and MLOps open-source projects:

### 1. Formatting and Linting
We use [Ruff](https://github.com/astral-sh/ruff) for fast, consistent linting and formatting:
```bash
# Check code style
ruff check .

# Automatically fix format issues
ruff format .
```

### 2. Strict Type Checking
Rerunner is 100% typed with zero `Any` in public APIs:
```bash
mypy src tests
```

### 3. Running Tests
Run the entire test suite locally:
```bash
pytest
```

---

## Pull Request Guidelines

1. **Keep PRs focused**: Each pull request should address a single issue or implement a single feature.
2. **Include tests**: Every bug fix or new feature must be accompanied by comprehensive unit tests.
3. **Update documentation**: If changing user-facing APIs or CLI behavior, update docstrings and README.
4. **Follow conventional commits**:
   - `feat:` for new capabilities
   - `fix:` for bug fixes
   - `docs:` for documentation updates
   - `test:` for test additions or refactors
   - `chore:` for tooling and dependencies

---

## How to Get Involved

Check out issues labeled:
- `good first issue`: Ideal for new contributors.
- `help wanted`: Important features or performance enhancements seeking community collaboration.
- `rfc`: Architectural proposals open for design feedback.
