# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Ray MCP (Model Context Protocol) server that provides comprehensive Ray cluster management, job execution, and distributed computing capabilities. The server acts as an MCP bridge to Ray, enabling LLMs to manage Ray clusters and jobs through structured tool calls.

## Architecture

- **`ray_mcp/main.py`**: Main MCP server entry point with tool definitions and request handlers
- **`ray_mcp/ray_manager.py`**: Core Ray cluster management (RayManager class)
- **`ray_mcp/worker_manager.py`**: Multi-node worker management and orchestration
- **`ray_mcp/tools.py`**: MCP tool implementations and validation
- **`ray_mcp/types.py`**: Type definitions and Pydantic models for all data structures
- **`examples/`**: Working examples demonstrating Ray usage patterns
- **`tests/`**: Comprehensive test suite with multiple test categories

## Key Development Commands

### Testing
```bash
# Fast development tests (excludes e2e)
make test

# Full test suite including e2e tests
make test-full  

# Smart test runner (detects changes)
make test-smart

# Specific test categories
make test-smoke    # Basic functionality verification
make test-e2e      # End-to-end integration tests
```

### Code Quality
```bash
# Run all linting checks
make lint

# Auto-format code
make format

# Individual checks
uv run pyright ray_mcp/    # Type checking
uv run black ray_mcp/      # Code formatting
uv run isort ray_mcp/      # Import sorting
```

### Development Setup
```bash
# Full development setup
make dev-install

# Install dependencies only
uv sync

# Run the MCP server
uv run ray-mcp
```

### Testing Infrastructure

The project uses pytest with custom markers:
- `fast`: Quick unit/integration tests for development
- `e2e`: End-to-end tests requiring full Ray cluster setup
- `smoke`: Minimal verification tests
- `slow`: Performance-intensive tests

Test files follow patterns: `test_*.py` in the `tests/` directory.

## Multi-Node Architecture

The server supports both single-node and multi-node Ray clusters:
- **Default**: Creates head node + 2 worker nodes automatically
- **Custom**: Supports configurable worker node specifications
- **WorkerManager**: Handles worker lifecycle and resource management

## Key Implementation Details

- All Ray operations are wrapped with proper error handling for Ray availability
- The server uses async/await patterns for MCP protocol compliance
- Type safety is enforced with Pydantic models and pyright type checking
- Multi-node clusters use localhost networking with configurable ports
- Job submission supports both simple scripts and complex workflow orchestration

## Claude Desktop Setup

### Local Development
```json
{
  "mcpServers": {
    "ray-mcp": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--directory", "/path/to/ray-mcp", "ray-mcp"]
    }
  }
}
```

### Connecting to Remote Ray Cluster
```json
{
  "mcpServers": {
    "ray-mcp": {
      "command": "/opt/homebrew/bin/uv", 
      "args": ["run", "--directory", "/path/to/ray-mcp", "ray-mcp"],
      "env": {
        "RAY_ADDRESS": "ray://127.0.0.1:10001"
      }
    }
  }
}
```

### Kubernetes Ray Cluster
For Kubernetes-deployed Ray clusters, port-forward the Ray client port:
```bash
kubectl port-forward -n ray-cluster ray-cluster-kuberay-head-<pod-id> 10001:10001
```

Then use `RAY_ADDRESS=ray://127.0.0.1:10001` in Claude Desktop config.

### Version Compatibility
Ensure local Ray/Python versions match your cluster:
- Check cluster versions: `kubectl logs -n ray-cluster ray-cluster-kuberay-head-<pod-id>`
- Update `pyproject.toml` to match cluster Ray version
- Use `uv python pin <version>` to match Python version
- Run `uv sync` to update dependencies

## Development Notes

- This project uses `uv` exclusively (not pip or python directly)
- All commands should use `uv run` prefix
- The codebase follows black formatting and isort import organization
- Coverage threshold is set to 80% minimum
- Test execution time is optimized with parallel test runners and smart test selection