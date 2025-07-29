"""Console script for dof."""

from dof import DOF

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def run():
    """Start Isaac Sim and open VS Code with the container connection."""
    try:
        dof = DOF()
        simulator = dof.start_sim()
        console.print("✅ [green]Successfully started Isaac Sim environment![/green]")
        console.print(
            "🤖 [blue]VS Code should open with the container connection.[/blue]"
        )
        return simulator
    except Exception as e:
        console.print(f"❌ [red]Failed to start Isaac Sim: {str(e)}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the application script"""
    app()


if __name__ == "__main__":
    main()
