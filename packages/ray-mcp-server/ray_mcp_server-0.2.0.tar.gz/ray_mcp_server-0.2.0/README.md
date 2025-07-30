# ⚡ Ray MCP Server

🚀 **Supercharge your AI workflows with distributed computing!** 

A powerful Model Context Protocol (MCP) server that brings Ray's distributed computing capabilities directly to Claude Desktop. Manage clusters, submit jobs, and orchestrate complex workflows through natural language commands! 🎯

## ✨ Features

- 🏗️ **Multi-Node Cluster Management**: Start and manage Ray clusters with head nodes and worker nodes
- 🚀 **Job Management**: Submit, monitor, and manage Ray jobs with ease
- 🎭 **Actor Management**: Create and manage Ray actors for stateful computations
- 📊 **Real-time Monitoring**: Get cluster status, resource usage, and performance metrics
- 🔍 **Logging and Debugging**: Access logs and debug job issues seamlessly
- ⏰ **Scheduling**: Schedule jobs with cron-like syntax for automated workflows

## 🚀 Quick Start

### 📦 Installation

**🚀 Super Easy with uvx (Recommended):**
```bash
# Install and run directly with uvx - no setup needed! ⚡
uvx ray-mcp-server
```

**📥 Or clone for development:**
```bash
# Clone the repository
git clone <repository-url>
cd ray-mcp

# Install dependencies with UV (lightning fast! ⚡)
uv sync

# You're ready to go! 🎉
```

### 🎯 Starting Ray Clusters

The server supports both single-node and multi-node cluster configurations:

#### 🖥️ Simple Single-Node Cluster

```json
{
  "tool": "start_ray",
  "arguments": {
    "num_cpus": 4,
    "num_gpus": 1
  }
}
```

#### 🌐 Multi-Node Cluster (Default)

The server now defaults to starting multi-node clusters with 2 worker nodes (perfect for scaling! 📈):

```json
{
  "tool": "start_ray",
  "arguments": {
    "num_cpus": 1
  }
}
```

This creates:
- 🧠 **Head node**: 1 CPU, 0 GPUs, 1GB object store memory
- ⚙️ **Worker node 1**: 2 CPUs, 0 GPUs, 500MB object store memory  
- ⚙️ **Worker node 2**: 2 CPUs, 0 GPUs, 500MB object store memory

#### 🛠️ Custom Multi-Node Setup

For advanced configurations, you can specify custom worker nodes:

```json
{
  "tool": "start_ray",
  "arguments": {
    "num_cpus": 4,
    "num_gpus": 0,
    "object_store_memory": 1000000000,
    "worker_nodes": [
      {
        "num_cpus": 2,
        "num_gpus": 0,
        "object_store_memory": 500000000,
        "node_name": "cpu-worker-1"
      },
      {
        "num_cpus": 4,
        "num_gpus": 1,
        "object_store_memory": 1000000000,
        "node_name": "gpu-worker-1",
        "resources": {"custom_resource": 2}
      }
    ],
    "head_node_port": 10001,
    "dashboard_port": 8265,
    "head_node_host": "127.0.0.1"
  }
}
```

### 💫 Basic Usage

Just ask Claude Desktop naturally! 🗣️

- *"What's my Ray cluster status?"* 
- *"Submit a job to process my data"*
- *"Show me cluster resources"*
- *"List all running jobs"*

Or use direct tool calls:
```json
{
  "tool": "cluster_status"
}
```

## 🛠️ Available Tools

20+ powerful tools for comprehensive Ray management! 💪

### 🏗️ Cluster Operations
- 🚀 `start_ray` - Start a new Ray cluster with head node and optional worker nodes
- 🔗 `connect_ray` - Connect to an existing Ray cluster
- 🛑 `stop_ray` - Stop the current Ray cluster
- 📊 `cluster_status` - Get comprehensive cluster status
- 💾 `cluster_resources` - Get resource usage information
- 🖥️ `cluster_nodes` - List all cluster nodes
- ⚙️ `worker_status` - Get detailed status of worker nodes

### 🚀 Job Operations
- 📤 `submit_job` - Submit a new job to the cluster
- 📋 `list_jobs` - List all jobs (running, completed, failed)
- 🔍 `job_status` - Get detailed status of a specific job
- ❌ `cancel_job` - Cancel a running or queued job
- 👀 `monitor_job` - Monitor job progress in real-time
- 🐛 `debug_job` - Debug a job with detailed information
- 📜 `get_logs` - Retrieve job logs and outputs

### 🎭 Actor Operations
- 👥 `list_actors` - List all actors in the cluster
- 💀 `kill_actor` - Terminate a specific actor

### 📈 Enhanced Monitoring
- ⚡ `performance_metrics` - Get detailed cluster performance metrics
- 🏥 `health_check` - Perform comprehensive cluster health check
- 🎯 `optimize_config` - Get cluster optimization recommendations

### ⏰ Job Scheduling
- 📅 `schedule_job` - Configure job scheduling parameters

## 📚 Examples

Ready-to-run examples in the `examples/` directory:

- 🎯 `simple_job.py` - Basic Ray job example (start here!)
- 🌐 `multi_node_cluster.py` - Multi-node cluster with worker management
- 🎭 `actor_example.py` - Actor-based stateful computation
- 🔄 `data_pipeline.py` - Scalable data processing pipeline
- 🤖 `distributed_training.py` - Distributed machine learning
- 🎼 `workflow_orchestration.py` - Complex workflow orchestration

## 🔌 Claude Desktop Integration

### ⚡ Quick Setup

1. **🎯 Choose your installation method:**

   **Option A: uvx (Easiest! 🚀)**
   ```bash
   # No installation needed! uvx handles everything
   ```

   **Option B: Development setup**
   ```bash
   git clone <repository-url>
   cd ray-mcp
   uv sync
   ```

2. **⚙️ Add to Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

   **For uvx installation:**
   ```json
   {
     "mcpServers": {
       "ray-mcp": {
         "command": "uvx",
         "args": ["ray-mcp-server"]
       }
     }
   }
   ```

   **For development setup:**
   ```json
   {
     "mcpServers": {
       "ray-mcp": {
         "command": "/opt/homebrew/bin/uv",
         "args": ["run", "--directory", "/absolute/path/to/ray-mcp", "ray-mcp-server"]
       }
     }
   }
   ```

3. **🌐 For remote Ray clusters** (like Kubernetes), add port-forwarding and environment:
   ```bash
   kubectl port-forward -n ray-cluster ray-cluster-kuberay-head-<pod-id> 10001:10001
   ```
   
   **For uvx:**
   ```json
   {
     "mcpServers": {
       "ray-mcp": {
         "command": "uvx",
         "args": ["ray-mcp-server"],
         "env": {
           "RAY_ADDRESS": "ray://127.0.0.1:10001"
         }
       }
     }
   }
   ```

4. **🔄 Restart Claude Desktop** and test with: *"What Ray tools are available?"* 🎉

### 📖 Detailed Setup Guides

- 🚢 **Kubernetes Ray Clusters**: See [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)
- ⚙️ **Configuration Examples**: See [docs/config/](docs/config/)
- 👨‍💻 **Development Guide**: See [CLAUDE.md](CLAUDE.md)

## 🛠️ Development

### 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/test_mcp_tools.py
uv run pytest tests/test_multi_node_cluster.py
uv run pytest tests/test_e2e_integration.py
```

### ✨ Code Quality

```bash
# Run linting and formatting checks
make lint

# Format code automatically
make format

# Run type checking
uv run pyright ray_mcp/

# Run code formatting
uv run black ray_mcp/
uv run isort ray_mcp/
```

## 📄 License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

This software includes code originally from [ray-mcp](https://github.com/pradeepiyer/ray-mcp) licensed under the MIT License. See [NOTICE](NOTICE) file for full attribution details.

---

**Ready to supercharge your Ray workflows? Get started now!** 🚀✨ 