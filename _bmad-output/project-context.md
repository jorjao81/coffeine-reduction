---
project_name: 'coffeine-reduction'
user_name: 'Pauloschreiner'
date: '2025-12-27'
sections_completed: ['technology_stack', 'implementation_rules', 'critical_donts']
---

# Project Context for AI Agents

_Critical rules and patterns for coffeine-reduction CLI implementation._

---

## Technology Stack & Versions

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.13 | Runtime |
| Typer | >=0.9.0 | CLI framework |
| Plotext | >=5.2.0 | Terminal graphs |
| Rich | (via Typer) | Terminal formatting |
| Ruff | v0.8.4 | Linting + formatting |
| basedpyright | strict | Type checking |
| pytest | latest | Testing |
| uv | latest | Package/run management |

---

## Critical Implementation Rules

### Python & Type Safety

- **basedpyright strict mode** - All code must pass strict type checking
- **Type hints required** on all function signatures
- **No `# type: ignore`** without explicit justification
- Use `from __future__ import annotations` if needed for forward refs

### CLI Framework (Typer)

- **Error handling pattern:**
  ```python
  typer.echo("Error: message", err=True)
  raise typer.Exit(1)
  ```
- **Exit codes:** 0=success, 1=user error, 2=internal error
- Use Rich console (via Typer) for all formatted output

### Data Patterns

- **TSV log is append-only** - NEVER rewrite, only append
- **ISO 8601 timestamps** - Use `datetime.isoformat()` always
- **Tab-separated values** - No quoting needed, tabs rare in drink names

### Testing Rules

- Tests in `tests/test_*.py` mirroring `src/*.py`
- **Mock file I/O** - Don't create real files in tests
- **pytest runs on pre-commit** - Tests must pass before commit

### Code Quality

- **Ruff auto-fixes on commit** - Let it format, don't fight it
- **Line length: 120 chars** (configured in pyproject.toml)
- **PEP 8 naming** enforced by Ruff

### Development Workflow

- **Run with:** `uv run caf <command>`
- **Pre-commit hooks must pass** before any commit:
  - ruff (lint + format)
  - basedpyright
  - pytest
  - markdownlint
- **no-claude-commit hook** blocks AI-generated commits

---

## Critical Don'ts

- **DON'T** use `print()` - use `typer.echo()` or Rich console
- **DON'T** use `sys.exit()` - use `raise typer.Exit(code)`
- **DON'T** rewrite the TSV log file - append only
- **DON'T** use camelCase - Python uses snake_case
- **DON'T** skip type hints - basedpyright will fail
- **DON'T** commit without running `uv run pytest` first
