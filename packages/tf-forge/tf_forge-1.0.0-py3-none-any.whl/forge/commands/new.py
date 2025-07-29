import pathlib
import typer
from rich.tree import Tree
from ..app import app, console

MODULE_STRUCTURE = {
    ".gitignore": """# Terraform specific
.terraform/
*.tfstate
*.tfstate.*
crash.log
*.tfvars
*.tfplan

# OS specific
.DS_Store
Thumbs.db
""",
    "main.tf": "# Add your main resources here",
    "versions.tf": "# Add your versions here",
    "variables.tf": "# Add your variables here",
    "outputs.tf": "# Add your outputs here",
    "README.md": "",
    "examples": {
        "basic": {
            "main.tf": """
module "example" {
  source = "../../"
  # Add required variables here
}
"""
        }
    }
}

@app.command()
def new(
    module_name: str = typer.Argument(
        ...,
        help="The name of the Terraform module to create (e.g., terraform-aws-vpc).",
    )
):
    """
    Create a new, standardized Terraform module directory structure.
    """
    console.print(f"🔥 Forging new Terraform module: [bold cyan]{module_name}[/bold cyan]")
    module_path = pathlib.Path.cwd() / module_name
    if module_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{module_name}' already exists.")
        raise typer.Exit(code=1)
    try:
        _create_structure(module_path, MODULE_STRUCTURE, module_name)
        console.print("\n[bold green]✔ Module forged successfully![/bold green]")
        tree = Tree(f"📁 [bold cyan]{module_name}[/bold cyan]")
        _build_tree(module_path, tree)
        console.print(tree)
    except IOError as e:
        console.print(f"[bold red]Error creating module structure:[/bold red] {e}")
        raise typer.Exit(code=1)


def _create_structure(base_path: pathlib.Path, structure: dict, module_name: str):
    base_path.mkdir(parents=True, exist_ok=True)
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict):
            _create_structure(path, content, module_name)
        else:
            final_content = content.strip().replace("$MODULE_NAME", module_name)
            path.write_text(final_content)


def _build_tree(directory: pathlib.Path, tree: Tree):
    paths = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for path in paths:
        if path.is_dir():
            branch = tree.add(f"📁 [bold cyan]{path.name}[/bold cyan]")
            _build_tree(path, branch)
        else:
            tree.add(f"📄 {path.name}")