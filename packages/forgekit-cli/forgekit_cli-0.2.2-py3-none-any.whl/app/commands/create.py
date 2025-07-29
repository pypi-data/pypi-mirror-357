# cli/commands/create.py
import os
import json
import requests
import typer
from app.tools import create_file
from app.commands import API_URL, auth_headers, check_config_exists
import subprocess
import sys
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich.table import Table

console = Console()

def run(config_file: str = "forgekit.config.json"):
    check_config_exists(config_file)

    with open(config_file) as f:
        config = json.load(f)

    for key in ["name", "description", "driver", "references"]:
        if key not in config:
            typer.echo(f"❌ Missing required configuration: {key}")
            sys.exit(1)

    payload = {
        "project_name": config["name"],
        "project_description": config["description"],
        "driver": config["driver"],
        "references": config["references"],
    }

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("Generating files...", total=None)
        r = requests.post(f"{API_URL}/generate", json=payload, headers=auth_headers())
    
    r.raise_for_status()

    typer.echo("✅ Project files generated successfully. Now creating local files...")

    data = r.json()

    project_path = os.path.basename(os.getcwd())

    if "init" in data and data["init"]:
        subprocess.run(data["init"], shell=True, check=True)

    table = Table(title="Files to be created")
    table.add_column("Index", justify="right", style="magenta", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Path", style="magenta")
    table.add_column("Description", style="magenta", max_width=40)

    for idx, d in enumerate(data["files"], start=1):
        table.add_row(
            str(idx),
            d.get("path", "Unknown").split('/')[-1],
            os.path.join(project_path, d.get("path", "Unknown")),
            d.get("description", "No description available")
        )

    console.print(table)

    for file in data["files"]:
        path = os.path.join(project_path, file["path"])
        create_file(str(path), file["content"], meta={
            "description": file["description"],
        })

    typer.echo("📂 Project files created successfully.")

    create_file(os.path.join(project_path, "README.md"), data["readme"])

    typer.echo("📄 README.md created successfully.")

    if "docs" in data:
        config["docs"] = data["docs"]

        with open(os.path.join(project_path, config_file), 'w') as f:
            json.dump(config, f, indent=4)

    typer.echo("✅ Project created.")
 
    if "start" in data:
        typer.echo("You can now run the following command to start your project:")
        typer.secho(f"  {data['start']}", fg=typer.colors.GREEN)
