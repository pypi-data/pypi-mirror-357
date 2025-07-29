import pathlib
import hcl2
import typer
from collections import defaultdict
from ..app import app, console

def _merge_dicts(list_of_dicts):
    merged = defaultdict(list)
    for d in list_of_dicts:
        for key, value in d.items():
            merged[key].extend(value)
    return dict(merged)

@app.command()
def docs():
    """
    Generate Terraform module documentation from variables and outputs.
    """
    console.print("📄 Generating module documentation...")
    
    cwd = pathlib.Path.cwd()
    readme_path = cwd / "README.md"
    tf_files = list(cwd.glob("*.tf"))

    if not tf_files:
        console.print("[bold red]Error:[/bold red] No .tf files found in the current directory.")
        raise typer.Exit(code=1)
    if not readme_path.exists():
        console.print("[bold red]Error:[/bold red] README.md not found in the current directory.")
        raise typer.Exit(code=1)

    try:
        parsed_data_list = []
        for tf_file in tf_files:
            with tf_file.open('r', encoding='utf-8') as f:
                parsed_data_list.append(hcl2.load(f))
        
        all_data = _merge_dicts(parsed_data_list)
        
        reqs_md = _generate_requirements_markdown(all_data.get("terraform", []))
        providers_md = _generate_providers_markdown(all_data.get("terraform", []))
        modules_md = _generate_modules_markdown(all_data.get("module", []))
        inputs_md = _generate_inputs_markdown(all_data.get("variable", []))
        outputs_md = _generate_outputs_markdown(all_data.get("output", []))
        
        _update_readme(readme_path, reqs_md, providers_md, modules_md, inputs_md, outputs_md)
        
        console.print("[bold green]✔ Documentation updated successfully in README.md![/bold green]")

    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)

def _generate_requirements_markdown(terraform_blocks: list) -> str:
    # ... (sve _generate i _update_readme funkcije idu ovde)
    if not terraform_blocks:
        return ""
    req_version = "n/a"
    for block in terraform_blocks:
        if "required_version" in block:
            req_version = block.get("required_version", "n/a")
            if isinstance(req_version, list):
                req_version = req_version[0]
            break
    md = "## Requirements\n\n"
    md += "| Name | Version |\n"
    md += "|------|:-------:|\n"
    md += f"| terraform | `{req_version}` |\n"
    return md

def _generate_providers_markdown(terraform_blocks: list) -> str:
    all_providers = {}
    for block in terraform_blocks:
        providers_block = block.get("required_providers")
        if providers_block and isinstance(providers_block, list):
            for provider_dict in providers_block:
                all_providers.update(provider_dict)
    if not all_providers:
        return ""
    md = "## Providers\n\n"
    md += "| Name | Version | Source |\n"
    md += "|------|:-------:|--------|\n"
    for name, details in all_providers.items():
        version = details.get("version", "any")
        source = details.get("source", "n/a")
        md += f"| `{name}` | `{version}` | `{source}` |\n"
    return md

def _generate_modules_markdown(modules: list) -> str:
    if not modules:
        return ""
    md = "## Modules\n\n"
    md += "| Name | Source | Version |\n"
    md += "|------|--------|:-------:|\n"
    for module_data in modules:
        for name, details in module_data.items():
            source = details.get("source", "n/a")
            version = details.get("version", "any")
            md += f"| `{name}` | `{source}` | `{version}` |\n"
    return md

def _generate_inputs_markdown(variables: list) -> str:
    if not variables:
        return ""
    md = "## Inputs\n\n"
    md += "| Name | Description | Type | Default | Required |\n"
    md += "|------|-------------|:----:|:-------:|:--------:|\n"
    for var_data in variables:
        for name, details in var_data.items():
            description = details.get("description", "").replace("\n", " ")
            var_type = f"`{details.get('type', 'any')}`"
            default = details.get("default")
            if default is None:
                default_str = "n/a"
                required = "yes"
            else:
                default_str = f"`{default}`"
                required = "no"
            md += f"| `{name}` | {description} | {var_type} | {default_str} | {required} |\n"
    return md

def _generate_outputs_markdown(outputs: list) -> str:
    if not outputs:
        return ""
    md = "## Outputs\n\n"
    md += "| Name | Description |\n"
    md += "|------|-------------|\n"
    for out_data in outputs:
        for name, details in out_data.items():
            description = details.get("description", "").replace("\n", " ")
            md += f"| `{name}` | {description} |\n"
    return md

def _update_readme(readme_path: pathlib.Path, *markdown_parts):
    start_marker = ""
    end_marker = ""
    readme_content = readme_path.read_text(encoding='utf-8')
    doc_content = "\n\n".join(part for part in markdown_parts if part).strip()
    if start_marker in readme_content and end_marker in readme_content:
        start_index = readme_content.find(start_marker)
        end_index = readme_content.find(end_marker)
        before_docs = readme_content[:start_index]
        after_docs = readme_content[end_index + len(end_marker):]
        new_readme_content = f"{before_docs}{start_marker}\n{doc_content}\n{end_marker}{after_docs}"
        readme_path.write_text(new_readme_content, encoding='utf-8')
    else:
        with readme_path.open('a', encoding='utf-8') as f:
            if readme_content and not readme_content.endswith('\n'):
                f.write('\n')
            full_doc_block = f"\n{start_marker}\n{doc_content}\n{end_marker}\n"
            f.write(full_doc_block)