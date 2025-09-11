# Gear: AI Task-Runner Agent

![Gear Logo Placeholder](https://via.placeholder.com/150?text=Gear)

## Project Overview

**Gear** is a general-purpose AI task-runner agent designed to automate complex workflows by translating high-level natural language goals into executable plans. It's built with a modular and extensible architecture, making it adaptable for various automation domains, starting with job application automation.

## Core Components

Gear's architecture is composed of several interconnected services:

1.  **Agent Core (Python Service):**
    *   **Planner:** Uses an LLM to generate structured JSON plans from high-level goals.
    *   **Executor:** Executes plan steps by calling external MCP servers.
    *   **Verifier:** (Future) Validates results of each step before continuing.
    *   **Persistence:** (Future) Stores plans, operations, and artifacts.
    *   **Observability:** (Future) Structured logs, traces, metrics.

2.  **MCP Servers (Model Context Protocol):**
    Standalone services responsible for specific actions. They are designed to be extensible.
    *   **Playwright MCP:** Automates browser actions (scraping, navigation, form filling).
    *   **Filesystem MCP:** Handles file read/write, artifact storage, versioning.
    *   **Notion MCP:** CRUD operations on Notion pages/databases.
    *(Extensible: Easily add more MCPs like Email, Slack, Jira, etc.)*

3.  **LLM Provider:**
    An adapter layer for various Large Language Models (e.g., OpenAI, Anthropic). Used by the Planner to generate plans.

4.  **CLI (Command Line Interface):**
    The primary interface for users to submit goals and interact with the agent.

## Flow of Execution

1.  **User/Scheduler Submits Goal:** A high-level goal (e.g., "Apply to top 5 Python developer jobs on Indeed") is submitted via the CLI.
2.  **Planning:** The `Planner` (using an LLM) generates a structured JSON plan describing the necessary steps.
3.  **Execution:** The `Executor` iterates through the plan's steps, calling the appropriate MCP server with structured arguments.
4.  **Verification:** (Future) Results are validated by the `Verifier`.
5.  **Persistence:** (Future) Plan, step results, and artifacts are stored.
6.  **Completion:** Success/failure is logged, and results are synced (e.g., to Notion).

## Getting Started

### Prerequisites

*   Python 3.8+ (or newer)
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/gear.git # Replace with your actual repo URL
    cd gear
    ```
2.  **Install dependencies:**
    ```bash
    python3 -m pip install -r requirements.txt
    ```

### Configuration

Adjust the settings in `config/settings.yaml` to configure LLM providers, MCP server URLs, and other parameters. A sample configuration is provided:

```yaml
# config/settings.yaml
llm:
  provider: mock # or openai, anthropic, etc.
  api_key: your_llm_api_key # Replace with your actual API key
mcp_servers:
  playwright:
    url: http://localhost:8000
  filesystem:
    url: http://localhost:8001
  notion:
    url: http://localhost:8002
```

## Usage

Interact with the Gear agent using the command-line interface.

To run the agent with a specific goal:

```bash
python -m agent_core.cli run "your high-level goal here"
```

### Examples:

*   **Open Google:**
    ```bash
    python -m agent_core.cli run "open google"
    ```
*   **Search on Google:**
    ```bash
    python -m agent_core.cli run "search for latest AI news"
    ```

## Development

### Running MCP Servers (Example: Playwright MCP)

To run the Playwright MCP (which the Executor will call):

```bash
cd gear # Ensure you are in the project root
uvicorn mcp_servers.playwright_mcp.main:app --reload
```

### Extending Gear

*   **Adding New MCPs:** Create a new directory under `mcp_servers/`, implement its API (e.g., using FastAPI), and update `config/settings.yaml`.
*   **Integrating New LLMs:** Implement a new adapter in `llm_provider/` that conforms to the expected interface.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) (future).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (future).

## Contact

For questions or feedback, please open an issue on the GitHub repository.
