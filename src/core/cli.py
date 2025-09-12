import typer
from src.core.planner import Planner
from src.core.executor import Executor
from src.core.models import Plan
import json
import dataclasses

app = typer.Typer()

@app.command()
def chat():
    """Chat with the AI task-runner agent."""
    typer.echo("Starting interactive chat with the AI agent. Type 'exit' or 'quit' to end the session.")

    planner = Planner()
    executor = Executor()

    while True:
        goal = typer.prompt("Enter your goal (or 'exit'/'quit' to end)")
        if goal.lower() in ["exit", "quit"]:
            typer.echo("Ending chat session. Goodbye!")
            break

        typer.echo(f"Received goal: {goal}")

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
            elif response is None:
                typer.echo("No response received from planner — please try again later; session remains active", err=True)
                return
            else:
                typer.echo("\nUnexpected response type from Planner.", err=True)
                raise typer.Exit(code=1)

        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            # Do not exit, allow user to enter new goal
            # raise typer.Exit(code=1)

if __name__ == "__main__":
    app()