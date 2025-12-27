"""Caffeine tracking CLI application."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(
    name="caf",
    help="Track your caffeine intake and visualize your reduction journey.",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)


@app.command()
def log(
    drink: str = typer.Argument(..., help="Name of the drink"),
    mg: int | None = typer.Option(None, "--mg", "-m", help="Caffeine amount in mg (required for unknown drinks)"),
) -> None:
    """Log a caffeinated drink."""
    from src import log as log_module

    try:
        drink_name, caffeine, total = log_module.log_drink(drink, mg=mg)
        console.print(f"[green]✓[/green] Logged: [bold]{drink_name}[/bold] ([cyan]{caffeine}mg[/cyan])")
        console.print(f"  Today's total: [bold cyan]{total}mg[/bold cyan]")
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@app.command()
def drinks() -> None:
    """List all known drinks and their caffeine content."""
    from src.drinks_db import DRINKS_DB

    console.print("[bold]Known drinks:[/bold]\n")

    # Sort by caffeine content (highest first)
    sorted_drinks = sorted(DRINKS_DB.items(), key=lambda x: x[1], reverse=True)

    for drink, mg in sorted_drinks:
        console.print(f"  {drink:<20} [cyan]{mg:>3}mg[/cyan]")

    console.print(f"\n[dim]{len(DRINKS_DB)} drinks available[/dim]")


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
        yesterday_color = "green" if yesterday_diff <= 0 else "yellow"
        console.print(f"  [dim]vs yesterday:[/dim] [{yesterday_color}]{diff_str}[/{yesterday_color}]")

        # Same-time comparison (AC #2)
        same_time_diff = status_module.get_same_time_comparison()
        if same_time_diff is not None:
            same_time_str = status_module.format_comparison(same_time_diff)
            same_time_color = "green" if same_time_diff <= 0 else "yellow"
            console.print(
                f"  [dim]vs yesterday at this time:[/dim] [{same_time_color}]{same_time_str}[/{same_time_color}]"
            )

    console.print()

    if not entries:
        console.print("[dim]No drinks logged today[/dim]")
        return

    for timestamp, drink, mg in entries:
        time_str = status_module.format_time(timestamp)
        console.print(f"  [dim]{time_str}[/dim]  {drink:<20} [cyan]{mg}mg[/cyan]")


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


if __name__ == "__main__":
    app()
