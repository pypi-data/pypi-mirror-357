# Kubernetes Ray Cluster Setup

This guide explains how to connect the Ray MCP server to a Ray cluster running in Kubernetes.

## Prerequisites

- Kubernetes cluster with Ray operator deployed
- `kubectl` configured to access your cluster
- Claude Desktop installed

## Step 1: Identify Your Ray Cluster

Find your Ray head node pod:
```bash
kubectl get pods -n ray-cluster
```

Look for a pod name like `ray-cluster-kuberay-head-<hash>`.

## Step 2: Check Ray Services

Verify the Ray services and ports:
```bash
kubectl get svc -n ray-cluster
```

You should see a service with ports including:
- `10001/TCP` - Ray Client port (required)
- `8265/TCP` - Ray Dashboard
- `6379/TCP` - Ray GCS port

## Step 3: Port Forward Ray Client

Forward the Ray Client port to your local machine:
```bash
kubectl port-forward -n ray-cluster ray-cluster-kuberay-head-<hash> 10001:10001
```

Keep this command running in a terminal window.

## Step 4: Check Cluster Versions

Get the Ray and Python versions from your cluster:
```bash
kubectl logs -n ray-cluster ray-cluster-kuberay-head-<hash> | grep -E "(Ray|Python)"
```

Example output:
```
Ray: 2.47.0
Python: 3.12.9
```

## Step 5: Configure Local Environment

Clone and set up the Ray MCP server:
```bash
git clone <repo-url>
cd ray-mcp

# Match your cluster's Python version
uv python pin 3.12

# Update pyproject.toml to match cluster Ray version
# Edit: ray[default]==2.47.0

# Install dependencies
uv sync
```

## Step 6: Configure Claude Desktop

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

Add the Ray MCP server:
```json
{
  "mcpServers": {
    "ray-mcp": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "--directory", "/absolute/path/to/ray-mcp", "ray-mcp"],
      "env": {
        "RAY_ADDRESS": "ray://127.0.0.1:10001"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/ray-mcp` with the actual path to your cloned repository.

## Step 7: Test Connection

1. Restart Claude Desktop
2. In a new conversation, ask: "What Ray tools are available?"
3. Test cluster connection: "Show me the Ray cluster status"

## Troubleshooting

### Version Mismatch Errors
If you see version mismatch errors:
1. Check cluster versions: `kubectl logs -n ray-cluster ray-cluster-kuberay-head-<hash>`
2. Update `pyproject.toml` to match exact Ray version
3. Use `uv python pin <version>` to match Python version
4. Run `uv sync` to reinstall dependencies

### Connection Timeout
- Verify port-forward is running: `lsof -i :10001`
- Check if Ray Client port (10001) is exposed in the service
- Ensure no firewall blocking localhost:10001

### MCP Server Not Starting
- Check Claude Desktop logs for errors
- Verify the path in your config is absolute, not relative
- Test manually: `uv run ray-mcp` (should start without errors)

## Example Commands

Once connected, you can use commands like:
- "Submit a simple Ray job"
- "Show cluster resources and utilization"
- "List all running Ray jobs"
- "Get cluster node information"
- "Monitor job progress"