# cli/commands/fix.py
import json
import requests
import typer
from app.commands import API_URL, auth_headers, check_config_exists

def run(config_file: str = "forgekit.config.json"):
    check_config_exists(config_file)

    with open(config_file) as f:
        config = json.load(f)

    file_path = typer.prompt("Enter path to file with error")
    with open(file_path) as f:
        original_content = f.read()

    error_output = typer.prompt("Paste the error message")

    docs = config.get("docs", "")

    payload = {
        "file_path": file_path,
        "original_content": original_content,
        "driver": config["driver"],
        "error_output": error_output,
        "docs": docs
    }

    r = requests.post(f"{API_URL}/fix", json=payload, headers=auth_headers())
    r.raise_for_status()
    result = r.json()

    if result.get("file_path"):
        with open(result["file_path"], "w") as f:
            f.write(result["content"])
        typer.echo(f"✅ Fixed file saved to {result['file_path']}")
    else:
        typer.echo("⚠️ No file path provided in response, content not saved to file.")