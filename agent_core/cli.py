import typer
from agent_core.planner import Planner
from agent_core.executor import Executor
from agent_core.models import Plan

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
            typer.echo(response.json(indent=2))

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
