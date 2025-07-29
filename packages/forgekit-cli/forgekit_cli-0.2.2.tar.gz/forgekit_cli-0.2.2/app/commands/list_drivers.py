# cli/commands/list_drivers.py
import requests
import typer
from app.commands import API_URL, auth_headers
from rich.console import Console
from rich.table import Table

console = Console()

def run():
    try:
        resp = requests.get(f"{API_URL}/drivers", headers=auth_headers())
        resp.raise_for_status()

        table = Table(title="Available Drivers")
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")

        for idx, d in enumerate(resp.json(), start=1):
            table.add_row(str(idx), d['name'], d.get('description', 'No description available'))

        console.print(table)

        return resp.json()
    except Exception as e:
        typer.echo(f"❌ Failed to fetch drivers: {e}")

def select_driver():
    drivers = run()
    if not drivers:
        typer.echo("No drivers available.")
        raise typer.Exit()

    driver_names = [d['name'] for d in drivers]
    driver_choice = typer.prompt("Select a driver (enter associated number)")
    
    if not driver_choice.isdigit() or int(driver_choice) < 1 or int(driver_choice) > len(driver_names):
        typer.secho("Invalid choice. Please enter a valid number.", fg=typer.colors.BRIGHT_RED)
        select_driver()
    
    selected_driver = driver_names[int(driver_choice) - 1]
    typer.secho(f"You selected: {selected_driver}", fg=typer.colors.GREEN)
    return selected_driver