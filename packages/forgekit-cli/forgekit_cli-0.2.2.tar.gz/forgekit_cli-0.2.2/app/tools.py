import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

LOG_DIR = ".forgekit_logs"
os.makedirs(LOG_DIR, exist_ok=True)
    
def create_file(path: str, content: str, meta: dict = None):
    if content.strip().startswith("```"):
        content = "\n".join(content.strip().splitlines()[1:-1])

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

    # Log file input/output
    if meta:
        log_path = Path(LOG_DIR) / f"create_{p.name}_{int(datetime.now().timestamp())}.json"
        # Ensure the log directory exists before writing the log file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as f:
            json.dump({
                "path": path,
                "description": meta.get("description"),
                "model_input": meta.get("input"),
                "model_output": content,
                "timestamp": datetime.now().isoformat(),
                "tool": "create_file"
            }, f, indent=2)


def run_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()