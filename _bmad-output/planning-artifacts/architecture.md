---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
workflowType: 'architecture'
project_name: 'coffeine-reduction'
user_name: 'Pauloschreiner'
date: '2025-12-27'
status: 'complete'
completedAt: '2025-12-27'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The 18 FRs organize into a simple CRUD-like pattern for caffeine tracking:
- **Logging subsystem** (5 FRs): Input drinks with auto/manual caffeine lookup
- **Status subsystem** (4 FRs): Query today's consumption with comparisons
- **Visualization subsystem** (3 FRs): Render trends as terminal graphs
- **Data layer** (4 FRs): Persist logs and config with integrity guarantees
- **Reference data** (2 FRs): Built-in drink database with fallback to manual entry

**Non-Functional Requirements:**
- Performance: <1s commands, <2s graph rendering
- Reliability: Crash-safe data persistence, graceful config fallback
- Usability: Works in light/dark terminals, zero-config startup

**Scale & Complexity:**
- Primary domain: CLI Tool
- Complexity level: Low
- Estimated architectural components: 4-5 (CLI parser, logging service, status service, graph renderer, data store)

### Technical Constraints & Dependencies

- Local-only operation (no network)
- Human-readable data format (inspectable by user)
- Terminal-based output only (no GUI)
- Single-user (no auth, no multi-tenancy)
- Cross-platform terminal compatibility desired

### Cross-Cutting Concerns Identified

1. **Data Integrity** - Atomic writes to prevent corruption on crash
2. **Terminal Formatting** - Consistent, readable output across themes
3. **Caffeine Lookup** - Shared reference data for logging and display

## Starter Template Evaluation

### Primary Technology Domain

CLI Tool (Python) - Building on existing Python 3.13 project structure

### Existing Technical Foundation

The project already has core tooling established:
- **Language:** Python 3.13 with strict type checking
- **Linting:** Ruff with comprehensive rule set
- **Type Checking:** basedpyright (strict mode)
- **Testing:** pytest
- **Build System:** hatchling

### Framework Selection: Typer + Plotext

**CLI Framework: Typer**
- Type-hint based API aligns with strict typing discipline
- Includes Rich for terminal formatting (satisfies NFR6)
- Simple subcommand pattern for `log`, `status`, `graph`
- Built on battle-tested Click library

**Visualization: Plotext**
- Terminal-native graph rendering
- Time-series support for daily/weekly trends
- Matplotlib-like API for familiarity

**Rationale:** Typer's type-hint approach matches the project's strict typing philosophy, while Plotext provides the terminal graph capability required for the `caf graph` command.

### Dependencies to Add

```toml
dependencies = [
    "typer[all]>=0.9.0",
    "plotext>=5.2.0",
]
```

### Architectural Decisions Established

- **CLI Pattern:** Subcommand-based (`caf log`, `caf status`, `caf graph`)
- **Output Formatting:** Rich (bundled with Typer)
- **Graph Rendering:** Plotext terminal charts
- **Type Safety:** Full type hints throughout codebase

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Data storage format and location
- CLI entry point configuration

**Important Decisions (Shape Architecture):**
- Crash safety strategy
- Config file format

**Deferred Decisions (Post-MVP):**
- PyPI distribution
- Shell completion

### Data Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Log Format | TSV | Human-readable, vi-editable, no quoting issues |
| Config Format | TOML | Python stdlib support, safe, familiar from pyproject.toml |
| File Location | `./data/` | Git-versioned, inspectable, portable |
| Crash Safety | Append-only | Inherently safe, simple implementation |

**Log File Structure (`./data/drinks.tsv`):**
```
timestamp	drink	caffeine_mg
2025-12-27T08:15	espresso	63
```

**Config File Structure (`./data/config.toml`):**
```toml
[display]
graph_days = 14
```

### Infrastructure & Deployment

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package Manager | uv | Fast, auto-syncs, no manual venv |
| Run Method | `uv run caf` | Zero friction during development |
| Entry Point | `[project.scripts]` | Standard, works with uv |

**Entry Point Configuration:**
```toml
[project.scripts]
caf = "src.cli:app"
```

## Implementation Patterns & Consistency Rules

### Pattern Summary

This is a small Python CLI - patterns are kept minimal and follow Python conventions.

### Naming Patterns

**Follow PEP 8 throughout:**

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `log_drink()`, `get_today_total()` |
| Variables | snake_case | `caffeine_mg`, `drink_name` |
| Classes | PascalCase | `DrinkEntry`, `CaffeineDatabase` |
| Constants | UPPER_SNAKE | `DEFAULT_ESPRESSO_MG = 63` |
| Files/Modules | snake_case | `drink_log.py`, `caffeine_db.py` |

### Structure Patterns

**Flat module organization:**
```
src/
  __init__.py
  cli.py          # Typer app & commands
  log.py          # Drink logging logic
  status.py       # Status display logic
  graph.py        # Graph rendering
  data.py         # TSV read/write
  drinks_db.py    # Caffeine lookup table
```

**Data location:**
```
data/
  drinks.tsv      # Append-only drink log
  config.toml     # User configuration
```

### Format Patterns

**Date/Time:** ISO 8601 format in all data files
- Example: `2025-12-27T08:15:00`
- Use `datetime.isoformat()` for consistency

**TSV Log Format:**
```
timestamp	drink	caffeine_mg
2025-12-27T08:15:00	espresso	63
```

### Error Handling Patterns

**Use Typer's error handling:**
```python
import typer

def some_command():
    if error_condition:
        typer.echo("Error: descriptive message", err=True)
        raise typer.Exit(1)
```

**Exit codes:**
- `0` = Success
- `1` = User error (bad input, file not found)
- `2` = Internal error (unexpected)

### All AI Agents MUST:

1. Follow PEP 8 naming conventions
2. Place new modules in flat `src/` structure
3. Use ISO 8601 for all timestamps
4. Use Typer's error handling, not raw print/sys.exit
5. Append to TSV log, never rewrite

## Project Structure & Boundaries

### Complete Project Directory Structure

```
coffeine-reduction/
├── pyproject.toml          # Project config, dependencies, entry point
├── uv.lock                  # Locked dependencies
├── README.md                # Project documentation
├── .gitignore               # Git ignore patterns
├── .pre-commit-config.yaml  # Pre-commit hooks
├── data/
│   ├── drinks.tsv           # Append-only drink log
│   └── config.toml          # User configuration (optional)
├── src/
│   ├── __init__.py          # Package marker
│   ├── cli.py               # Typer app, command definitions
│   ├── log.py               # Drink logging logic
│   ├── status.py            # Status display logic
│   ├── graph.py             # Graph rendering with Plotext
│   ├── data.py              # TSV read/write, config loading
│   └── drinks_db.py         # Built-in caffeine database
└── tests/
    ├── __init__.py
    ├── test_cli.py          # CLI command tests
    ├── test_log.py          # Logging logic tests
    ├── test_status.py       # Status calculation tests
    ├── test_graph.py        # Graph rendering tests
    ├── test_data.py         # Data persistence tests
    └── test_drinks_db.py    # Database lookup tests
```

### Module Boundaries

**cli.py** - Entry point, command definitions only
- Defines Typer app and commands
- Delegates to other modules for logic
- Handles user-facing output via Rich/Typer

**log.py** - Drink logging logic
- Validates drink input
- Looks up caffeine via drinks_db
- Calls data.py to append entry

**status.py** - Status calculation
- Reads today's entries from data.py
- Calculates totals and comparisons
- Formats output for display

**graph.py** - Visualization
- Reads historical data from data.py
- Renders terminal graph via Plotext
- Handles date range calculations

**data.py** - Data layer
- TSV append/read operations
- TOML config loading
- Ensures data directory exists

**drinks_db.py** - Reference data
- Dictionary of drink → caffeine_mg
- Fuzzy matching for drink names
- Returns None for unknown drinks

### Data Flow

```
User Command → cli.py → [log|status|graph].py → data.py → drinks.tsv
                              ↓
                         drinks_db.py (lookup)
```

### Requirements Mapping

| Requirement | Primary Module | Supporting Modules |
|-------------|----------------|-------------------|
| FR1-2: Log drink | log.py | cli.py, data.py |
| FR3: Auto-lookup caffeine | drinks_db.py | log.py |
| FR4-5: Log confirmation | cli.py | log.py |
| FR6-7: Today's total/list | status.py | cli.py, data.py |
| FR8-9: Comparison to yesterday | status.py | data.py |
| FR10-12: Graph display | graph.py | cli.py, data.py |
| FR13-15: Data persistence | data.py | - |
| FR16: Config file | data.py | - |
| FR17-18: Drink database | drinks_db.py | log.py |

### Test Organization

Tests mirror source structure:
- Each `src/X.py` has a corresponding `tests/test_X.py`
- Tests use pytest fixtures for test data
- No external dependencies in tests (mock file I/O)

## Architecture Validation Results

### Coherence Validation ✅

All architectural decisions are compatible and reinforce each other:
- Python 3.13 + Typer + Plotext + Rich work seamlessly together
- TSV/TOML data formats align with human-readability requirement
- PEP 8 patterns match Python ecosystem conventions
- uv tooling integrates cleanly with pyproject.toml

### Requirements Coverage ✅

**All 18 Functional Requirements covered:**
- Logging (FR1-5): cli.py → log.py → drinks_db.py → data.py
- Status (FR6-9): cli.py → status.py → data.py
- Graph (FR10-12): cli.py → graph.py → data.py
- Data (FR13-16): data.py with append-only TSV
- Database (FR17-18): drinks_db.py

**All 7 Non-Functional Requirements addressed:**
- Performance (NFR1-2): Local ops, efficient Plotext
- Reliability (NFR3-5): Append-only persistence
- Usability (NFR6-7): Rich theming, sensible defaults

### Implementation Readiness ✅

- 6 modules with clear, single responsibilities
- Data flow documented and straightforward
- Patterns comprehensive for consistency
- Test structure mirrors source

### Architecture Completeness Checklist

- [x] Project context analyzed
- [x] Technology stack specified (Python, Typer, Plotext)
- [x] Data architecture defined (TSV, TOML, append-only)
- [x] Implementation patterns established (PEP 8, ISO 8601)
- [x] Project structure complete
- [x] Requirements mapped to modules
- [x] All FRs/NFRs covered

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Simple, focused architecture matching project scope
- Clear module boundaries prevent conflicts
- Human-readable data formats aid debugging
- Standard Python conventions reduce learning curve

**First Implementation Step:**
Add dependencies to pyproject.toml and create cli.py with Typer app skeleton

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-27
**Document Location:** _bmad-output/planning-artifacts/architecture.md

### Final Architecture Deliverables

**Complete Architecture Document**
- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**Implementation Ready Foundation**
- 10+ architectural decisions made
- 5 implementation patterns defined
- 6 source modules specified
- 25 requirements (18 FR + 7 NFR) fully supported

**AI Agent Implementation Guide**
- Technology stack: Python 3.13, Typer, Plotext, Rich
- Consistency rules: PEP 8, ISO 8601, Typer errors
- Project structure with clear module boundaries
- Data flow and integration patterns

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing coffeine-reduction. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
```bash
# Add dependencies to pyproject.toml
uv add "typer[all]" plotext

# Create CLI entry point
# src/cli.py with Typer app
```

**Development Sequence:**
1. Add Typer and Plotext dependencies
2. Create cli.py with basic Typer app skeleton
3. Implement drinks_db.py with caffeine lookup
4. Implement data.py for TSV operations
5. Build log, status, graph commands
6. Add tests for each module

### Architecture Status

**READY FOR IMPLEMENTATION** ✅

---

*Architecture created collaboratively on 2025-12-27*

