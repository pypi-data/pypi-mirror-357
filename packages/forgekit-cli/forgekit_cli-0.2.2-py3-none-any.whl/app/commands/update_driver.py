from app.commands import check_config_exists
from app.commands.list_drivers import select_driver
import json
import typer

def run(config_file: str = "forgekit.config.json"):
    check_config_exists(config_file)

    current_driver = None

    with open(config_file) as f:
        config = json.load(f)

        if "driver" in config:
            current_driver = config["driver"]
            typer.echo(f"Current driver: {current_driver}")

    driver = select_driver()
    
    with open(config_file) as f:
        config = json.load(f)
        config["driver"] = driver
    
    typer.echo("✅ Driver updated successfully.")