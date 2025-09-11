import typer
from agent_core.planner import Planner
from agent_core.executor import Executor

app = typer.Typer()

@app.command()
def run(goal: str = typer.Argument(..., help="The high-level goal for the agent to achieve.")):
    """Run the AI task-runner agent with a given goal."""
    typer.echo(f"Received goal: {goal}")

    planner = Planner()
    executor = Executor()

    try:
        plan = planner.generate_plan(goal)
        typer.echo("\nGenerated Plan:")
        typer.echo(plan.json(indent=2))

        typer.echo("\nExecuting Plan...")
        executor.execute_plan(plan)
        typer.echo("\nPlan execution complete.")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
