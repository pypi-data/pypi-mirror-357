import typer
import semver
import shutil
from typing import Optional

from ..app import app, console
from ..core.utils import run_command

def _get_latest_version(tags_str: str) -> Optional[semver.VersionInfo]:
    """Parses a list of tags and returns the latest semver version."""
    latest_semver = None
    for tag in tags_str.split('\n'):
        if not tag:
            continue
        try:
            version_str = tag.lstrip('v')
            version = semver.VersionInfo.parse(version_str)
            if latest_semver is None or version.compare(latest_semver) > 0:
                latest_semver = version
        except ValueError:
            continue
    return latest_semver


@app.command()
def publish():
    """
    Publish a new version by creating a git tag and a GitHub release.
    """
    console.print("🚀 Starting module publish process...")

    success, git_status, err = run_command(["git", "status", "--porcelain"])
    if not success:
        console.print(f"[bold red]Error checking git status:[/bold red]\n{err}")
        raise typer.Exit(code=1)
    if git_status:
        console.print("[bold red]Error:[/bold red] Uncommitted changes found. Please commit or stash them before publishing.")
        raise typer.Exit(code=1)
    console.print("✔ Git working directory is clean.")

    console.print("Fetching latest tags from remote...")
    success, _, err = run_command(["git", "fetch", "--tags"])
    if not success:
        console.print(f"[bold red]Error fetching git tags:[/bold red]\n{err}")
        raise typer.Exit(code=1)

    success, all_tags, err = run_command(["git", "tag"])
    if not success:
        console.print(f"[bold red]Error listing git tags:[/bold red]\n{err}")
        raise typer.Exit(code=1)
        
    latest_version = _get_latest_version(all_tags)

    if latest_version:
        console.print(f"Latest version found: [bold cyan]v{latest_version}[/bold cyan]")
        next_version_suggestion = f"v{latest_version.bump_patch()}"
    else:
        console.print("No existing version tags found.")
        next_version_suggestion = "v0.1.0"
    
    new_version_str = typer.prompt(
        f"Enter new version (suggestion: {next_version_suggestion})",
        default=next_version_suggestion
    )

    try:
        semver.VersionInfo.parse(new_version_str.lstrip('v'))
        if not new_version_str.startswith('v'):
            console.print("[bold yellow]Warning:[/bold yellow] Version does not start with 'v'. Adding 'v' prefix.")
            new_version_str = f"v{new_version_str}"
            
    except ValueError:
        console.print(f"[bold red]Error:[/bold red] Invalid version format. Please use semantic versioning (e.g., v1.2.3).")
        raise typer.Exit(code=1)

    console.print(f"Creating tag [bold cyan]{new_version_str}[/bold cyan]...")
    success, _, err = run_command(["git", "tag", new_version_str])
    if not success:
        console.print(f"[bold red]Error creating git tag:[/bold red]\n{err}")
        raise typer.Exit(code=1)

    console.print(f"Pushing tag [bold cyan]{new_version_str}[/bold cyan] to remote 'origin'...")
    success, _, err = run_command(["git", "push", "origin", new_version_str])
    if not success:
        console.print(f"[bold red]Error pushing git tag:[/bold red]\n{err}")
        raise typer.Exit(code=1)

    console.print(f"\n[bold green]✔ Git tag {new_version_str} published successfully![/bold green]")

    if not shutil.which("gh"):
        console.print("\n[yellow]GitHub CLI ('gh') not found. Skipping release creation.[/yellow]")
        console.print("Install it to enable GitHub Release creation: https://cli.github.com/")
        raise typer.Exit()

    create_release = typer.confirm("\nDo you want to create a GitHub Release for this tag?", default=True)

    if create_release:
        console.print(f"Creating GitHub Release for tag [bold cyan]{new_version_str}[/bold cyan]...")
        success, _, err = run_command(["gh", "release", "create", new_version_str, "--generate-notes", "--notes", ""])
        if not success:
            console.print(f"\n[bold red]Failed to create GitHub Release.[/bold red]\n{err}")
            console.print("Please check if you are authenticated with 'gh auth login' and have rights to the repository.")
            raise typer.Exit(code=1)
        
        console.print("\n[bold green]✔ GitHub Release created successfully![/bold green]")
        console.print("Opening the release in your browser to view and publish...")
        run_command(["gh", "release", "view", new_version_str, "--web"])