import logging
from pathlib import Path

import typer
import yaml
from pkg_resources import get_distribution
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from .banner import ASCII_TITLE
from .generators import (
    generate_agent_code,
    generate_env_example,
    generate_prompt_template,
    generate_readme,
    generate_requirements,
)
from .validators import validate_spec

app = typer.Typer(help="Open Agent Spec (OAS) CLI")
console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with appropriate level and handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )
    return logging.getLogger("oas")


def get_version_from_pyproject():
    """Get the version from package metadata."""
    try:
        return get_distribution("open-agent-spec").version
    except Exception:
        return "unknown"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    """Main CLI entry point."""
    if version:
        cli_version = get_version_from_pyproject()
        console.print(
            f"[bold cyan]Open Agent Spec CLI[/] version [green]{cli_version}[/]"
        )
        raise typer.Exit()

    if ctx.invoked_subcommand is None or ctx.invoked_subcommand == "help":
        console.print(f"[bold cyan]{ASCII_TITLE}[/]\n")
        console.print(
            Panel.fit(
                "Use [bold magenta]oas init[/] to scaffold an agent project\n"
                "Use [bold magenta]oas update[/] to update existing agent code\n"
                "Define it via Open Agent Spec YAML\n"
                "Use [bold yellow]--dry-run[/] to preview actions without writing files.",
                title="[bold green]OAS CLI[/]",
                subtitle="Open Agent Spec Generator",
            )
        )


def load_and_validate_spec(
    spec_path: Path, log: logging.Logger
) -> tuple[dict, str, str]:
    """Load and validate a spec file, returning the data and derived names."""
    log.info(f"Reading spec from: {spec_path}")
    try:
        with open(spec_path) as f:
            spec_data = yaml.safe_load(f)
        log.info("Spec file loaded successfully")
    except yaml.YAMLError as err:
        log.error(f"Error reading spec file: {err}")
        raise ValueError("Invalid YAML format") from err

    try:
        agent_name, class_name = validate_spec(spec_data)
        return spec_data, agent_name, class_name
    except ValueError as err:
        log.error(str(err))
        raise ValueError(f"Invalid spec: {err}") from err


def generate_files(
    output: Path, spec_data: dict, agent_name: str, class_name: str, log: logging.Logger
) -> None:
    """Generate all agent files."""
    try:
        # Create output directory
        output.mkdir(parents=True, exist_ok=True)

        # Generate each file
        generate_agent_code(output, spec_data, agent_name, class_name)
        generate_readme(output, spec_data)
        generate_requirements(output)
        generate_env_example(output)
        generate_prompt_template(output, spec_data)

        console.print("\n[bold green]✅ Agent project initialized![/] ✨")
        log.info("Project initialized")
        log.info("\nNext steps:")
        log.info("1. cd into the output directory")
        log.info("2. Copy .env.example to .env and set your OpenAI key")
        log.info("3. Run: pip install -r requirements.txt")
        log.info("4. Run: python agent.py")

    except Exception as err:
        log.error(f"Error during file generation: {err}")
        raise RuntimeError(f"Failed to generate agent code: {err}") from err


@app.command()
def version():
    """Show the Open Agent Spec CLI version."""
    cli_version = get_version_from_pyproject()
    console.print(f"[bold cyan]Open Agent Spec CLI[/] version [green]{cli_version}[/]")


@app.command()
def init(
    spec: Path = typer.Option(..., help="Path to Open Agent Spec YAML file"),
    output: Path = typer.Option(..., help="Directory to scaffold the agent into"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview what would be created without writing files"
    ),
):
    """Initialize an agent project based on Open Agent Spec."""
    log = setup_logging(verbose)
    if verbose:
        log.setLevel(logging.DEBUG)

    console.print(
        Panel(
            ASCII_TITLE,
            title="[bold cyan]OAS CLI[/]",
            subtitle="[green]Open Agent Spec Generator[/]",
        )
    )

    spec_data, agent_name, class_name = load_and_validate_spec(spec, log)

    if dry_run:
        console.print(
            Panel.fit(
                "🧪 [bold]Dry run mode[/]: No files will be written.", style="yellow"
            )
        )
        log.info("Agent Name: %s", agent_name)
        log.info("Class Name: %s", class_name)
        log.info("Output directory would be: %s", output.resolve())
        log.info("Files that would be created:")
        log.info("- agent.py")
        log.info("- README.md")
        log.info("- requirements.txt")
        log.info("- .env.example")
        log.info("- prompts/agent_prompt.jinja2")
        return

    generate_files(output, spec_data, agent_name, class_name, log)


@app.command()
def update(
    spec: Path = typer.Option(..., help="Path to updated Open Agent Spec YAML file"),
    output: Path = typer.Option(..., help="Directory containing the agent to update"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview what would be updated without writing files"
    ),
):
    """Update an existing agent project based on changes to the Open Agent Spec."""
    log = setup_logging(verbose)
    if verbose:
        log.setLevel(logging.DEBUG)

    console.print(
        Panel(
            ASCII_TITLE,
            title="[bold cyan]OAS CLI[/]",
            subtitle="[green]Open Agent Spec Updater[/]",
        )
    )

    # Check if output directory exists
    if not output.exists():
        log.error(
            f"Output directory {output} does not exist. Use 'oas init' to create a new agent."
        )
        raise typer.Exit(1)

    spec_data, agent_name, class_name = load_and_validate_spec(spec, log)

    if dry_run:
        console.print(
            Panel.fit(
                "🧪 [bold]Dry run mode[/]: No files will be updated.", style="yellow"
            )
        )
        log.info("Agent Name: %s", agent_name)
        log.info("Class Name: %s", class_name)
        log.info("Files that would be updated:")
        log.info("- agent.py")
        log.info("- README.md")
        log.info("- requirements.txt")
        log.info("- .env.example")
        log.info("- prompts/agent_prompt.jinja2")
        return

    # Generate updated files
    log.info("Generating updated files...")
    generate_files(output, spec_data, agent_name, class_name, log)

    console.print("\n[bold green]✅ Agent project updated![/] ✨")
    log.info("Note: If you're using version control, make sure to commit your changes.")


if __name__ == "__main__":
    app()
