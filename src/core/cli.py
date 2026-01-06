import typer
import traceback
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
        typer.secho(f"Initialization failed: {e}", fg=typer.colors.RED, err=True)
        typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1)

    typer.echo("Gear is ready!")
    typer.echo("Starting interactive chat. Type 'exit' or 'quit' to end.")

    try:
        while True:
            goal = typer.prompt("Enter your goal ('stop' to take over, 'exit' to quit)")
            if goal.lower() in ["exit", "quit"]:
                typer.echo("Ending chat session. Goodbye!")
                break
            
            if goal.lower() == "stop":
                typer.echo("Agent paused. You can now interact with the browser manually.")
                typer.echo("Type another goal when you want the agent to resume.")
                continue

            typer.echo(f"Received goal: {goal}")

            try:
                context = executor.get_current_state()
                response = planner.generate_plan(goal, context=context)

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

@app.command()
def analyze(url: str = typer.Argument(..., help="The URL of the form to analyze")):
    """Analyze a web form and show its schema."""
    from src.llm.adapter import _ensure_initialized
    try:
        _ensure_initialized()
    except Exception as e:
        typer.secho(f"Initialization failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    from src.core.executor import Executor
    typer.echo(f"Analyzing form at: {url}")
    executor = Executor()
    try:
        pw = executor.get_playwright_service()
        pw.navigate(url)
        fields = pw.get_form_fields()
        
        # Simplify fields for display
        schema = {}
        for field in fields:
            if field['type'] in ['submit', 'button'] and not field.get('isNavigationButton'):
                continue
            
            key = field.get('label') or field.get('name') or field.get('placeholder') or f"field_{field['index']}"
            schema[key] = {
                "type": field['type'],
                "required": field['required'],
                "selector": field['selector']
            }
            if field.get('options'):
                schema[key]["options"] = [opt.get('text') or opt.get('label') for opt in field['options']]
        
        typer.echo("\nExtracted Form Schema:")
        typer.echo(json.dumps(schema, indent=2))
    finally:
        executor.cleanup()

@app.command()
def resolve(
    url: str = typer.Argument(..., help="The URL of the form to resolve"),
    knowledge_base_dir: str = typer.Option("./user_data", help="Directory containing user documents")
):
    """Resolve form fields using local documents."""
    from src.llm.adapter import _ensure_initialized
    try:
        _ensure_initialized()
    except Exception as e:
        typer.secho(f"Initialization failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    from src.services.document_loader import DocumentLoader
    from src.core.context_resolver import ContextResolver
    from src.core.executor import Executor
    
    typer.echo(f"Resolving context for: {url}")
    
    # 1. Load Documents
    typer.echo(f"Loading documents from: {knowledge_base_dir}")
    # Ensure directory exists
    import os
    if not os.path.exists(knowledge_base_dir):
        os.makedirs(knowledge_base_dir, exist_ok=True)
        typer.secho(f"Created directory: {knowledge_base_dir}. Please add documents there.", fg=typer.colors.YELLOW)
        return

    loader = DocumentLoader(knowledge_base_dir)
    knowledge_context = loader.load_all_documents()
    
    if not knowledge_context:
        typer.secho("No documents found in knowledge base. Add some files (PDF, TXT, MD) and try again.", fg=typer.colors.RED)
        return

    # 2. Extract Schema from Page
    typer.echo("Fetching form fields from page...")
    executor = Executor()
    try:
        pw = executor.get_playwright_service()
        pw.navigate(url)
        # Give a little extra time for dynamic fields
        import time
        time.sleep(2)
        fields = pw.get_form_fields()
        
        # Create a Target Schema for Gemini
        target_schema = {}
        for field in fields:
            if field['type'] in ['submit', 'button']: continue
            key = field.get('label') or field.get('name') or field.get('placeholder') or f"field_{field['index']}"
            target_schema[key] = f"type: {field['type']}, required: {field['required']}"
            if field.get('options'):
                opts = [opt.get('text') or opt.get('label') for opt in field['options']]
                target_schema[key] += f", options: {opts}"

        # 3. Resolve
        typer.echo("Mapping documents to form fields...")
        resolver = ContextResolver()
        resolved_data = resolver.resolve(target_schema, knowledge_context)
        
        typer.echo("\n--- RESOLUTION RESULTS ---")
        for key, value in resolved_data.items():
            status = "✅" if value else "❌"
            color = typer.colors.GREEN if value else typer.colors.RED
            typer.secho(f"{status} {key}: {value}", fg=color)
        
        gaps = resolver.identify_gaps(resolved_data)
        if gaps:
            typer.secho(f"\nGaps identified: {len(gaps)} missing fields.", fg=typer.colors.YELLOW)
        else:
            typer.secho("\nAll fields successfully resolved!", fg=typer.colors.GREEN, bold=True)
            
    finally:
        executor.cleanup()

if __name__ == "__main__":
    app()