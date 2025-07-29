# cli/commands/__init__.py
import os
import json
from pathlib import Path
import typer
import sys

API_URL = os.getenv("FORGEKIT_API_URL", "http://localhost:8000") # "https://coral-app-vdhjm.ondigitalocean.app"
CONFIG_PATH = Path.home() / ".forgekit" / "config.json"

def get_api_key() -> str:
    # 1. Try environment
    key = os.getenv("FORGEKIT_API_KEY")
    if key:
        return key

    # 2. Try global config
    config_path = os.path.join(Path.home(), ".forgekit", "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config.get("api_key", "")
        except Exception:
            pass

    return ""

def auth_headers():
    key = get_api_key()
    if not key:
        typer.secho("❌ Missing API key. Set FORGEKIT_API_KEY or create ~/.forgekit/config.json with 'api_key'.", fg=typer.colors.BRIGHT_RED)
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}

def check_config_exists(config_file: str):
    if not os.path.exists(config_file):
        typer.secho(f"❌ Missing {config_file}. Please create it first using forgekit initialize.", fg=typer.colors.BRIGHT_RED)
        sys.exit(1)


# This will raise an error if the API key is not set
auth_headers()  # Ensure headers are set up