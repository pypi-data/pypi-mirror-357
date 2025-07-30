#!/usr/bin/env python3
"""
System Diagnostics MCP Server

A comprehensive system diagnostics and monitoring server for Ubuntu systems.
Provides tools for checking system health, network connectivity, processes, and more.
"""

import json
import logging
import os
import platform
import pwd
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
import requests
from mcp.server import FastMCP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("system-diag-mcp")

# Initialize the FastMCP server
mcp = FastMCP("system-diag-mcp")


def run_command(cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
    """Run a system command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return {
            "success": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }


# Core Diagnostics Tools
@mcp.tool()
async def check_port(host: str, port: int) -> str:
    """Test if a TCP port is open on a remote host.
    
    Args:
        host: Hostname or IP address
        port: Port number to check
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            message = f"Port {port} on {host} is OPEN"
            status = "open"
        else:
            message = f"Port {port} on {host} is CLOSED or FILTERED"
            status = "closed"
            
        return json.dumps({
            "host": host,
            "port": port,
            "status": status,
            "message": message
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to check port: {str(e)}"
        }, indent=2)


@mcp.tool()
async def ping_host(host: str, count: int = 4) -> str:
    """ICMP ping to a remote host.
    
    Args:
        host: Hostname or IP address to ping
        count: Number of pings to send
    """
    result = run_command(["ping", "-c", str(count), host])
    return json.dumps(result, indent=2)


@mcp.tool()
async def dns_lookup(domain: str, record_type: str = "A") -> str:
    """Resolve DNS records for a domain.
    
    Args:
        domain: Domain name to resolve
        record_type: DNS record type (A, AAAA, MX, etc.)
    """
    result = run_command(["dig", "+short", domain, record_type])
    return json.dumps(result, indent=2)


@mcp.tool()
async def http_check(url: str, timeout: int = 10) -> str:
    """HTTP status check for a URL.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
    """
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        result = {
            "url": url,
            "status_code": response.status_code,
            "status_text": response.reason,
            "response_time": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
            "final_url": response.url
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"HTTP check failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def traceroute_host(host: str, max_hops: int = 30) -> str:
    """Trace network path to a host.
    
    Args:
        host: Hostname or IP address to trace route to
        max_hops: Maximum number of hops
    """
    result = run_command(["traceroute", "-m", str(max_hops), host], timeout=60)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_uptime() -> str:
    """Return system uptime information."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    
    result = {
        "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
        "uptime_seconds": int(uptime_seconds),
        "uptime_formatted": uptime_str
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_sys_info() -> str:
    """Get basic system information (CPU, memory, disk)."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    result = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        },
        "load_average": os.getloadavg()
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_hostname() -> str:
    """Retrieve machine hostname."""
    result = {
        "hostname": platform.node(),
        "fqdn": socket.getfqdn()
    }
    return json.dumps(result, indent=2)


# Service & Process Monitoring Tools
@mcp.tool()
async def list_processes(filter_name: str = "", sort_by: str = "cpu") -> str:
    """List running processes.
    
    Args:
        filter_name: Filter processes by name pattern
        sort_by: Sort by: cpu, memory, pid, name
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            if filter_name and filter_name.lower() not in pinfo['name'].lower():
                continue
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort processes
    if sort_by == "cpu":
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    elif sort_by == "pid":
        processes.sort(key=lambda x: x['pid'])
    elif sort_by == "name":
        processes.sort(key=lambda x: x['name'].lower())
    
    return json.dumps(processes[:50], indent=2)


@mcp.tool()
async def list_services(state: str = "all") -> str:
    """List systemd services.
    
    Args:
        state: Filter by state: active, inactive, failed, all
    """
    cmd = ["systemctl", "list-units", "--type=service", "--no-pager"]
    if state != "all":
        cmd.extend(["--state", state])
    
    result = run_command(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
async def service_status(service_name: str) -> str:
    """Get status of a specific service.
    
    Args:
        service_name: Name of the service to check
    """
    result = run_command(["systemctl", "status", service_name, "--no-pager"])
    return json.dumps(result, indent=2)


@mcp.tool()
async def read_journal(unit: str = "", lines: int = 50, since: str = "today") -> str:
    """Fetch latest logs for a systemd unit or tag.
    
    Args:
        unit: Systemd unit name
        lines: Number of lines to show
        since: Show logs since (e.g., '1 hour ago', 'today')
    """
    cmd = ["journalctl", "--no-pager", "-n", str(lines), "--since", since]
    if unit:
        cmd.extend(["-u", unit])
    
    result = run_command(cmd)
    return json.dumps(result, indent=2)


@mcp.tool()
async def cron_list() -> str:
    """Show cron jobs for current user."""
    result = run_command(["crontab", "-l"])
    return json.dumps(result, indent=2)


# Disk & Memory Tools
@mcp.tool()
async def check_disk_usage(path: str = "/") -> str:
    """Get disk usage summary.
    
    Args:
        path: Specific path to check
    """
    result = run_command(["df", "-h", path])
    
    # Also get detailed info using psutil
    try:
        disk_usage = psutil.disk_usage(path)
        detailed = {
            "path": path,
            "total": disk_usage.total,
            "used": disk_usage.used,
            "free": disk_usage.free,
            "percent": (disk_usage.used / disk_usage.total) * 100
        }
        if isinstance(result, dict):
            result["detailed"] = detailed
    except Exception:
        pass
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def check_memory() -> str:
    """Get RAM and swap usage information."""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    result = {
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
            "active": memory.active,
            "inactive": memory.inactive,
            "buffers": memory.buffers,
            "cached": memory.cached,
            "shared": memory.shared
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def check_inode_usage() -> str:
    """Get filesystem inode statistics."""
    result = run_command(["df", "-i"])
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_mounts() -> str:
    """List mounted volumes."""
    result = run_command(["mount"])
    
    # Also get mount info from psutil
    try:
        mount_points = psutil.disk_partitions()
        detailed_mounts = []
        for partition in mount_points:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                detailed_mounts.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": (usage.used / usage.total) * 100 if usage.total > 0 else 0
                })
            except PermissionError:
                detailed_mounts.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "error": "Permission denied"
                })
        
        if isinstance(result, dict):
            result["detailed_mounts"] = detailed_mounts
    except Exception:
        pass
    
    return json.dumps(result, indent=2)


# Network & Ports Tools
@mcp.tool()
async def list_open_ports(protocol: str = "all") -> str:
    """Show open TCP/UDP ports.
    
    Args:
        protocol: Filter by protocol: tcp, udp, all
    """
    connections = psutil.net_connections(kind='inet')
    open_ports = []
    
    for conn in connections:
        if conn.status == psutil.CONN_LISTEN:
            proto = "tcp" if conn.type == socket.SOCK_STREAM else "udp"
            if protocol != "all" and proto != protocol:
                continue
            
            try:
                process = psutil.Process(conn.pid) if conn.pid else None
                process_name = process.name() if process else "unknown"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
            
            open_ports.append({
                "protocol": proto,
                "local_address": conn.laddr.ip if conn.laddr else "",
                "local_port": conn.laddr.port if conn.laddr else 0,
                "pid": conn.pid,
                "process": process_name
            })
    
    return json.dumps(open_ports, indent=2)


@mcp.tool()
async def check_firewall_status() -> str:
    """Get UFW/iptables firewall status."""
    # Check UFW status
    ufw_result = run_command(["ufw", "status", "verbose"])
    
    # Check iptables
    iptables_result = run_command(["iptables", "-L", "-n"])
    
    result = {
        "ufw": ufw_result,
        "iptables": iptables_result
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_network_interfaces() -> str:
    """List network interfaces with IP, MAC, and link state."""
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    result = {}
    for interface, addresses in interfaces.items():
        interface_info = {
            "addresses": [],
            "stats": stats.get(interface, {})._asdict() if interface in stats else {}
        }
        
        for addr in addresses:
            addr_info = {
                "family": str(addr.family),
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
                "ptp": addr.ptp
            }
            interface_info["addresses"].append(addr_info)
        
        result[interface] = interface_info
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def check_bandwidth_usage() -> str:
    """Get network traffic statistics."""
    stats = psutil.net_io_counters(pernic=True)
    
    result = {}
    for interface, stat in stats.items():
        result[interface] = {
            "bytes_sent": stat.bytes_sent,
            "bytes_recv": stat.bytes_recv,
            "packets_sent": stat.packets_sent,
            "packets_recv": stat.packets_recv,
            "errin": stat.errin,
            "errout": stat.errout,
            "dropin": stat.dropin,
            "dropout": stat.dropout
        }
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def resolve_host(ip: str) -> str:
    """Reverse DNS lookup for IP address.
    
    Args:
        ip: IP address to resolve
    """
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        result = {
            "ip": ip,
            "hostname": hostname
        }
    except socket.herror as e:
        result = {
            "ip": ip,
            "error": str(e)
        }
    
    return json.dumps(result, indent=2)


@mcp.tool()
async def curl_url(url: str, follow_redirects: bool = True, timeout: int = 10) -> str:
    """GET request with curl, showing full headers.
    
    Args:
        url: URL to request
        follow_redirects: Follow redirects
        timeout: Request timeout in seconds
    """
    cmd = ["curl", "-I", "-s", "-S", "--max-time", str(timeout)]
    if follow_redirects:
        cmd.append("-L")
    cmd.append(url)
    
    result = run_command(cmd)
    return json.dumps(result, indent=2)


# Security & Access Tools
@mcp.tool()
async def list_users() -> str:
    """List local users."""
    users = []
    for user in pwd.getpwall():
        users.append({
            "username": user.pw_name,
            "uid": user.pw_uid,
            "gid": user.pw_gid,
            "home": user.pw_dir,
            "shell": user.pw_shell,
            "gecos": user.pw_gecos
        })
    
    return json.dumps(users, indent=2)


@mcp.tool()
async def last_logins(count: int = 20) -> str:
    """Show last login attempts.
    
    Args:
        count: Number of entries to show
    """
    result = run_command(["last", "-n", str(count)])
    return json.dumps(result, indent=2)


@mcp.tool()
async def check_sudoers() -> str:
    """Show who can use sudo."""
    # Check who's in sudo group
    sudo_group = run_command(["getent", "group", "sudo"])
    
    # Check sudoers file (requires sudo)
    sudoers = run_command(["sudo", "-l"])
    
    result = {
        "sudo_group": sudo_group,
        "sudoers": sudoers
    }
    return json.dumps(result, indent=2)


@mcp.tool()
async def who_is_logged_in() -> str:
    """Show current user sessions."""
    result = run_command(["who", "-a"])
    
    # Also get detailed user info
    try:
        users = psutil.users()
        detailed_users = []
        for user in users:
            detailed_users.append({
                "name": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": datetime.fromtimestamp(user.started).isoformat(),
                "pid": user.pid if hasattr(user, 'pid') else None
            })
        if isinstance(result, dict):
            result["detailed_users"] = detailed_users
    except Exception:
        pass
    
    return json.dumps(result, indent=2)


def main():
    """Run the server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
