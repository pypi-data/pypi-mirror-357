import typer
import os
import json

from app.commands.list_drivers import select_driver

def run():
    config_file_name = "forgekit.config.json"

    config_file = os.path.join(os.getcwd(), config_file_name)
    if os.path.exists(config_file):
        overwrite = typer.confirm(f"Config file '{config_file}' already exists. Overwrite?", default=False)
        if not overwrite:
            typer.echo("Initialization cancelled.")
            raise typer.Exit()

    driver = select_driver()

    with open(config_file, 'w') as f:
        json.dump({
            "name": "",
            "description": "",
            "references": [
                ""
            ],
            "driver": driver,
            "docs": ""
        }, f, indent=4)

    typer.echo(f"✅ Configuration file '{config_file}' created with driver '{driver}'.")
    typer.secho("Note: the docs key will automatically be added to the config file when you run 'forgekit create'. Use references for custom references", fg=typer.colors.YELLOW)
    typer.echo("You can now run 'forgekit create' to start your project.")