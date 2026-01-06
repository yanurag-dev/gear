# Gear Project - Agent Operational Guidelines

This document outlines the context, rules, and standards for the AI agent working on the **Gear** project.

## 1. Project Overview
**Gear** is an intelligent, CLI-based browser automation and task runner agent. It leverages Large Language Models (LLMs) to plan and execute browser interactions and resolve form-filling tasks using local document context (RAG).

### Core Components
*   **CLI (`src/core/cli.py`)**: The entry point using `typer`. Handles commands like `chat`, `setup`, `analyze`, and `resolve`.
*   **Executor (`src/core/executor.py`)**: Manages browser state via `playwright`.
*   **Planner (`src/core/planner.py`)**: Generates execution plans using LLMs.
*   **Context Resolver (`src/core/context_resolver.py`)**: Maps local documents to web forms.
*   **Document Loader (`src/services/document_loader.py`)**: Ingests user documents.

## 2. Technology Stack
*   **Language**: Python 3.x
*   **CLI Framework**: `typer`
*   **Browser Automation**: `playwright` (Sync API)
*   **Data Validation**: `pydantic`
*   **LLM Provider**: Google Gemini (via `google-generativeai`)

## 3. Coding Standards & Patterns

### Imports & Structure
*   Always use absolute imports from the `src` root (e.g., `from src.core.models import Plan`).
*   Avoid circular imports by keeping data models (`src/core/models.py`) independent.

### Error Handling
*   Use `try/except` blocks for external operations (subprocess, network, file I/O).
*   In CLI commands, catch exceptions and raise `typer.Exit(code=1)` with details.
*   Use `traceback.format_exc()` for debug logging when verbose.

### CLI User Experience
*   Use `typer.echo()` and `typer.secho()` for output.
*   Use colors (RED for errors, GREEN for success, YElLOW for warnings) to improve readability.
*   Keep user prompts clear and actionable.

### Testing
*   When fixing bugs, attempt to verify with `pytest` if available, or manual reproduction steps.

## 4. Operational Guidelines

### Core Mandates
*   **Conventions**: Adhere to existing project conventions. Analyze surrounding code first.
*   **Libraries**: Verify library availability before importing.
*   **Paths**: Always use **absolute paths** for file operations.

### Interaction Style
*   **Concise & Direct**: Keep text output brief. Focus on the code.
*   **No Fluff**: Avoid "I hope this helps" or "Here is the code". Just state what was done.
*   **Proactive**: If a user asks for a feature, implement the necessary components, tests, and integration points.

### Safety
*   **Review Commands**: Explain potentially destructive commands (file deletion, system modifications) before running them.
*   **Security**: Never commit or log API keys.

## 5. Memory & Context
*   Update this file (`gemini.md`) if significant architectural changes or new persistent rules are established.