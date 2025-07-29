# src/forge/core/utils.py
import subprocess
from typing import List, Tuple

def run_command(command: List[str], check=False) -> Tuple[bool, str, str]:
    """
    Executes a shell command and returns a tuple of (success, stdout, stderr).
    """
    try:
        process = subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return process.returncode == 0, process.stdout.strip(), process.stderr.strip()
    except FileNotFoundError:
        return False, "", f"Command '{command[0]}' not found."
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip(), e.stderr.strip()