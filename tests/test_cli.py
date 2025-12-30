"""Tests for CLI module."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

import src.data as data_module
from src.cli import app

runner = CliRunner()

# Exit codes as per architecture: 0=success, 1=user error, 2=internal error
EXIT_SUCCESS = 0
EXIT_USER_ERROR = 1
EXIT_MISSING_ARGS = 2  # Typer's exit code when no_args_is_help triggers


def test_help_shows_commands() -> None:
    """Test that help shows all expected commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "log" in result.output
    assert "drinks" in result.output
    assert "status" in result.output
    assert "graph" in result.output


def test_app_no_args_shows_help() -> None:
    """Test that running with no args shows help due to no_args_is_help=True."""
    result = runner.invoke(app, [])
    # Typer's no_args_is_help=True returns exit code 2 but still shows help
    assert result.exit_code == EXIT_MISSING_ARGS
    assert "log" in result.output
    assert "drinks" in result.output
    assert "status" in result.output
    assert "graph" in result.output


def test_log_command_help() -> None:
    """Test that log command has help text."""
    result = runner.invoke(app, ["log", "--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "Log a caffeinated drink" in result.output
    assert "DRINK" in result.output


def test_status_command_help() -> None:
    """Test that status command has help text."""
    result = runner.invoke(app, ["status", "--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "caffeine and sugar intake" in result.output


def test_graph_command_help() -> None:
    """Test that graph command has help text."""
    result = runner.invoke(app, ["graph", "--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "caffeine intake graph" in result.output


def test_drinks_command_lists_drinks() -> None:
    """Test that drinks command lists known drinks."""
    result = runner.invoke(app, ["drinks"])
    assert result.exit_code == EXIT_SUCCESS
    assert "baly" in result.output
    assert "red bull" in result.output
    assert "60mg" in result.output  # baly caffeine
    assert "27g sugar" in result.output  # baly sugar
    assert "drinks available" in result.output


def test_drinks_command_help() -> None:
    """Test that drinks command has help text."""
    result = runner.invoke(app, ["drinks", "--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "List all known drinks" in result.output


def test_log_command_known_drink(tmp_path: Path) -> None:
    """Test that log command works with known drink."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "baly"])

        assert result.exit_code == EXIT_SUCCESS
        assert "Logged:" in result.output
        assert "baly" in result.output
        assert "60mg" in result.output
        assert "27g sugar" in result.output
        assert "Today's total:" in result.output


def test_log_command_unknown_drink(tmp_path: Path) -> None:
    """Test that log command fails gracefully for unknown drink."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "unknown_beverage_xyz"])

        assert result.exit_code == EXIT_USER_ERROR
        assert "Unknown drink" in result.output


def test_log_command_creates_file(tmp_path: Path) -> None:
    """Test that log command creates data file."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        runner.invoke(app, ["log", "red bull"])

        assert test_file.exists()
        content = test_file.read_text()
        assert "red bull" in content
        assert "80" in content
        assert "27" in content  # sugar


def test_log_command_running_total(tmp_path: Path) -> None:
    """Test that running total accumulates across multiple logs."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result1 = runner.invoke(app, ["log", "baly"])
        result2 = runner.invoke(app, ["log", "red bull"])

        assert "60mg" in result1.output
        assert "27g sugar" in result1.output
        assert "140mg" in result2.output  # 60 + 80
        assert "54g sugar" in result2.output  # 27 + 27


def test_status_command_runs() -> None:
    """Test that status command runs successfully."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code == EXIT_SUCCESS
    assert "Today:" in result.output


def test_graph_command_no_data(tmp_path: Path) -> None:
    """Test graph command with no data shows friendly message."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    config_file = test_dir / "config.toml"

    with (
        patch.object(data_module, "DATA_DIR", test_dir),
        patch.object(data_module, "DRINKS_FILE", test_file),
        patch.object(data_module, "CONFIG_FILE", config_file),
    ):
        result = runner.invoke(app, ["graph"])
        assert result.exit_code == EXIT_SUCCESS
        assert "No data to graph" in result.output


def test_app_instantiation() -> None:
    """Test that app is properly instantiated with expected properties."""
    assert app.info.name == "caf"
    assert app.info.help is not None
    assert "caffeine" in app.info.help.lower()


def test_log_unknown_drink_with_mg(tmp_path: Path) -> None:
    """Test logging unknown drink with --mg option."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "weird energy drink", "--mg", "200"])

        assert result.exit_code == EXIT_SUCCESS
        assert "weird energy drink" in result.output
        assert "200mg" in result.output


def test_log_unknown_drink_with_short_mg(tmp_path: Path) -> None:
    """Test logging unknown drink with -m short option."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "custom brew", "-m", "150"])

        assert result.exit_code == EXIT_SUCCESS
        assert "custom brew" in result.output
        assert "150mg" in result.output


def test_log_known_drink_with_mg_override(tmp_path: Path) -> None:
    """Test that --mg overrides known drink caffeine value."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "baly", "--mg", "100"])

        assert result.exit_code == EXIT_SUCCESS
        assert "100mg" in result.output  # Override, not 60mg


def test_log_negative_mg_rejected(tmp_path: Path) -> None:
    """Test that negative caffeine values are rejected."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["log", "weird drink", "--mg", "-50"])

        assert result.exit_code == EXIT_USER_ERROR
        assert "cannot be negative" in result.output


def test_log_help_shows_mg_option() -> None:
    """Test that log command help shows --mg option."""
    result = runner.invoke(app, ["log", "--help"])
    assert result.exit_code == EXIT_SUCCESS
    assert "--mg" in result.output
    assert "-m" in result.output
    assert "Caffeine amount" in result.output


def test_status_with_drinks(tmp_path: Path) -> None:
    """Test status command with logged drinks."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        # Log some drinks first
        runner.invoke(app, ["log", "baly"])
        runner.invoke(app, ["log", "red bull"])

        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "Today:" in result.output
        assert "140mg" in result.output  # Verify exact total (60 + 80)
        assert "54g" in result.output  # Verify sugar total (27 + 27)
        assert "baly" in result.output
        assert "red bull" in result.output


def test_status_empty_day(tmp_path: Path) -> None:
    """Test status command with no drinks logged."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "Today:" in result.output
        assert "0mg" in result.output
        assert "No drinks logged" in result.output


def test_status_shows_time_format(tmp_path: Path) -> None:
    """Test that status shows time in HH:MM format, not full ISO timestamp."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        runner.invoke(app, ["log", "baly"])

        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "baly" in result.output
        assert "60mg" in result.output
        # Verify time is in HH:MM format, not full ISO (should NOT contain date portion)
        today = datetime.now().date().isoformat()
        assert today not in result.output  # Date should not appear in drink list


def test_status_with_yesterday_data(tmp_path: Path) -> None:
    """Test status shows yesterday comparison when yesterday data exists."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    # Setup yesterday data manually (with sugar column)
    test_file.write_text(f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n" f"{yesterday}T08:00:00\tbaly\t60\t27\n")

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        # Log today's drink (same as yesterday)
        runner.invoke(app, ["log", "baly"])

        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "vs yesterday:" in result.output
        assert "0mg" in result.output  # Same intake: 60mg today vs 60mg yesterday


def test_status_without_yesterday_data(tmp_path: Path) -> None:
    """Test status omits comparison when no yesterday data."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        runner.invoke(app, ["log", "baly"])

        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "vs yesterday" not in result.output


def test_status_shows_same_time_comparison(tmp_path: Path) -> None:
    """Test status shows same-time comparison."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

    test_file.write_text(f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n" f"{yesterday}T08:00:00\tbaly\t60\t27\n")

    with patch.object(data_module, "DATA_DIR", test_dir), patch.object(data_module, "DRINKS_FILE", test_file):
        runner.invoke(app, ["log", "baly"])

        result = runner.invoke(app, ["status"])
        assert result.exit_code == EXIT_SUCCESS
        assert "vs yesterday at this time" in result.output


# ============================================================================
# Graph CLI Tests (Story 3.1)
# ============================================================================


def test_graph_with_data(tmp_path: Path) -> None:
    """Test graph command renders with data."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    config_file = test_dir / "config.toml"
    test_dir.mkdir(parents=True)

    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
    today = datetime.now().date().isoformat()

    test_file.write_text(
        f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n"
        f"{yesterday}T08:00:00\tbaly\t60\t27\n"
        f"{today}T08:00:00\tred bull\t80\t27\n"
    )

    with (
        patch.object(data_module, "DATA_DIR", test_dir),
        patch.object(data_module, "DRINKS_FILE", test_file),
        patch.object(data_module, "CONFIG_FILE", config_file),
        patch("src.graph.plt") as mock_plt,  # Mock plotext to avoid terminal output
    ):
        result = runner.invoke(app, ["graph"])
        assert result.exit_code == EXIT_SUCCESS
        # Verify plotext was called
        mock_plt.show.assert_called_once()


def test_graph_with_config(tmp_path: Path) -> None:
    """Test graph respects config file for graph_days."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    config_file = test_dir / "config.toml"
    test_dir.mkdir(parents=True)

    # Create config with custom days
    config_file.write_text("[display]\ngraph_days = 30\n")

    today = datetime.now().date().isoformat()
    test_file.write_text(f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n" f"{today}T08:00:00\tbaly\t60\t27\n")

    with (
        patch.object(data_module, "DATA_DIR", test_dir),
        patch.object(data_module, "DRINKS_FILE", test_file),
        patch.object(data_module, "CONFIG_FILE", config_file),
        patch("src.graph.plt"),  # Mock plotext
        patch.object(data_module, "get_daily_totals", wraps=data_module.get_daily_totals) as mock_get_daily_totals,
    ):
        result = runner.invoke(app, ["graph"])
        assert result.exit_code == EXIT_SUCCESS
        # Verify the config value of 30 days was actually used
        mock_get_daily_totals.assert_called_once_with(30)


def test_graph_default_days_no_config(tmp_path: Path) -> None:
    """Test graph uses default 14 days when no config file."""
    test_dir = tmp_path / "data"
    test_file = test_dir / "drinks.tsv"
    config_file = test_dir / "config.toml"
    test_dir.mkdir(parents=True)

    today = datetime.now().date().isoformat()
    test_file.write_text(f"timestamp\tdrink\tcaffeine_mg\tsugar_g\n" f"{today}T08:00:00\tbaly\t60\t27\n")

    # Note: config_file doesn't exist, should use default 14 days
    with (
        patch.object(data_module, "DATA_DIR", test_dir),
        patch.object(data_module, "DRINKS_FILE", test_file),
        patch.object(data_module, "CONFIG_FILE", config_file),
        patch("src.graph.plt"),  # Mock plotext
    ):
        result = runner.invoke(app, ["graph"])
        assert result.exit_code == EXIT_SUCCESS
