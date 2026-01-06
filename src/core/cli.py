import typer
from src.core.planner import Planner
from src.core.executor import Executor
from src.core.models import Plan
import json
import dataclasses
import logging

# Configure logging to show warnings and errors
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

app = typer.Typer()

@app.command()
def setup():
    """Setup the environment (install Playwright browsers, etc.)."""
    import subprocess
    import sys
    typer.echo("Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        typer.echo("Playwright browsers installed successfully.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error installing browsers: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def chat():
    """Chat with the AI task-runner agent."""
    typer.echo("Initializing Gear...")
    planner = Planner()
    executor = Executor()
    
    # Proactively check config and environment
    from src.llm.adapter import _ensure_initialized
    try:
        _ensure_initialized()
        # Optional: Pre-warm the browser if we want it ready immediately
        # executor.get_playwright_service() 
    except Exception as e:
        raise typer.Exit(code=1)

    typer.echo("Gear is ready!")
    typer.echo("Starting interactive chat. Type 'exit' or 'quit' to end.")

    try:
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
                    results = executor.execute_plan(response)
                    
                    # Display results (like form fields) to the user
                    for i, result in enumerate(results):
                        if result:
                            typer.echo(f"\nResult from Step {i+1}:")
                            if isinstance(result, (list, dict)):
                                typer.echo(json.dumps(result, indent=2))
                            else:
                                typer.echo(str(result))
                    
                    typer.echo("\nPlan execution complete.")
                elif isinstance(response, str):
                    typer.echo("\nDirect LLM Response:")
                    typer.echo(response)
                elif response is None:
                    typer.echo("No response received from planner — please try again later; session remains active", err=True)
                else:
                    typer.echo("\nUnexpected response type from Planner.", err=True)
                    # Don't exit, just continue
            except ValueError as e:
                typer.echo(f"Error: {e}", err=True)
    finally:
        executor.cleanup()

if __name__ == "__main__":
    app()