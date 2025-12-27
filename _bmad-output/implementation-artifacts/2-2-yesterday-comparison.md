# Story 2.2: Yesterday Comparison

Status: done

## Story

As a **user**,
I want **to see how today's intake compares to yesterday**,
So that **I can see if I'm trending in the right direction**.

## Acceptance Criteria

1. **Given** the user runs `caf status`
   **When** there is data from yesterday
   **Then** they see a comparison: "vs yesterday: -45mg" or "+20mg"

2. **Given** the user runs `caf status` at 2pm
   **When** comparing to yesterday at the same time
   **Then** they see a same-time comparison: "vs yesterday at this time: -30mg"

3. **Given** there is no data from yesterday
   **When** the user runs `caf status`
   **Then** the comparison section is omitted (no "vs yesterday" shown)

## Tasks / Subtasks

- [x] Task 1: Add data layer functions for yesterday's data (AC: #1, #2, #3)
  - [x] 1.1: Add `get_yesterday_entries()` function to `src/data.py`
  - [x] 1.2: Add `get_yesterday_total()` function to `src/data.py`
  - [x] 1.3: Add `get_yesterday_total_by_time(hour: int, minute: int)` for same-time comparison
  - [x] 1.4: Add tests to `tests/test_data.py`

- [x] Task 2: Update status module with comparison logic (AC: #1, #2, #3)
  - [x] 2.1: Add `get_yesterday_comparison()` function to `src/status.py`
  - [x] 2.2: Add `get_same_time_comparison()` function for time-based comparison
  - [x] 2.3: Format comparison output with +/- sign
  - [x] 2.4: Handle missing yesterday data (return None)
  - [x] 2.5: Add tests to `tests/test_status.py`

- [x] Task 3: Update status CLI command (AC: #1, #2, #3)
  - [x] 3.1: Update status command to call comparison functions
  - [x] 3.2: Display "vs yesterday: +/-Xmg" when yesterday data exists
  - [x] 3.3: Display "vs yesterday at this time: +/-Xmg" for same-time comparison
  - [x] 3.4: Omit comparison section when no yesterday data
  - [x] 3.5: Add CLI tests to `tests/test_cli.py`

- [x] Task 4: Verify all acceptance criteria
  - [x] 4.1: Test with yesterday data - verify comparison displays
  - [x] 4.2: Test same-time comparison accuracy
  - [x] 4.3: Test without yesterday data - verify comparison is omitted

- [x] Task 5: Run all quality gates
  - [x] 5.1: Run `uv run ruff check src tests`
  - [x] 5.2: Run `uv run basedpyright`
  - [x] 5.3: Run `uv run pytest` - verify all tests pass

## Dev Notes

### Architecture Compliance

**Modules to Modify:**
- `src/data.py` - Add yesterday data retrieval functions
- `src/status.py` - Add comparison calculation logic (after Story 2.1 creates this)
- `src/cli.py` - Extend status command output

**Data Flow:**
```
User runs: caf status
     │
     ▼
cli.py calls status.get_status_data() [Story 2.1]
     │
     ▼
cli.py calls status.get_yesterday_comparison()
     │
     ├── data.get_yesterday_total() → yesterday_total
     │
     ├── data.get_today_total() → today_total
     │
     └── Returns comparison (today_total - yesterday_total) or None
     │
     ▼
cli.py calls status.get_same_time_comparison()
     │
     ├── data.get_yesterday_total_by_time() → yesterday_by_time
     │
     ├── data.get_today_total() → today_total
     │
     └── Returns same-time comparison or None
     │
     ▼
cli.py displays with Rich formatting
```

### Technical Requirements

**DEPENDENCY: This story depends on Story 2.1 being completed first** - It extends the status.py module and status CLI command created in 2.1.

**New Data Functions: src/data.py**
```python
from datetime import datetime, timedelta

def get_yesterday_date() -> str:
    """Get yesterday's date in ISO format (YYYY-MM-DD)."""
    yesterday = datetime.now().date() - timedelta(days=1)
    return yesterday.isoformat()


def get_yesterday_entries() -> list[tuple[str, str, int]]:
    """Read all entries from yesterday. Returns list of (timestamp, drink, mg)."""
    if not DRINKS_FILE.exists():
        return []

    yesterday = get_yesterday_date()
    entries: list[tuple[str, str, int]] = []

    with DRINKS_FILE.open() as f:
        header = next(f, None)
        if header is None:
            return []

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == TSV_COLUMNS and parts[0].startswith(yesterday):
                try:
                    caffeine_mg = int(parts[2])
                    entries.append((parts[0], parts[1], caffeine_mg))
                except ValueError:
                    continue

    return entries


def get_yesterday_total() -> int:
    """Calculate yesterday's total caffeine intake."""
    return sum(mg for _, _, mg in get_yesterday_entries())


def get_yesterday_total_by_time(hour: int, minute: int) -> int:
    """
    Calculate yesterday's caffeine total up to a specific time.

    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)

    Returns:
        Total caffeine consumed yesterday before the specified time
    """
    cutoff_time = f"{hour:02d}:{minute:02d}"
    total = 0

    for timestamp, _, mg in get_yesterday_entries():
        # Extract time from timestamp (HH:MM)
        if "T" in timestamp:
            time_part = timestamp.split("T")[1][:5]
            if time_part <= cutoff_time:
                total += mg

    return total
```

**Status Module Extensions: src/status.py**
```python
from datetime import datetime

from src import data


def get_yesterday_comparison() -> int | None:
    """
    Get comparison between today and yesterday's total.

    Returns:
        Difference (today - yesterday) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    today_total = data.get_today_total()
    yesterday_total = data.get_yesterday_total()

    return today_total - yesterday_total


def get_same_time_comparison() -> int | None:
    """
    Get comparison between today and yesterday at the same time.

    Returns:
        Difference (today - yesterday_by_time) or None if no yesterday data
    """
    yesterday_entries = data.get_yesterday_entries()
    if not yesterday_entries:
        return None

    now = datetime.now()
    today_total = data.get_today_total()
    yesterday_by_time = data.get_yesterday_total_by_time(now.hour, now.minute)

    return today_total - yesterday_by_time


def format_comparison(diff: int) -> str:
    """
    Format comparison difference with sign.

    Examples: "+45mg", "-30mg", "0mg"
    """
    if diff > 0:
        return f"+{diff}mg"
    elif diff < 0:
        return f"{diff}mg"
    else:
        return "0mg"
```

**CLI Output Pattern:**
```python
@app.command()
def status() -> None:
    """Show today's caffeine intake summary."""
    from src import status as status_module

    entries, total = status_module.get_status_data()

    console.print(f"[bold]Today:[/bold] [cyan]{total}mg[/cyan]")

    # Yesterday comparison (AC #1, #3)
    yesterday_diff = status_module.get_yesterday_comparison()
    if yesterday_diff is not None:
        diff_str = status_module.format_comparison(yesterday_diff)
        color = "green" if yesterday_diff <= 0 else "yellow"
        console.print(f"  [dim]vs yesterday:[/dim] [{color}]{diff_str}[/{color}]")

        # Same-time comparison (AC #2)
        same_time_diff = status_module.get_same_time_comparison()
        if same_time_diff is not None:
            same_time_str = status_module.format_comparison(same_time_diff)
            same_time_color = "green" if same_time_diff <= 0 else "yellow"
            console.print(f"  [dim]vs yesterday at this time:[/dim] [{same_time_color}]{same_time_str}[/{same_time_color}]")

    console.print()

    if not entries:
        console.print("[dim]No drinks logged today[/dim]")
        return

    for timestamp, drink, mg in entries:
        time_str = status_module.format_time(timestamp)
        console.print(f"  [dim]{time_str}[/dim]  {drink:<20} [cyan]{mg}mg[/cyan]")
```

**Output Format Examples:**

*With yesterday data (today less than yesterday):*
```
Today: 126mg
  vs yesterday: -63mg
  vs yesterday at this time: -45mg

  08:15  espresso             63mg
  10:30  coffee               63mg
```

*With yesterday data (today more than yesterday):*
```
Today: 252mg
  vs yesterday: +63mg
  vs yesterday at this time: +30mg

  08:15  espresso             63mg
  10:30  coffee               95mg
  14:00  energy drink         94mg
```

*No yesterday data:*
```
Today: 189mg

  08:15  espresso             63mg
  10:30  coffee               95mg
  14:00  green tea            31mg
```

### Previous Story Learnings (from Epic 1 + Story 2.1)

**CRITICAL - Apply These Patterns:**
1. **Rich console is set up** - Use `console.print()` for output
2. **Type hints required everywhere** - basedpyright strict mode
3. **Use `from __future__ import annotations`** for all modules
4. **Color conventions** - green for reduction (good), yellow for increase
5. **Lazy imports inside commands** - Prevents circular imports

**Code Quality Standards:**
- All tests must pass before marking complete
- Ruff, basedpyright must report 0 errors
- Don't break Story 2.1 functionality when extending

### Testing Requirements

**New Tests for tests/test_data.py:**
```python
def test_get_yesterday_entries(tmp_data_dir) -> None:
    """Test reading yesterday's entries."""
    # Setup: Write entries for yesterday and today
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    today = datetime.now().date().isoformat()

    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
        f"{today}T09:00:00\tcoffee\t95\n"
    )

    entries = data.get_yesterday_entries()
    assert len(entries) == 1
    assert entries[0][1] == "espresso"


def test_get_yesterday_total_by_time(tmp_data_dir) -> None:
    """Test yesterday total up to specific time."""
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
        f"{yesterday}T14:00:00\tcoffee\t95\n"
    )

    # Before 10:00 should only include 8am drink
    total = data.get_yesterday_total_by_time(10, 0)
    assert total == 63

    # After 15:00 should include both
    total = data.get_yesterday_total_by_time(15, 0)
    assert total == 158


def test_get_yesterday_entries_empty(tmp_data_dir) -> None:
    """Test yesterday entries when no data exists."""
    entries = data.get_yesterday_entries()
    assert entries == []
```

**New Tests for tests/test_status.py:**
```python
def test_get_yesterday_comparison_with_data() -> None:
    """Test yesterday comparison when data exists."""
    with patch("src.status.data.get_yesterday_entries", return_value=[("ts", "drink", 100)]):
        with patch("src.status.data.get_today_total", return_value=80):
            with patch("src.status.data.get_yesterday_total", return_value=100):
                diff = status.get_yesterday_comparison()
                assert diff == -20  # Reduced by 20mg


def test_get_yesterday_comparison_no_data() -> None:
    """Test yesterday comparison when no yesterday data."""
    with patch("src.status.data.get_yesterday_entries", return_value=[]):
        diff = status.get_yesterday_comparison()
        assert diff is None


def test_format_comparison() -> None:
    """Test comparison formatting."""
    assert status.format_comparison(45) == "+45mg"
    assert status.format_comparison(-30) == "-30mg"
    assert status.format_comparison(0) == "0mg"
```

**New CLI Tests in tests/test_cli.py:**
```python
def test_status_with_yesterday_data(cli_runner, tmp_data_dir) -> None:
    """Test status shows yesterday comparison."""
    # Setup yesterday data manually
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    drinks_file = tmp_data_dir / "drinks.tsv"
    drinks_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
    )

    # Log today's drink
    cli_runner.invoke(app, ["log", "espresso"])

    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "vs yesterday" in result.output


def test_status_without_yesterday_data(cli_runner, tmp_data_dir) -> None:
    """Test status omits comparison when no yesterday data."""
    cli_runner.invoke(app, ["log", "espresso"])

    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "vs yesterday" not in result.output
```

### Project Structure Notes

**Modified Files:**
- `src/data.py` - Add yesterday data functions
- `src/status.py` - Add comparison logic (extends Story 2.1)
- `src/cli.py` - Extend status command with comparisons
- `tests/test_data.py` - Add yesterday data tests
- `tests/test_status.py` - Add comparison tests (extends Story 2.1)
- `tests/test_cli.py` - Add comparison CLI tests

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2]
- [Source: _bmad-output/planning-artifacts/architecture.md#Module Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture]
- [Source: _bmad-output/implementation-artifacts/2-1-todays-status-summary.md]
- [Source: _bmad-output/project-context.md#CLI Framework (Typer)]

### Critical Don'ts

- **DON'T** break Story 2.1 functionality - this extends, not replaces
- **DON'T** use `print()` - use `console.print()`
- **DON'T** skip type hints - basedpyright strict mode is active
- **DON'T** break existing tests
- **DON'T** hardcode dates in tests - use datetime calculations

### Edge Cases to Handle

1. **No yesterday data** - Comparison section should be completely omitted (AC #3)
2. **First drink of the day** - Same-time comparison should work correctly
3. **Midnight boundary** - get_yesterday_date() handles timezone correctly
4. **Empty drink log** - Should handle gracefully (no comparison shown)

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
- All 68 tests pass (added 15 new tests: 5 data, 7 status, 3 CLI)

### Completion Notes List

- Added `get_yesterday_date()`, `get_yesterday_entries()`, `get_yesterday_total()`, `get_yesterday_total_by_time()` to `src/data.py`
- Added `get_yesterday_comparison()`, `get_same_time_comparison()`, `format_comparison()` to `src/status.py`
- Updated `src/cli.py` status command to display yesterday comparisons with color coding (green=reduction, yellow=increase)
- Added 5 new tests to `tests/test_data.py` for yesterday data functions
- Added 7 new tests to `tests/test_status.py` for comparison functions
- Added 3 new tests to `tests/test_cli.py` for comparison display
- All acceptance criteria verified:
  - AC #1: Shows "vs yesterday: -95mg" when yesterday data exists ✅
  - AC #2: Shows "vs yesterday at this time: 0mg" for same-time comparison ✅
  - AC #3: Comparison omitted when no yesterday data ✅
- Quality gates: Ruff clean, basedpyright 0 errors, all 68 tests pass

### File List

**Files Modified:**
- `src/data.py` - Added 4 new functions for yesterday data retrieval
- `src/status.py` - Added 3 new functions for comparison logic
- `src/cli.py` - Extended status command with comparison display
- `tests/test_data.py` - Added 5 new tests
- `tests/test_status.py` - Added 7 new tests
- `tests/test_cli.py` - Added 3 new tests

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5 (code-review workflow)
**Date:** 2025-12-27

### Issues Found & Fixed

| Severity | Issue | Resolution |
|----------|-------|------------|
| HIGH | `get_yesterday_comparison()` and `get_same_time_comparison()` each read TSV file 3 times | Fixed: calculate totals from cached entries, eliminated redundant file reads |
| MEDIUM | Variable `color` reassigned in status command (lines 64, 71) | Fixed: renamed to `yesterday_color` and `same_time_color` |
| MEDIUM | `test_status_with_yesterday_data` doesn't verify comparison value | Fixed: added assertion for "0mg" comparison |
| LOW | Line too long in cli.py (124 > 120 chars) | Fixed: wrapped console.print() call |

### Files Modified During Review

- `src/status.py` - Optimized comparison functions to avoid redundant file reads
- `src/cli.py` - Renamed color variables for clarity, fixed line length
- `tests/test_status.py` - Updated test to match optimized implementation
- `tests/test_cli.py` - Strengthened test assertion for yesterday comparison

### Quality Gates Post-Review

- Ruff: All checks passed
- basedpyright: 0 errors, 0 warnings
- pytest: 68 passed

## Change Log

- 2025-12-27: Story 2.2 Yesterday Comparison implemented - all acceptance criteria satisfied
- 2025-12-27: Code review completed - fixed 4 issues (1 high, 2 medium, 1 low)

