---
stepsCompleted: [1, 2, 3, 4, 7, 8, 9, 10, 11]
inputDocuments:
  - '_bmad-output/analysis/brainstorming-session-2025-12-27.md'
workflowType: 'prd'
lastStep: 0
briefCount: 0
researchCount: 0
brainstormingCount: 1
projectDocsCount: 0
---

# Product Requirements Document - coffeine-reduction

**Author:** Pauloschreiner
**Date:** 2025-12-27

## Executive Summary

A personal CLI tool for tracking and reducing caffeine consumption to zero. The app makes it effortless to log caffeinated drinks, estimates current caffeine in your system using pharmacokinetic half-life decay (~5-6 hours), and visualizes progress over time.

The core motivation isn't just "less caffeine" - it's regaining the freedom to be productive without chemical dependency.

### What Makes This Special

**Effortless logging** - The primary differentiator is ease of use, not speed. Logging a drink should feel natural and require minimal cognitive effort, ensuring consistent tracking even when busy or tired.

**Body awareness** - Real-time estimation of caffeine currently in your system, helping you understand your actual dependency state rather than just consumption totals.

**Progress visibility** - Long-term visualization of the journey toward zero, providing motivation through visible trends.

## Project Classification

**Technical Type:** CLI Tool
**Domain:** General (personal wellness/productivity)
**Complexity:** Low
**Project Context:** Greenfield - new project

This is a personal-use terminal application with a focus on pleasant visual presentation. No multi-user, compliance, or external integration requirements.

## Success Criteria

### User Success

- **Primary success indicator:** Seeing a clear downward trend in caffeine consumption over weeks
- **Consistent logging:** Actually remembering to log every drink without friction
- **Progress awareness:** Understanding consumption patterns through visualization
- Reaching zero caffeine is a bonus milestone, not a requirement for success

### Technical Success

- Logging feels effortless - minimal keystrokes, intuitive commands
- CLI renders nicely with pleasant visual presentation
- Data persists reliably between sessions
- Graph renders clearly in terminal

### Measurable Outcomes

- Can log a drink with minimal cognitive effort
- Weekly trend is visible and understandable at a glance
- Tool is used consistently (doesn't get abandoned due to friction)

## Product Scope

### MVP - Minimum Viable Product

- **Easy drink logging:** Name/description + quantity → auto-calculate caffeine mg
- **Daily consumption view:** Today's total + list of drinks logged
- **Progress over time:** Graph showing daily totals trending over weeks

### Growth Features (Post-MVP)

- Body caffeine estimate (real-time using half-life decay)
- Withdrawal prediction (when you'll feel the dip)
- Sugar tracking (coupled consumption)
- Clean streak counter

### Vision (Future)

- To be determined based on actual usage patterns

## User Journeys

### Journey 1: Morning Coffee Logging

It's 8:15 AM. You just made your usual morning espresso. Without thinking much about it, you open the terminal and type `caf log espresso`. The CLI responds with a brief confirmation showing today's running total. Done in seconds - you're back to your morning routine.

Throughout the day, this happens a few more times: `caf log "green tea"` after lunch, `caf log cola` in the afternoon. Each time, minimal friction - just the drink name and you're done.

### Journey 2: End-of-Day Status Check

Before winding down for the evening, you're curious how today went. You type `caf status` and see a clean summary: today's total caffeine intake, a list of what you logged, and maybe a note about how it compares to yesterday. A quick glance tells you whether you're trending in the right direction.

### Journey 3: Weekly Progress Review

It's Sunday. You want to see if your reduction efforts are paying off. You type `caf graph` and a visual chart renders in your terminal - daily totals over the past few weeks. The downward trend is visible. That's the moment of satisfaction: proof that the small daily choices are adding up.

### Journey 4: First-Time Setup

You've just installed the tool. You run `caf` for the first time. It either works immediately with sensible defaults, or asks one or two quick questions (like preferred units). No lengthy onboarding - you're ready to log your first drink within a minute.

### Journey Requirements Summary

These journeys reveal the following capabilities needed:

- **Logging command**: Simple syntax like `caf log <drink>` with auto-calculation of caffeine mg
- **Status command**: Show today's summary (total, list, comparison)
- **Graph command**: Render weekly/monthly trend visualization in terminal
- **Drink database**: Built-in lookup for common drinks and their caffeine content
- **Data persistence**: Store logs locally for history and graphing
- **Pleasant CLI output**: Readable, visually appealing terminal formatting

## CLI Tool Specific Requirements

### Project-Type Overview

coffeine-reduction is an interactive CLI tool designed for personal daily use. The focus is on pleasant terminal interaction rather than scripting or automation.

### Command Structure

- **Primary commands:**
  - `caf log <drink>` - Log a caffeinated drink
  - `caf status` - Show today's consumption summary
  - `caf graph` - Display progress visualization
- **Interactive usage pattern** - Designed for human interaction, not piping/scripting
- **Minimal flags** - Sensible defaults over complex options

### Output Formats

- **Pretty terminal output only** - Focus on readable, visually appealing display
- **No machine-readable format needed** - No JSON/CSV export required for MVP
- **Terminal graph rendering** - Progress visualization renders nicely in terminal

### Configuration & Data Storage

- **Config file approach** - Settings stored in config file (e.g., `~/.config/caf/config.toml` or similar)
- **Drink log file** - Special attention to the file storing consumption history
  - Must be human-readable and inspectable
  - Should handle data reliably (no corruption on crashes)
  - Consider simple format (CSV, TOML, or SQLite)
- **Caffeine database** - Built-in lookup table for common drinks and their caffeine content

### Implementation Considerations

- **Data integrity** - The drink log is the core data asset; protect it
- **Sensible defaults** - Works out of the box without configuration
- **Shell completion** - Nice-to-have for future (tab-complete drink names)

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP - solve the core problem with minimal features
**Resource Requirements:** Solo developer, personal project

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- Morning coffee logging (and throughout day)
- End-of-day status check
- Weekly progress review
- First-time setup

**Must-Have Capabilities:**
- `caf log <drink>` - Log drinks with auto-calculated caffeine mg
- `caf status` - Today's consumption summary
- `caf graph` - Weekly trend visualization
- Built-in drink database (common drinks + caffeine content)
- Local data persistence (reliable drink log storage)
- Pretty terminal output

### Post-MVP Features

**Phase 2 (Growth):**
- Body caffeine estimate (real-time half-life decay calculation)
- Withdrawal prediction (when you'll feel the dip)
- Sugar tracking (coupled consumption awareness)
- Clean streak counter
- Shell completion for drink names

**Phase 3 (If Needed):**
- To be determined based on actual usage patterns

### Risk Mitigation Strategy

**Technical Risks:** Low - straightforward CLI with local storage, no complex dependencies
**Market Risks:** N/A - personal tool, no market validation needed
**Resource Risks:** Minimal - solo project with clear, small scope

## Functional Requirements

### Drink Logging

- FR1: User can log a caffeinated drink by name
- FR2: User can log a drink with a custom caffeine amount (mg)
- FR3: System can look up caffeine content for known drinks automatically
- FR4: User can log drinks at any time (defaults to current time)
- FR5: User can see confirmation after logging a drink

### Consumption Status

- FR6: User can view today's total caffeine consumption
- FR7: User can view a list of all drinks logged today
- FR8: User can see how today compares to yesterday (total)
- FR9: User can see how today compares to yesterday at the same time of day

### Progress Visualization

- FR10: User can view a graph of daily caffeine totals over time
- FR11: User can view trends spanning multiple weeks
- FR12: Graph displays in the terminal with clear visual formatting

### Data Management

- FR13: System persists all logged drinks between sessions
- FR14: User can inspect the drink log data file directly
- FR15: System protects data integrity (no corruption on crashes)
- FR16: System stores configuration in a config file

### Drink Database

- FR17: System includes a built-in database of common drinks and their caffeine content
- FR18: User can log drinks not in the database by providing caffeine amount

## Non-Functional Requirements

### Performance

- NFR1: All commands complete and display output within 1 second
- NFR2: Graph rendering completes within 2 seconds even with months of data

### Reliability & Data Integrity

- NFR3: Drink log data is never lost due to application crashes
- NFR4: Data file remains valid and readable after unexpected termination
- NFR5: Application handles corrupted config gracefully (falls back to defaults)

### Usability

- NFR6: Terminal output is readable in both light and dark terminal themes
- NFR7: Commands work without requiring manual configuration after install
