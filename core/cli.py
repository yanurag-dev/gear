import typer
from core.planner import Planner
from core.executor import Executor
from core.models import Plan
import json
import dataclasses

app = typer.Typer()

@app.command()
def run(goal: str = typer.Option(..., help="The high-level goal for the agent to achieve.")):
    """Run the AI task-runner agent with a given goal."""
    typer.echo(f"Received goal: {goal}")

    planner = Planner()
    executor = Executor()

    try:
        response = planner.generate_plan(goal)

        if isinstance(response, Plan):
            typer.echo("\nGenerated Plan:")
            try:
                if hasattr(response, 'model_dump'): # Pydantic v2
                    typer.echo(json.dumps(response.model_dump(), indent=2))
                elif hasattr(response, 'json'): # Pydantic v1
                    typer.echo(response.json(indent=2))
                elif dataclasses.is_dataclass(response): # Dataclass
                    typer.echo(json.dumps(dataclasses.asdict(response), indent=2))
                else: # Fallback for other types
                    typer.echo(json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o)), indent=2))
            except Exception as e:
                typer.echo(f"Error serializing Plan: {e}", err=True)
                typer.echo(str(response)) # Print raw response if serialization fails

            typer.echo("\nExecuting Plan...")
            executor.execute_plan(response)
            typer.echo("\nPlan execution complete.")
        elif isinstance(response, str):
            typer.echo("\nDirect LLM Response:")
            typer.echo(response)
        else:
            typer.echo("\nUnexpected response type from Planner.", err=True)
            raise typer.Exit(code=1)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
