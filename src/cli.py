"""Caffeine and sugar tracking CLI application."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(
    name="caf",
    help="Track your caffeine and sugar intake and visualize your reduction journey.",
    no_args_is_help=True,
)

console = Console(width=60)
err_console = Console(stderr=True, width=60)


@app.command()
def log(
    drink: str | None = typer.Argument(None, help="Name of the drink"),
    mg: int | None = typer.Option(None, "--mg", "-m", help="Caffeine amount in mg (required for unknown drinks)"),
    sugar: int | None = typer.Option(None, "--sugar", "-s", help="Sugar amount in grams"),
) -> None:
    """Log a caffeinated drink. Run without arguments to select interactively."""
    import questionary

    from src import log as log_module
    from src.drinks_db import DRINKS_DB

    # If no drink specified, show interactive selection
    selected_drink: str
    if drink is None:
        sorted_drinks = sorted(DRINKS_DB.items(), key=lambda x: x[1].caffeine_mg, reverse=True)
        choices = [f"{name} ({info.caffeine_mg}mg, {info.sugar_g}g sugar)" for name, info in sorted_drinks]

        selected = questionary.select(
            "Select a drink to log:",
            choices=choices,
        ).ask()

        if selected is None:
            # User cancelled (Ctrl+C)
            raise typer.Exit(0)

        # Extract drink name from selection (remove the " (XXmg, Xg sugar)" suffix)
        selected_drink = selected.rsplit(" (", 1)[0]
    else:
        selected_drink = drink

    try:
        drink_name, caffeine, sugar_g, total_caffeine, total_sugar = log_module.log_drink(
            selected_drink, mg=mg, sugar=sugar
        )
        console.print(
            f"[green]✓[/green] Logged: [bold]{drink_name}[/bold] "
            f"([cyan]{caffeine}mg[/cyan], [magenta]{sugar_g}g sugar[/magenta])"
        )
        console.print(
            f"  Today's total: [bold cyan]{total_caffeine}mg[/bold cyan], "
            f"[bold magenta]{total_sugar}g sugar[/bold magenta]"
        )
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from None


@app.command()
def drinks() -> None:
    """List all known drinks and their caffeine/sugar content."""
    from src.drinks_db import DRINKS_DB

    console.print("[bold]Known drinks:[/bold]\n")

    # Sort by caffeine content (highest first)
    sorted_drinks = sorted(DRINKS_DB.items(), key=lambda x: x[1].caffeine_mg, reverse=True)

    for drink, info in sorted_drinks:
        console.print(
            f"  {drink:<20} [cyan]{info.caffeine_mg:>3}mg[/cyan]  " f"[magenta]{info.sugar_g:>2}g sugar[/magenta]"
        )

    console.print(f"\n[dim]{len(DRINKS_DB)} drinks available[/dim]")


@app.command()
def status() -> None:
    """Show today's caffeine and sugar intake summary."""
    from src import status as status_module

    entries, caffeine_total, sugar_total = status_module.get_status_data()

    console.print(
        f"[bold]Today:[/bold] [cyan]{caffeine_total}mg[/cyan] caffeine, " f"[magenta]{sugar_total}g[/magenta] sugar"
    )

    # Yesterday comparison (AC #1, #3)
    yesterday_diff = status_module.get_yesterday_comparison()
    if yesterday_diff is not None:
        caffeine_diff, sugar_diff = yesterday_diff
        caffeine_str = status_module.format_comparison(caffeine_diff)
        sugar_str = status_module.format_comparison(sugar_diff, "g")
        caffeine_color = "green" if caffeine_diff <= 0 else "yellow"
        sugar_color = "green" if sugar_diff <= 0 else "yellow"
        console.print(
            f"  [dim]vs yesterday:[/dim] [{caffeine_color}]{caffeine_str}[/{caffeine_color}] caffeine, "
            f"[{sugar_color}]{sugar_str}[/{sugar_color}] sugar"
        )

        # Same-time comparison (AC #2)
        same_time_diff = status_module.get_same_time_comparison()
        if same_time_diff is not None:
            caffeine_time_diff, sugar_time_diff = same_time_diff
            caffeine_time_str = status_module.format_comparison(caffeine_time_diff)
            sugar_time_str = status_module.format_comparison(sugar_time_diff, "g")
            caffeine_time_color = "green" if caffeine_time_diff <= 0 else "yellow"
            sugar_time_color = "green" if sugar_time_diff <= 0 else "yellow"
            console.print(
                f"  [dim]vs yesterday at this time:[/dim] "
                f"[{caffeine_time_color}]{caffeine_time_str}[/{caffeine_time_color}] caffeine, "
                f"[{sugar_time_color}]{sugar_time_str}[/{sugar_time_color}] sugar"
            )

    console.print()

    if not entries:
        console.print("[dim]No drinks logged today[/dim]")
        return

    for timestamp, drink, mg, sg in entries:
        time_str = status_module.format_time(timestamp)
        console.print(f"  [dim]{time_str}[/dim]  {drink:<20} [cyan]{mg}mg[/cyan]  [magenta]{sg}g sugar[/magenta]")


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
