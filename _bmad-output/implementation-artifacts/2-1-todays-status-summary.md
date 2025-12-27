# Story 2.1: Today's Status Summary

Status: done

## Story

As a **user**,
I want **to see today's total caffeine intake and a list of drinks I've logged**,
So that **I can track my daily consumption at a glance**.

## Acceptance Criteria

1. **Given** the user has logged drinks today
   **When** they run `caf status`
   **Then** they see today's total caffeine (e.g., "Today: 189mg")
   **And** a list of drinks logged today with times and amounts

2. **Given** the user has not logged any drinks today
   **When** they run `caf status`
   **Then** they see "Today: 0mg" and a message like "No drinks logged today"

## Tasks / Subtasks

- [x] Task 1: Create status.py module (AC: #1, #2)
  - [x] 1.1: Create `src/status.py` with `get_status_data()` function that returns today's entries and total
  - [x] 1.2: Implement `format_time()` function to format timestamp display
  - [x] 1.3: Handle empty day case (no entries) with appropriate messaging
  - [x] 1.4: Write tests in `tests/test_status.py`

- [x] Task 2: Implement status CLI command (AC: #1, #2)
  - [x] 2.1: Update `src/cli.py` status command to call status module functions
  - [x] 2.2: Display today's total with Rich formatting
  - [x] 2.3: Display list of drinks with timestamps and amounts
  - [x] 2.4: Handle empty day case with friendly message
  - [x] 2.5: Add CLI tests to `tests/test_cli.py`

- [x] Task 3: Verify acceptance criteria
  - [x] 3.1: Test with logged drinks - verify total and list display
  - [x] 3.2: Test with no drinks - verify "0mg" and "No drinks logged" message
  - [x] 3.3: Test time formatting is human-readable

- [x] Task 4: Run all quality gates
  - [x] 4.1: Run `uv run ruff check src tests`
  - [x] 4.2: Run `uv run basedpyright`
  - [x] 4.3: Run `uv run pytest` - verify all tests pass

## Dev Notes

### Architecture Compliance

**Module to Create:**
- `src/status.py` - Status calculation and display logic (per architecture decision)

**Module to Modify:**
- `src/cli.py` - Replace placeholder status command with real implementation

**Data Flow:**
```
User runs: caf status
     │
     ▼
cli.py calls status.get_status_data()
     │
     ▼
status.py calls data.get_today_entries() and data.get_today_total()
     │
     ▼
status.py formats output (time, drink, mg for each entry)
     │
     ▼
cli.py displays with Rich console formatting
```

### Technical Requirements

**New Module: src/status.py**
```python
from __future__ import annotations

from src import data


def get_status_data() -> tuple[list[tuple[str, str, int]], int]:
    """
    Get today's status data.

    Returns:
        Tuple of (entries, total) where entries is list of (timestamp, drink, mg)
    """
    entries = data.get_today_entries()
    total = data.get_today_total()
    return entries, total


def format_time(iso_timestamp: str) -> str:
    """
    Format ISO timestamp to human-readable time.

    Example: "2025-12-27T08:15:00" -> "08:15"
    """
    # Extract HH:MM from ISO format
    if "T" in iso_timestamp:
        time_part = iso_timestamp.split("T")[1]
        return time_part[:5]  # HH:MM
    return iso_timestamp
```

**CLI Update Pattern (follow established patterns from Story 1.2/1.3):**
```python
@app.command()
def status() -> None:
    """Show today's caffeine intake summary."""
    from src import status as status_module

    entries, total = status_module.get_status_data()

    console.print(f"[bold]Today:[/bold] [cyan]{total}mg[/cyan]")
    console.print()

    if not entries:
        console.print("[dim]No drinks logged today[/dim]")
        return

    for timestamp, drink, mg in entries:
        time_str = status_module.format_time(timestamp)
        console.print(f"  [dim]{time_str}[/dim]  {drink:<20} [cyan]{mg}mg[/cyan]")
```

**Output Format Examples:**

*With drinks logged:*
```
Today: 189mg

  08:15  espresso             63mg
  10:30  coffee               95mg
  14:00  green tea            31mg
```

*No drinks today:*
```
Today: 0mg

No drinks logged today
```

### Previous Story Learnings (from Epic 1)

**CRITICAL - Apply These Patterns:**
1. **Rich console is set up** - Use `console.print()` for output (already imported in cli.py)
2. **Type hints required everywhere** - basedpyright strict mode
3. **Use `from __future__ import annotations`** for all new modules
4. **Follow lazy import pattern** - Import modules inside commands to avoid circular imports
5. **Error handling pattern** - Not needed here (no user input to validate)

**Code Quality Standards (from Story 1-3 review):**
- All tests must pass before marking complete
- Ruff, basedpyright must report 0 errors
- 46 tests currently passing - don't break them

### Current Code State

**src/cli.py status command (current - placeholder):**
```python
@app.command()
def status() -> None:
    """Show today's caffeine intake summary."""
    console.print("[dim]Status... (not implemented yet)[/dim]")
```

**src/data.py (already has needed functions):**
- `get_today_entries()` - Returns list of (timestamp, drink, mg) for today
- `get_today_total()` - Returns int total of today's caffeine

### Testing Requirements

**New Test File: tests/test_status.py**
```python
"""Tests for status module."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src import status


def test_get_status_data_with_entries() -> None:
    """Test status data with drinks logged."""
    mock_entries = [
        ("2025-12-27T08:15:00", "espresso", 63),
        ("2025-12-27T10:30:00", "coffee", 95),
    ]
    with patch("src.status.data.get_today_entries", return_value=mock_entries):
        with patch("src.status.data.get_today_total", return_value=158):
            entries, total = status.get_status_data()
            assert len(entries) == 2
            assert total == 158


def test_get_status_data_empty() -> None:
    """Test status data with no drinks logged."""
    with patch("src.status.data.get_today_entries", return_value=[]):
        with patch("src.status.data.get_today_total", return_value=0):
            entries, total = status.get_status_data()
            assert entries == []
            assert total == 0


def test_format_time() -> None:
    """Test ISO timestamp to time formatting."""
    assert status.format_time("2025-12-27T08:15:00") == "08:15"
    assert status.format_time("2025-12-27T14:30:45") == "14:30"
```

**New CLI Tests in tests/test_cli.py:**
```python
def test_status_with_drinks(cli_runner, tmp_data_dir) -> None:
    """Test status command with logged drinks."""
    # Log some drinks first
    cli_runner.invoke(app, ["log", "espresso"])
    cli_runner.invoke(app, ["log", "coffee"])

    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Today:" in result.output
    assert "mg" in result.output
    assert "espresso" in result.output
    assert "coffee" in result.output


def test_status_empty_day(cli_runner, tmp_data_dir) -> None:
    """Test status command with no drinks logged."""
    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Today:" in result.output
    assert "0mg" in result.output
    assert "No drinks logged" in result.output
```

### Project Structure Notes

**New Files:**
- `src/status.py` - Status display logic module
- `tests/test_status.py` - Tests for status module

**Modified Files:**
- `src/cli.py` - Replace status placeholder with implementation
- `tests/test_cli.py` - Add status command tests

**Architecture Alignment:**
- Follows flat `src/` module organization from architecture
- status.py handles "Status display logic" per module boundaries
- CLI delegates to status module per established patterns

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.1]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Directory Structure]
- [Source: _bmad-output/implementation-artifacts/1-3-log-unknown-drinks-with-custom-caffeine.md#Dev Agent Record]
- [Source: _bmad-output/project-context.md#CLI Framework (Typer)]

### Critical Don'ts

- **DON'T** use `print()` - use `console.print()`
- **DON'T** skip type hints - basedpyright strict mode is active
- **DON'T** break existing tests (46 currently passing)
- **DON'T** modify data.py - it already has the functions needed
- **DON'T** use camelCase - Python uses snake_case

### Edge Cases to Handle

1. **Empty drink log file** - Should show 0mg and "No drinks logged"
2. **Corrupted entries** - data.py already handles this (skips bad rows)
3. **Midnight rollover** - get_today_entries() uses current date, handles correctly

### Pre-Commit Hooks

All must pass before code review:
1. `uv run ruff check --fix src tests` - Linting
2. `uv run basedpyright` - Type checking
3. `uv run pytest` - All tests pass

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- RED-GREEN-REFACTOR cycle followed for all implementations
- Tests written before implementation code
- All 53 tests pass (added 7 new tests)

### Completion Notes List

- Created `src/status.py` with `get_status_data()` and `format_time()` functions
- Updated `src/cli.py` status command to display today's total and drink list with Rich formatting
- Created `tests/test_status.py` with 4 unit tests for status module
- Added 3 new CLI tests to `tests/test_cli.py` for status command
- Updated existing placeholder test to verify real implementation
- All acceptance criteria verified manually: AC #1 (drinks logged) and AC #2 (no drinks) both pass
- Quality gates: Ruff clean, basedpyright 0 errors, all 53 tests pass

### File List

**Files Created:**
- `src/status.py` - Status display logic module with get_status_data() and format_time()
- `tests/test_status.py` - 4 unit tests for status module

**Files Modified:**
- `src/cli.py` - Replaced status placeholder with full implementation
- `tests/test_cli.py` - Added 3 new status tests, updated 1 placeholder test

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5 (code-review workflow)
**Date:** 2025-12-27

### Issues Found & Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| HIGH | `get_status_data()` reads TSV file twice (calls get_today_entries then get_today_total which re-reads) | Fixed: calculate total from cached entries |
| MEDIUM | `test_status_with_drinks` doesn't verify actual total | Fixed: added assertion for "158mg" |
| MEDIUM | `test_status_shows_time_format` doesn't verify time format | Fixed: added assertion that date doesn't appear in output |

### Files Modified During Review

- `src/status.py` - Optimized get_status_data() to avoid redundant file read
- `tests/test_cli.py` - Strengthened test assertions for status command

### Quality Gates Post-Review

- Ruff: All checks passed
- basedpyright: 0 errors, 0 warnings
- pytest: 68 passed

## Change Log

- 2025-12-27: Story 2.1 Today's Status Summary implemented - all acceptance criteria satisfied
- 2025-12-27: Code review completed - fixed 3 issues (1 high, 2 medium)

