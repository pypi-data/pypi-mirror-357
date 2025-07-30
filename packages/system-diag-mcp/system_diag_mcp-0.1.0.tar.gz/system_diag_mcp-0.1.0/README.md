# System Diagnostics MCP Server

A Model Context Protocol (MCP) server that provides comprehensive system diagnostics and monitoring capabilities for Ubuntu systems.

## Features

### 🧠 Core Diagnostics
- **check_port** – Test if a TCP port is open
- **ping_host** – ICMP ping to a remote host  
- **dns_lookup** – Resolve DNS records for a domain
- **http_check** – HTTP status check for a URL
- **traceroute_host** – Trace network path to host
- **get_uptime** – Return system uptime
- **get_sys_info** – Basic system info (CPU, memory, disk)
- **get_hostname** – Retrieve machine hostname

### ⚙️ Service & Process Monitoring
- **list_processes** – List running processes (like ps)
- **list_services** – List systemd or init services
- **service_status** – Status of a specific service
- **read_journal** – Fetch latest logs for a unit or tag
- **cron_list** – Show cron jobs for current user

### 📦 Disk & Memory
- **check_disk_usage** – Disk usage summary (like df)
- **check_memory** – RAM/Swap usage (like free)
- **check_inode_usage** – Filesystem inode stats
- **list_mounts** – Mounted volumes

### 🔌 Network & Ports
- **list_open_ports** – Show open TCP/UDP ports
- **check_firewall_status** – UFW/iptables summary
- **list_network_interfaces** – IP, MAC, link state
- **check_bandwidth_usage** – Network traffic stats
- **resolve_host** – Reverse DNS for IP address
- **curl_url** – GET request with curl, full headers

### 🔒 Security & Access
- **list_users** – Local users
- **last_logins** – Last login attempts
- **check_sudoers** – Who can sudo
- **who_is_logged_in** – Current sessions

## Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install system-diag-mcp
```

### Using pip

```bash
pip install system-diag-mcp
```

## Usage

### As a standalone server

```bash
system-diag-mcp
```

### With Claude Desktop

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "system-diag": {
      "command": "system-diag-mcp"
    }
  }
}
```

### With other MCP clients

The server runs on stdio and implements the full MCP protocol.

## Development

```bash
# Clone the repository
git clone <repository-url>
cd system-diag-mcp

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## Requirements

- Python 3.8+
- Ubuntu/Debian-based system
- Required system tools: `ping`, `dig`, `traceroute`, `systemctl`, `ps`, `df`, `free`, `curl`

## License

MIT License
