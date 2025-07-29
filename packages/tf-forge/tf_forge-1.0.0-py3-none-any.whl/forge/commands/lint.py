import subprocess
import typer
import shutil
import json
from typing import List, Tuple, Dict, Any

from ..app import app, console
from rich.table import Table
from rich.panel import Panel

from ..core.utils import run_command
from .docs import _merge_dicts
import pathlib
import hcl2

SECRET_KEYWORDS = ["password", "secret", "token", "api_key", "private_key"]

@app.command()
def lint():
    """
    Run a suite of self-contained checks on your Terraform code.
    """
    console.print("🕵️  Running local lint checks...")
    
    if not shutil.which("terraform"):
        console.print("[bold red]Error:[/bold red] 'terraform' command not found. Please install it to use the 'lint' command.")
        raise typer.Exit(code=1)
    
    console.print("\n[bold]--- Running Checks ---[/bold]")
    all_passed = True

    fmt_success, fmt_out, _ = run_command(["terraform", "fmt", "-check", "-recursive"])
    status_fmt = "[bold green]✔ OK[/bold green]" if fmt_success else "[bold red]❌ Needs formatting[/bold red]"
    console.print(f"1. Code Formatting: {status_fmt}")
    if not fmt_success:
        all_passed = False
        console.print(Panel(fmt_out, title="Files to format", border_style="yellow"))

    validate_success, _, validate_err = run_command(["terraform", "validate"])
    status_validate = "[bold green]✔ OK[/bold green]" if validate_success else "[bold red]❌ Validation Failed[/bold red]"
    console.print(f"2. Syntax Validation: {status_validate}")
    if not validate_success:
        all_passed = False
        console.print(Panel(validate_err, title="Validation Errors", border_style="red"))

    console.print("3. Custom Best Practice Checks:")
    custom_checks_passed = _run_custom_checks()
    if not custom_checks_passed:
        all_passed = False

    if all_passed:
        console.print("\n[bold green]🎉 All checks passed successfully![/bold green]")
    else:
        console.print("\n[bold yellow]⚠️ Some checks failed. Please review the output above.[/bold yellow]")
        raise typer.Exit(code=1)


def _run_custom_checks() -> bool:
    """Orchestrates the execution of all custom checks."""
    cwd = pathlib.Path.cwd()
    tf_files = list(cwd.glob("*.tf"))
    if not tf_files:
        return True

    all_data = {}
    try:
        parsed_data_list = []
        for tf_file in tf_files:
            with tf_file.open('r', encoding='utf-8') as f:
                parsed_data_list.append(hcl2.load(f))
        all_data = _merge_dicts(parsed_data_list)
    except Exception as e:
        console.print(f"   [bold red]❌ Error parsing Terraform files: {e}[/bold red]")
        return False
    
    secrets_ok = _check_hardcoded_secrets(all_data.get("variable", []))
    modules_ok = _check_module_version_pinning(all_data.get("module", []))

    return all([secrets_ok, modules_ok])


def _check_hardcoded_secrets(variables: List[Dict[str, Any]]) -> bool:
    """Checks if variables with sensitive names have a default value."""
    found_secrets = []
    for var_block in variables:
        for var_name, var_details_list in var_block.items():
            if any(keyword in var_name.lower() for keyword in SECRET_KEYWORDS):
                for var_details in var_details_list:
                    if "default" in var_details:
                        found_secrets.append(f"variable.{var_name}")
    
    status = "[bold green]✔ OK[/bold green]" if not found_secrets else f"[bold red]🔥 {len(found_secrets)} Issues Found[/bold red]"
    console.print(f"   - Hardcoded Secrets: {status}")
    if found_secrets:
        console.print(Panel(f"The following variables seem to contain hardcoded secrets. Use a secrets manager instead.\n- " + "\n- ".join(found_secrets), title="Hardcoded Secrets Detected", border_style="red"))
    return not found_secrets

def _check_module_version_pinning(modules: List[Dict[str, Any]]) -> bool:
    """Checks if all module blocks have a 'version' attribute."""
    unpinned_modules = set()
    for module_block in modules:
        for module_name, module_details_list in module_block.items():
            for module_details in module_details_list:
                if "version" not in module_details:
                    unpinned_modules.add(f"module.{module_name}")

    status = "[bold green]✔ OK[/bold green]" if not unpinned_modules else f"[bold yellow]⚠️ {len(unpinned_modules)} Issues Found[/bold yellow]"
    console.print(f"   - Module Version Pinning: {status}")
    if unpinned_modules:
        console.print(Panel(f"The following modules are not pinned to a specific version:\n- " + "\n- ".join(sorted(list(unpinned_modules))), title="Unpinned Modules", border_style="yellow"))
    return not unpinned_modules