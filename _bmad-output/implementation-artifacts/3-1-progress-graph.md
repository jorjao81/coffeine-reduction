# Story 3.1: Progress Graph

Status: done

## Story

As a **user**,
I want **to see a graph of my daily caffeine totals over time**,
So that **I can visualize my progress toward reducing consumption**.

## Acceptance Criteria

1. **Given** the user has logged drinks over multiple days
   **When** they run `caf graph`
   **Then** a terminal graph displays daily caffeine totals
   **And** the x-axis shows dates, y-axis shows mg

2. **Given** the user runs `caf graph`
   **When** there are 14+ days of data
   **Then** the graph shows the most recent 14 days by default

3. **Given** a config file exists at `./data/config.toml` with `graph_days = 30`
   **When** the user runs `caf graph`
   **Then** the graph shows 30 days instead of the default 14

4. **Given** no config file exists
   **When** the user runs `caf graph`
   **Then** the default of 14 days is used (no error)

5. **Given** the user has fewer days of data than the configured range
   **When** they run `caf graph`
   **Then** the graph shows all available data

## Tasks / Subtasks

- [x] Task 1: Add config loading to data module (AC: #3, #4)
  - [x] 1.1: Add `load_config()` function to `src/data.py` - reads TOML config, returns dict with defaults
  - [x] 1.2: Add `get_graph_days()` function - returns configured days or default 14
  - [x] 1.3: Handle missing config file gracefully (return defaults)
  - [x] 1.4: Add tests to `tests/test_data.py`

- [x] Task 2: Add historical data retrieval (AC: #1, #2, #5)
  - [x] 2.1: Add `get_daily_totals(days: int)` function to `src/data.py` - returns list of (date, total_mg)
  - [x] 2.2: Handle date aggregation (sum all drinks per day)
  - [x] 2.3: Handle missing days (include as 0mg)
  - [x] 2.4: Add tests to `tests/test_data.py`

- [x] Task 3: Create graph module (AC: #1)
  - [x] 3.1: Create `src/graph.py` with `render_graph(daily_totals, days)` function
  - [x] 3.2: Use Plotext to create bar chart with dates on x-axis, mg on y-axis
  - [x] 3.3: Format dates for readability (MM-DD format)
  - [x] 3.4: Add title "Daily Caffeine Intake"
  - [x] 3.5: Add tests to `tests/test_graph.py`

- [x] Task 4: Implement graph CLI command (AC: #1, #2, #3, #4, #5)
  - [x] 4.1: Replace placeholder in `src/cli.py` with real implementation
  - [x] 4.2: Load config to get graph_days setting
  - [x] 4.3: Get daily totals for configured number of days
  - [x] 4.4: Call graph module to render
  - [x] 4.5: Handle no data case with friendly message
  - [x] 4.6: Add CLI tests to `tests/test_cli.py`

- [x] Task 5: Verify all acceptance criteria
  - [x] 5.1: Test with multi-day data - verify graph displays correctly
  - [x] 5.2: Test with 14+ days - verify only recent 14 shown (default)
  - [x] 5.3: Test with config file - verify custom graph_days works
  - [x] 5.4: Test without config file - verify defaults work
  - [x] 5.5: Test with fewer days than range - verify all data shown

- [x] Task 6: Run all quality gates
  - [x] 6.1: Run `uv run ruff check src tests`
  - [x] 6.2: Run `uv run basedpyright`
  - [x] 6.3: Run `uv run pytest` - verify all tests pass

## Dev Notes

### Architecture Compliance

**New Module to Create:**
- `src/graph.py` - Graph rendering with Plotext (per architecture decision)

**Modules to Modify:**
- `src/data.py` - Add config loading and historical data functions
- `src/cli.py` - Replace graph placeholder with real implementation

**Data Flow:**
```
User runs: caf graph
     │
     ▼
cli.py calls data.get_graph_days() → config_days (default 14)
     │
     ▼
cli.py calls data.get_daily_totals(config_days)
     │
     ├── Reads all entries from drinks.tsv
     ├── Groups by date, sums caffeine per day
     └── Returns last N days of (date, total_mg)
     │
     ▼
cli.py calls graph.render_graph(daily_totals)
     │
     ├── Uses Plotext bar chart
     ├── X-axis: dates (MM-DD format)
     ├── Y-axis: caffeine mg
     └── Renders to terminal
```

### Technical Requirements

**Config File Format (`./data/config.toml`):**
```toml
[display]
graph_days = 14
```

**New Data Functions: src/data.py**
```python
import tomllib
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

CONFIG_FILE = DATA_DIR / "config.toml"
DEFAULT_GRAPH_DAYS = 14


def load_config() -> dict[str, Any]:
    """
    Load config from TOML file. Returns empty dict if file doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open("rb") as f:
        return tomllib.load(f)


def get_graph_days() -> int:
    """Get number of days to show in graph from config, or default 14."""
    config = load_config()
    display = config.get("display", {})
    return display.get("graph_days", DEFAULT_GRAPH_DAYS)


def get_all_entries() -> list[tuple[str, str, int]]:
    """Read all entries from drinks.tsv. Returns list of (timestamp, drink, mg)."""
    if not DRINKS_FILE.exists():
        return []

    entries: list[tuple[str, str, int]] = []
    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == TSV_COLUMNS:
                try:
                    caffeine_mg = int(parts[2])
                    entries.append((parts[0], parts[1], caffeine_mg))
                except ValueError:
                    continue
    return entries


def get_daily_totals(days: int) -> list[tuple[str, int]]:
    """
    Get daily caffeine totals for the last N days.

    Args:
        days: Number of days to include

    Returns:
        List of (date_str, total_mg) sorted by date ascending.
        Includes days with 0mg if no drinks logged.
    """
    # Build date range
    today = datetime.now().date()
    date_range = [(today - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]

    # Aggregate by date
    daily_sums: dict[str, int] = defaultdict(int)
    for timestamp, _, mg in get_all_entries():
        date_part = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]
        daily_sums[date_part] += mg

    # Build result with zeros for missing days
    result: list[tuple[str, int]] = []
    for date in date_range:
        result.append((date, daily_sums.get(date, 0)))

    # Filter to only days with data or within range
    # If fewer days of data exist, only return those
    first_data_idx = None
    for i, (_, mg) in enumerate(result):
        if mg > 0:
            first_data_idx = i
            break

    if first_data_idx is not None:
        return result[first_data_idx:]

    return []  # No data at all
```

**New Graph Module: src/graph.py**
```python
"""Graph rendering for caffeine intake visualization."""

from __future__ import annotations

import plotext as plt


def render_graph(daily_totals: list[tuple[str, int]]) -> None:
    """
    Render a bar chart of daily caffeine totals.

    Args:
        daily_totals: List of (date_str, total_mg) tuples
    """
    if not daily_totals:
        return

    # Extract dates and values
    dates = [d[0] for d in daily_totals]
    values = [d[1] for d in daily_totals]

    # Format dates for readability (MM-DD)
    formatted_dates = [d[5:] for d in dates]  # "2025-12-27" -> "12-27"

    # Clear any previous plot
    plt.clear_figure()

    # Create bar chart
    plt.bar(formatted_dates, values)
    plt.title("Daily Caffeine Intake")
    plt.xlabel("Date")
    plt.ylabel("Caffeine (mg)")

    # Render to terminal
    plt.show()
```

**CLI Update Pattern:**
```python
@app.command()
def graph() -> None:
    """Display caffeine intake graph over time."""
    from src import data
    from src import graph as graph_module

    # Get configured number of days
    days = data.get_graph_days()

    # Get daily totals
    daily_totals = data.get_daily_totals(days)

    if not daily_totals:
        console.print("[dim]No data to graph. Log some drinks first![/dim]")
        return

    # Render the graph
    graph_module.render_graph(daily_totals)
```

**Output Example (terminal):**
```
                    Daily Caffeine Intake
     ┌─────────────────────────────────────────────────────┐
 300 ┤                                                     │
     │     █                                               │
 250 ┤     █                                               │
     │     █                                    █          │
 200 ┤     █               █                    █          │
     │     █     █         █    █               █    █     │
 150 ┤     █     █    █    █    █    █    █     █    █     │
     │     █     █    █    █    █    █    █     █    █     │
 100 ┤     █     █    █    █    █    █    █     █    █     │
     │     █     █    █    █    █    █    █     █    █     │
  50 ┤     █     █    █    █    █    █    █     █    █     │
     │     █     █    █    █    █    █    █     █    █     │
   0 ┼─────█─────█────█────█────█────█────█─────█────█─────┘
       12-14 12-15 12-16 12-17 12-18 12-19 12-20 12-21 12-22
                              Date
```

### Previous Story Learnings (from Epic 1 + Epic 2)

**CRITICAL - Apply These Patterns:**
1. **Rich console is set up** - Use `console.print()` for messages, Plotext for graph
2. **Type hints required everywhere** - basedpyright strict mode
3. **Use `from __future__ import annotations`** for all new modules
4. **Lazy imports inside commands** - Prevents circular imports
5. **Color conventions** - Use `[dim]` for secondary messages
6. **Test patterns established** - Mock file I/O, use fixtures

**Code Quality Standards (from reviews):**
- Avoid redundant file reads (cache entries when possible)
- All tests must pass before marking complete
- Ruff, basedpyright must report 0 errors
- 68 tests currently passing - don't break them

### Testing Requirements

**New Tests for tests/test_data.py:**
```python
def test_load_config_missing_file() -> None:
    """Test config loading when file doesn't exist."""
    config = data.load_config()
    assert config == {}


def test_load_config_with_file(tmp_data_dir) -> None:
    """Test config loading from file."""
    config_file = tmp_data_dir / "config.toml"
    config_file.write_text("[display]\ngraph_days = 30\n")

    config = data.load_config()
    assert config["display"]["graph_days"] == 30


def test_get_graph_days_default() -> None:
    """Test default graph days when no config."""
    with patch("src.data.load_config", return_value={}):
        assert data.get_graph_days() == 14


def test_get_graph_days_custom() -> None:
    """Test custom graph days from config."""
    with patch("src.data.load_config", return_value={"display": {"graph_days": 30}}):
        assert data.get_graph_days() == 30


def test_get_daily_totals(tmp_data_dir) -> None:
    """Test daily totals aggregation."""
    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
        f"{yesterday}T10:00:00\tcoffee\t95\n"
        f"{today}T08:00:00\tespresso\t63\n"
    )

    totals = data.get_daily_totals(7)
    # Should have 2 days with data
    assert len(totals) >= 2
    # Check yesterday total
    yesterday_entry = next((d for d in totals if d[0] == yesterday), None)
    assert yesterday_entry is not None
    assert yesterday_entry[1] == 158  # 63 + 95


def test_get_daily_totals_empty() -> None:
    """Test daily totals with no data."""
    with patch("src.data.get_all_entries", return_value=[]):
        totals = data.get_daily_totals(7)
        assert totals == []
```

**New Test File: tests/test_graph.py**
```python
"""Tests for graph module."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

from src import graph


def test_render_graph_with_data() -> None:
    """Test graph rendering with data."""
    daily_totals = [
        ("2025-12-26", 158),
        ("2025-12-27", 126),
    ]

    with patch("src.graph.plt") as mock_plt:
        graph.render_graph(daily_totals)

        mock_plt.clear_figure.assert_called_once()
        mock_plt.bar.assert_called_once()
        mock_plt.title.assert_called_with("Daily Caffeine Intake")
        mock_plt.xlabel.assert_called_with("Date")
        mock_plt.ylabel.assert_called_with("Caffeine (mg)")
        mock_plt.show.assert_called_once()


def test_render_graph_empty() -> None:
    """Test graph rendering with no data."""
    with patch("src.graph.plt") as mock_plt:
        graph.render_graph([])

        # Should not call any plotext functions
        mock_plt.bar.assert_not_called()
        mock_plt.show.assert_not_called()


def test_render_graph_date_formatting() -> None:
    """Test date formatting in graph."""
    daily_totals = [
        ("2025-12-27", 100),
    ]

    with patch("src.graph.plt") as mock_plt:
        graph.render_graph(daily_totals)

        # Verify dates are formatted as MM-DD
        call_args = mock_plt.bar.call_args
        dates = call_args[0][0]
        assert dates == ["12-27"]
```

**New CLI Tests in tests/test_cli.py:**
```python
def test_graph_with_data(cli_runner, tmp_data_dir) -> None:
    """Test graph command with data."""
    # Setup multi-day data
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    today = datetime.now().date().isoformat()

    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
        f"{today}T08:00:00\tcoffee\t95\n"
    )

    with patch("src.graph.plt"):  # Mock plotext to avoid terminal output
        result = cli_runner.invoke(app, ["graph"])
        assert result.exit_code == 0


def test_graph_no_data(cli_runner, tmp_data_dir) -> None:
    """Test graph command with no data."""
    result = cli_runner.invoke(app, ["graph"])
    assert result.exit_code == 0
    assert "No data to graph" in result.output


def test_graph_with_config(cli_runner, tmp_data_dir) -> None:
    """Test graph respects config file."""
    # Create config with custom days
    config_file = tmp_data_dir / "config.toml"
    config_file.write_text("[display]\ngraph_days = 30\n")

    # Create some data
    today = datetime.now().date().isoformat()
    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{today}T08:00:00\tespresso\t63\n"
    )

    with patch("src.graph.plt"):
        result = cli_runner.invoke(app, ["graph"])
        assert result.exit_code == 0
```

### Project Structure Notes

**New Files:**
- `src/graph.py` - Graph rendering with Plotext

**Modified Files:**
- `src/data.py` - Add config loading and get_daily_totals functions
- `src/cli.py` - Replace graph placeholder with real implementation
- `tests/test_data.py` - Add config and daily totals tests
- `tests/test_graph.py` - New test file for graph module
- `tests/test_cli.py` - Add graph command tests

**Architecture Alignment:**
- Follows flat `src/` module organization from architecture
- graph.py handles "Graph rendering with Plotext" per architecture
- CLI delegates to graph module per established patterns

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.1]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Framework Selection: Typer + Plotext]
- [Source: _bmad-output/project-context.md#CLI Framework (Typer)]
- [Plotext GitHub](https://github.com/piccolomo/plotext) - Latest version 5.3.2

### Critical Don'ts

- **DON'T** use `print()` - use `console.print()` for messages
- **DON'T** skip type hints - basedpyright strict mode is active
- **DON'T** break existing tests (68 currently passing)
- **DON'T** modify existing functions in data.py - add new ones
- **DON'T** use matplotlib - use Plotext for terminal graphs
- **DON'T** hardcode dates in tests - use datetime calculations

### Edge Cases to Handle

1. **No data at all** - Show friendly message, no error
2. **Only today's data** - Show single bar graph
3. **Missing config file** - Use default 14 days silently
4. **Invalid config values** - Use defaults (don't crash)
5. **Corrupted TSV rows** - Skip them (existing pattern)
6. **Days with no drinks** - Include as 0mg in date range

### Plotext API Reference

**Library Version:** 5.3.2 (latest as of Dec 2025)

**Key Functions Used:**
```python
import plotext as plt

# Clear previous plot state
plt.clear_figure()

# Create bar chart
plt.bar(labels, values)

# Set titles and labels
plt.title("Chart Title")
plt.xlabel("X Axis Label")
plt.ylabel("Y Axis Label")

# Render to terminal
plt.show()
```

**Date Formatting:**
- Input dates: ISO format "YYYY-MM-DD"
- Display format: "MM-DD" (for readability in terminal)
- Slice string: `date[5:]` converts "2025-12-27" to "12-27"

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
- All 84 tests pass (added 16 new tests: 9 data, 4 graph, 3 CLI)

### Completion Notes List

- Added `load_config()`, `get_graph_days()`, `get_all_entries()`, `get_daily_totals()` to `src/data.py`
- Created `src/graph.py` with `render_graph()` function using Plotext
- Updated `src/cli.py` graph command to display daily caffeine totals as a terminal bar chart
- Added 9 new tests to `tests/test_data.py` for config loading and daily totals
- Created `tests/test_graph.py` with 4 tests for graph rendering
- Added 4 new tests to `tests/test_cli.py` for graph command (replaced placeholder test)
- Updated `pyproject.toml` to disable missing type stub warnings for plotext (external library)
- All acceptance criteria verified:
  - AC #1: Graph displays daily caffeine totals with dates on x-axis, mg on y-axis
  - AC #2: Default 14 days shown when data available
  - AC #3: Config file `graph_days` setting is respected
  - AC #4: Default 14 days used when no config file exists (no error)
  - AC #5: Shows all available data when fewer days than configured range
- Quality gates: Ruff clean, basedpyright 0 errors, all 84 tests pass

### File List

**Files Created:**
- `src/graph.py` - Graph rendering module with Plotext bar chart

**Files Modified:**
- `src/data.py` - Added 4 new functions for config loading and daily totals
- `src/cli.py` - Replaced graph placeholder with full implementation
- `tests/test_data.py` - Added 9 new tests (config loading, daily totals)
- `tests/test_graph.py` - New test file with 4 tests
- `tests/test_cli.py` - Updated graph tests (4 tests, replaced placeholder)
- `pyproject.toml` - Added basedpyright config for plotext type stubs

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5 (code-review workflow)
**Date:** 2025-12-27

### Issues Found & Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| HIGH | `load_config()` didn't handle malformed TOML - would crash CLI | Added try/except for `tomllib.TOMLDecodeError`, returns empty dict on error |
| MEDIUM | `get_graph_days()` didn't validate graph_days is positive integer | Added validation: returns default 14 if value is not positive int |
| MEDIUM | `test_graph_with_config` was weak - didn't verify config value was used | Added mock assertion to verify `get_daily_totals(30)` called with config value |
| MEDIUM | No test for malformed config.toml handling | Added `test_load_config_malformed_toml` test |

### Files Modified During Review

- `src/data.py` - Added error handling for malformed TOML, added validation for graph_days
- `tests/test_data.py` - Added 4 new tests for edge cases (malformed TOML, negative/zero/string values)
- `tests/test_cli.py` - Strengthened `test_graph_with_config` to verify config value is used

### Quality Gates Post-Review

- Ruff: All checks passed
- basedpyright: 0 errors, 0 warnings
- pytest: 88 passed (was 84, added 4 new tests)

## Change Log

- 2025-12-27: Story 3.1 Progress Graph implemented - all acceptance criteria satisfied
- 2025-12-27: Code review completed - fixed 4 issues (1 high, 3 medium), added 4 tests

