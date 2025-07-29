# cli/commands/login.py
import typer
import requests
import json
from getpass import getpass

from app.commands import API_URL, CONFIG_PATH

def run():
    email = typer.prompt("Enter your email")
    password = getpass("Enter your password: ")

    try:
        response = requests.post(
            f"{API_URL}/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        typer.echo(f"❌ Login failed: {e}")
        raise typer.Exit(code=1)

    data = response.json()
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w") as f:
        json.dump({
            "api_key": data["api_key"]
        }, f, indent=2)

    typer.echo("✅ API key saved to ~/.forgekit/config.json")
