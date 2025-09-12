#!/bin/bash

# This script is for local development to start all MCP servers.
# In a production environment, these would likely be managed by Docker/Kubernetes.

echo "Starting Playwright MCP..."
uvicorn mcp.playwright_mcp.main:app --port 8000 --reload &
PLAYWRIGHT_PID=$!

echo "Starting Filesystem MCP..."
uvicorn mcp.filesystem_mcp.main:app --port 8001 --reload &
FILESYSTEM_PID=$!

echo "Starting Notion MCP..."
uvicorn mcp.notion_mcp.main:app --port 8002 --reload &
NOTION_PID=$!

echo "All MCPs started in background. PIDs: Playwright=$PLAYWRIGHT_PID, Filesystem=$FILESYSTEM_PID, Notion=$NOTION_PID"
echo "To stop them, run: kill $PLAYWRIGHT_PID $FILESYSTEM_PID $NOTION_PID"

wait
