"""Tests for data persistence module."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import src.data as data_module
from src.data import (
    append_drink,
    ensure_data_dir,
    get_daily_totals,
    get_graph_days,
    get_today_entries,
    get_today_total,
    get_yesterday_entries,
    get_yesterday_total,
    get_yesterday_total_by_time,
    load_config,
)


def test_ensure_data_dir_creates_directory(tmp_path: Path) -> None:
    """Test that ensure_data_dir creates the directory."""
    test_dir = tmp_path / "data"
    with patch.object(data_module, "DATA_DIR", test_dir):
        ensure_data_dir()
        assert test_dir.exists()
        assert test_dir.is_dir()


def test_append_drink_creates_file_with_header(tmp_path: Path) -> None:
    """Test that append_drink creates file with header on first write."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        append_drink("2025-12-27T08:00:00", "baly", 60, 27)

        assert test_file.exists()
        content = test_file.read_text()
        lines = content.strip().split("\n")

        # Check header
        assert lines[0] == "timestamp\tdrink\tcaffeine_mg\tsugar_g"
        # Check data row
        assert lines[1] == "2025-12-27T08:00:00\tbaly\t60\t27"


def test_append_drink_appends_without_header(tmp_path: Path) -> None:
    """Test that subsequent appends don't add another header."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        append_drink("2025-12-27T08:00:00", "baly", 60, 27)
        append_drink("2025-12-27T09:00:00", "red bull", 80, 27)

        content = test_file.read_text()
        lines = content.strip().split("\n")

        # Should have exactly 3 lines: header + 2 data rows
        assert len(lines) == 3
        assert lines[0] == "timestamp\tdrink\tcaffeine_mg\tsugar_g"
        assert lines[1] == "2025-12-27T08:00:00\tbaly\t60\t27"
        assert lines[2] == "2025-12-27T09:00:00\tred bull\t80\t27"


def test_get_today_entries_returns_todays_drinks(tmp_path: Path) -> None:
    """Test that get_today_entries returns only today's entries."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    today = datetime.now().date().isoformat()
    yesterday = "2020-01-01"  # Definitely not today

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        append_drink(f"{today}T08:00:00", "baly", 60, 27)
        append_drink(f"{yesterday}T08:00:00", "old_drink", 95, 30)
        append_drink(f"{today}T10:00:00", "red bull", 80, 27)

        entries = get_today_entries()

        assert len(entries) == 2
        assert entries[0] == (f"{today}T08:00:00", "baly", 60, 27)
        assert entries[1] == (f"{today}T10:00:00", "red bull", 80, 27)


def test_get_today_entries_empty_file(tmp_path: Path) -> None:
    """Test that get_today_entries handles non-existent file."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        entries = get_today_entries()
        assert entries == []


def test_get_today_total_calculates_sum(tmp_path: Path) -> None:
    """Test that get_today_total sums today's caffeine and sugar."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    today = datetime.now().date().isoformat()

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        append_drink(f"{today}T08:00:00", "baly", 60, 27)
        append_drink(f"{today}T10:00:00", "red bull", 80, 27)

        caffeine_total, sugar_total = get_today_total()
        assert caffeine_total == 140  # 60 + 80
        assert sugar_total == 54  # 27 + 27


def test_get_today_total_empty_returns_zero(tmp_path: Path) -> None:
    """Test that get_today_total returns (0, 0) for no entries."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        caffeine_total, sugar_total = get_today_total()
        assert caffeine_total == 0
        assert sugar_total == 0


def test_get_today_entries_skips_corrupted_rows(tmp_path: Path) -> None:
    """Test that corrupted rows with non-integer caffeine are skipped."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    today = datetime.now().date().isoformat()

    # Write file with a corrupted row
    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{today}T08:00:00\tespresso\t63\n"
        f"{today}T09:00:00\tcorrupted\tNOT_A_NUMBER\n"
        f"{today}T10:00:00\tcoffee\t95\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        entries = get_today_entries()

        # Should skip the corrupted row
        assert len(entries) == 2
        assert entries[0][1] == "espresso"
        assert entries[1][1] == "coffee"


def test_get_yesterday_entries(tmp_path: Path) -> None:
    """Test reading yesterday's entries."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    today = datetime.now().date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n" f"{yesterday}T08:00:00\tespresso\t63\n" f"{today}T09:00:00\tcoffee\t95\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        entries = get_yesterday_entries()
        assert len(entries) == 1
        assert entries[0][1] == "espresso"
        assert entries[0][2] == 63


def test_get_yesterday_entries_empty(tmp_path: Path) -> None:
    """Test yesterday entries when no data exists."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        entries = get_yesterday_entries()
        assert entries == []


def test_get_yesterday_total(tmp_path: Path) -> None:
    """Test yesterday's total caffeine and sugar."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n"
        f"{yesterday}T08:00:00\tbaly\t60\t27\n"
        f"{yesterday}T10:00:00\tred bull\t80\t27\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        caffeine_total, sugar_total = get_yesterday_total()
        assert caffeine_total == 140  # 60 + 80
        assert sugar_total == 54  # 27 + 27


def test_get_yesterday_total_by_time(tmp_path: Path) -> None:
    """Test yesterday total up to specific time."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n"
        f"{yesterday}T08:00:00\tbaly\t60\t27\n"
        f"{yesterday}T14:00:00\tred bull\t80\t27\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        # Before 10:00 should only include 8am drink
        caffeine_total, sugar_total = get_yesterday_total_by_time(10, 0)
        assert caffeine_total == 60
        assert sugar_total == 27

        # After 15:00 should include both
        caffeine_total, sugar_total = get_yesterday_total_by_time(15, 0)
        assert caffeine_total == 140
        assert sugar_total == 54


def test_get_yesterday_total_by_time_empty(tmp_path: Path) -> None:
    """Test yesterday total by time when no data."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        caffeine_total, sugar_total = get_yesterday_total_by_time(12, 0)
        assert caffeine_total == 0
        assert sugar_total == 0


# ============================================================================
# Config Loading Tests (Story 3.1)
# ============================================================================


def test_load_config_missing_file(tmp_path: Path) -> None:
    """Test config loading when file doesn't exist."""
    test_dir = tmp_path / "data"
    config_file = test_dir / "config.toml"

    with patch.object(data_module, "CONFIG_FILE", config_file):
        config = load_config()
        assert config == {}


def test_load_config_with_file(tmp_path: Path) -> None:
    """Test config loading from file."""
    test_dir = tmp_path / "data"
    test_dir.mkdir(parents=True)
    config_file = test_dir / "config.toml"
    config_file.write_text("[display]\ngraph_days = 30\n")

    with patch.object(data_module, "CONFIG_FILE", config_file):
        config = load_config()
        assert config["display"]["graph_days"] == 30


def test_get_graph_days_default() -> None:
    """Test default graph days when no config."""
    with patch.object(data_module, "load_config", return_value={}):
        assert get_graph_days() == 14


def test_get_graph_days_custom() -> None:
    """Test custom graph days from config."""
    with patch.object(data_module, "load_config", return_value={"display": {"graph_days": 30}}):
        assert get_graph_days() == 30


def test_get_graph_days_missing_display_section() -> None:
    """Test graph days when display section missing from config."""
    with patch.object(data_module, "load_config", return_value={"other": "stuff"}):
        assert get_graph_days() == 14


def test_load_config_malformed_toml(tmp_path: Path) -> None:
    """Test config loading gracefully handles malformed TOML."""
    test_dir = tmp_path / "data"
    test_dir.mkdir(parents=True)
    config_file = test_dir / "config.toml"
    config_file.write_text("this is not valid toml [[[")

    with patch.object(data_module, "CONFIG_FILE", config_file):
        config = load_config()
        assert config == {}  # Should return empty dict, not crash


def test_get_graph_days_negative_value() -> None:
    """Test graph days falls back to default for negative values."""
    with patch.object(data_module, "load_config", return_value={"display": {"graph_days": -5}}):
        assert get_graph_days() == 14  # Default


def test_get_graph_days_zero_value() -> None:
    """Test graph days falls back to default for zero."""
    with patch.object(data_module, "load_config", return_value={"display": {"graph_days": 0}}):
        assert get_graph_days() == 14  # Default


def test_get_graph_days_string_value() -> None:
    """Test graph days falls back to default for non-integer values."""
    with patch.object(data_module, "load_config", return_value={"display": {"graph_days": "thirty"}}):
        assert get_graph_days() == 14  # Default


# ============================================================================
# Daily Totals Tests (Story 3.1)
# ============================================================================


def test_get_daily_totals_aggregates_by_date(tmp_path: Path) -> None:
    """Test daily totals aggregation."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    today = datetime.now().date().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n"
        f"{yesterday}T08:00:00\tespresso\t63\n"
        f"{yesterday}T10:00:00\tcoffee\t95\n"
        f"{today}T08:00:00\tespresso\t63\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        totals = get_daily_totals(7)
        # Should have 2 days with data
        assert len(totals) >= 2
        # Check yesterday total (63 + 95 = 158)
        yesterday_entry = next((d for d in totals if d[0] == yesterday), None)
        assert yesterday_entry is not None
        assert yesterday_entry[1] == 158


def test_get_daily_totals_empty_no_file(tmp_path: Path) -> None:
    """Test daily totals with no data file."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        totals = get_daily_totals(7)
        assert totals == []


def test_get_daily_totals_single_day(tmp_path: Path) -> None:
    """Test daily totals with only one day of data."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    today = datetime.now().date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n"
        f"{today}T08:00:00\tbaly\t60\t27\n"
        f"{today}T10:00:00\tred bull\t80\t27\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        totals = get_daily_totals(14)
        assert len(totals) == 1
        assert totals[0] == (today, 140, 54)  # (date, caffeine, sugar)


def test_get_daily_totals_includes_zeros_for_gaps(tmp_path: Path) -> None:
    """Test that days with no drinks show 0mg."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    today = datetime.now().date().isoformat()
    two_days_ago = (datetime.now() - timedelta(days=2)).date().isoformat()

    # Gap: no data for yesterday
    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\n" f"{two_days_ago}T08:00:00\tespresso\t63\n" f"{today}T08:00:00\tcoffee\t95\n"
    )

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        totals = get_daily_totals(7)
        # Should have 3 days: two_days_ago, yesterday (0), today
        assert len(totals) == 3
        # Find yesterday's entry (should be 0)
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        yesterday_entry = next((d for d in totals if d[0] == yesterday), None)
        assert yesterday_entry is not None
        assert yesterday_entry[1] == 0
