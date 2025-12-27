---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
status: complete
completedAt: '2025-12-27'
---

# coffeine-reduction - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for coffeine-reduction, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

- FR1: User can log a caffeinated drink by name
- FR2: User can log a drink with a custom caffeine amount (mg)
- FR3: System can look up caffeine content for known drinks automatically
- FR4: User can log drinks at any time (defaults to current time)
- FR5: User can see confirmation after logging a drink
- FR6: User can view today's total caffeine consumption
- FR7: User can view a list of all drinks logged today
- FR8: User can see how today compares to yesterday (total)
- FR9: User can see how today compares to yesterday at the same time of day
- FR10: User can view a graph of daily caffeine totals over time
- FR11: User can view trends spanning multiple weeks
- FR12: Graph displays in the terminal with clear visual formatting
- FR13: System persists all logged drinks between sessions
- FR14: User can inspect the drink log data file directly
- FR15: System protects data integrity (no corruption on crashes)
- FR16: System stores configuration in a config file
- FR17: System includes a built-in database of common drinks and their caffeine content
- FR18: User can log drinks not in the database by providing caffeine amount

### NonFunctional Requirements

- NFR1: All commands complete and display output within 1 second
- NFR2: Graph rendering completes within 2 seconds even with months of data
- NFR3: Drink log data is never lost due to application crashes
- NFR4: Data file remains valid and readable after unexpected termination
- NFR5: Application handles corrupted config gracefully (falls back to defaults)
- NFR6: Terminal output is readable in both light and dark terminal themes
- NFR7: Commands work without requiring manual configuration after install

### Additional Requirements

**From Architecture:**

- Technology Stack: Python 3.13, Typer (CLI framework), Plotext (terminal graphs), Rich (formatting)
- Data Format: TSV for drink log (append-only), TOML for config
- Data Location: `./data/` directory (git-versioned, portable)
- Entry Point: `caf` command via `[project.scripts]` in pyproject.toml
- Package Manager: uv with `uv run caf` for development
- Module Structure: Flat `src/` organization with 6 modules (cli.py, log.py, status.py, graph.py, data.py, drinks_db.py)
- Crash Safety: Append-only log file pattern
- Naming Conventions: PEP 8 throughout, ISO 8601 for timestamps
- Error Handling: Use Typer's error handling with exit codes (0=success, 1=user error, 2=internal error)

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | Log drink by name |
| FR2 | Epic 1 | Log with custom caffeine amount |
| FR3 | Epic 1 | Auto-lookup caffeine for known drinks |
| FR4 | Epic 1 | Log defaults to current time |
| FR5 | Epic 1 | Confirmation after logging |
| FR6 | Epic 2 | View today's total |
| FR7 | Epic 2 | View today's drink list |
| FR8 | Epic 2 | Compare to yesterday (total) |
| FR9 | Epic 2 | Compare to yesterday (same time) |
| FR10 | Epic 3 | Graph of daily totals |
| FR11 | Epic 3 | Multi-week trends |
| FR12 | Epic 3 | Terminal graph formatting |
| FR13 | Epic 1 | Persist drinks between sessions |
| FR14 | Epic 1 | Inspectable data file |
| FR15 | Epic 1 | Data integrity protection |
| FR16 | Epic 3 | Config file storage |
| FR17 | Epic 1 | Built-in drink database |
| FR18 | Epic 1 | Log unknown drinks with manual mg |

## Epic List

### Epic 1: Log Drinks with Confidence

User can log any caffeinated drink and trust it's saved reliably.

**What users can do after this epic:**
- Run `caf log espresso` and see confirmation
- Log drinks with auto-calculated caffeine (from built-in database)
- Log custom drinks with manual caffeine amounts
- Trust that data is safely persisted to an inspectable file

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR13, FR14, FR15, FR17, FR18

### Epic 2: Track Today's Intake

User can see today's caffeine summary and compare to yesterday.

**What users can do after this epic:**
- Run `caf status` to see today's total and drink list
- See comparison to yesterday (total and same-time-of-day)
- Quick awareness of daily consumption

**FRs covered:** FR6, FR7, FR8, FR9

### Epic 3: Visualize Your Journey

User can see their progress toward caffeine reduction over weeks.

**What users can do after this epic:**
- Run `caf graph` to see weekly/multi-week trend visualization
- Clear terminal graph showing downward (or upward) trends
- Configure display preferences via config file

**FRs covered:** FR10, FR11, FR12, FR16

---

## Epic 1: Log Drinks with Confidence

User can log any caffeinated drink and trust it's saved reliably.

### Story 1.1: CLI Foundation

As a **user**,
I want **to run `caf` and see helpful information about available commands**,
So that **I know the tool is installed correctly and can discover how to use it**.

**Acceptance Criteria:**

**Given** the user has installed the package
**When** they run `caf` or `caf --help`
**Then** they see a help message listing available commands (log, status, graph)

**Given** the package is installed via `uv`
**When** the user runs `uv run caf`
**Then** the CLI executes successfully

---

### Story 1.2: Log Known Drinks

As a **user**,
I want **to log a caffeinated drink by name and have its caffeine content looked up automatically**,
So that **I can track my intake without manually knowing caffeine amounts**.

**Acceptance Criteria:**

**Given** the user runs `caf log espresso`
**When** "espresso" is in the built-in drink database
**Then** the drink is saved to `./data/drinks.tsv` with timestamp and caffeine amount
**And** a confirmation message displays: drink name, caffeine mg, and today's running total

**Given** no `./data/` directory exists
**When** the user logs their first drink
**Then** the directory and file are created automatically

---

### Story 1.3: Log Unknown Drinks with Custom Caffeine

As a **user**,
I want **to log drinks not in the database by specifying the caffeine amount manually**,
So that **I can track any caffeinated drink**.

**Acceptance Criteria:**

**Given** the user runs `caf log "weird energy drink" --mg 200`
**When** the drink is not in the database
**Then** the drink is saved with 200mg and confirmation displays

**Given** the user runs `caf log "unknown drink"` without --mg
**When** the drink is not in the database
**Then** an error message prompts to use --mg

**Given** the user runs `caf log espresso --mg 100`
**When** --mg is provided for a known drink
**Then** the specified amount overrides the database value (for different serving sizes)

---

## Epic 2: Track Today's Intake

User can see today's caffeine summary and compare to yesterday.

### Story 2.1: Today's Status Summary

As a **user**,
I want **to see today's total caffeine intake and a list of drinks I've logged**,
So that **I can track my daily consumption at a glance**.

**Acceptance Criteria:**

**Given** the user has logged drinks today
**When** they run `caf status`
**Then** they see today's total caffeine (e.g., "Today: 189mg")
**And** a list of drinks logged today with times and amounts

**Given** the user has not logged any drinks today
**When** they run `caf status`
**Then** they see "Today: 0mg" and a message like "No drinks logged today"

---

### Story 2.2: Yesterday Comparison

As a **user**,
I want **to see how today's intake compares to yesterday**,
So that **I can see if I'm trending in the right direction**.

**Acceptance Criteria:**

**Given** the user runs `caf status`
**When** there is data from yesterday
**Then** they see a comparison: "vs yesterday: -45mg" or "+20mg"

**Given** the user runs `caf status` at 2pm
**When** comparing to yesterday at the same time
**Then** they see a same-time comparison: "vs yesterday at this time: -30mg"

**Given** there is no data from yesterday
**When** the user runs `caf status`
**Then** the comparison section is omitted (no "vs yesterday" shown)

---

## Epic 3: Visualize Your Journey

User can see their progress toward caffeine reduction over weeks.

### Story 3.1: Progress Graph

As a **user**,
I want **to see a graph of my daily caffeine totals over time**,
So that **I can visualize my progress toward reducing consumption**.

**Acceptance Criteria:**

**Given** the user has logged drinks over multiple days
**When** they run `caf graph`
**Then** a terminal graph displays daily caffeine totals
**And** the x-axis shows dates, y-axis shows mg

**Given** the user runs `caf graph`
**When** there are 14+ days of data
**Then** the graph shows the most recent 14 days by default

**Given** a config file exists at `./data/config.toml` with `graph_days = 30`
**When** the user runs `caf graph`
**Then** the graph shows 30 days instead of the default 14

**Given** no config file exists
**When** the user runs `caf graph`
**Then** the default of 14 days is used (no error)

**Given** the user has fewer days of data than the configured range
**When** they run `caf graph`
**Then** the graph shows all available data
