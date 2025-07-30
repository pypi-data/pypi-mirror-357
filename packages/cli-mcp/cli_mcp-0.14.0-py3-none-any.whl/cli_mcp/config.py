from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict


def find_config(config_path: str | None = None) -> Path:
    """Find MCP configuration file in priority order:
    1. --configpath PATH if supplied
    2. ./.cursor/mcp.json in current working directory
    3. ./mcp.json in current working directory
    4. Search up parent directories for .cursor/mcp.json
    5. Search up parent directories for mcp.json
    6. ~/.cursor/mcp.json in user home directory
    7. ~/mcp.json in user home directory
    """
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return path

    # Start from current working directory
    current_dir = Path.cwd()

    # Check current directory first
    cursor_config = current_dir / ".cursor/mcp.json"
    if cursor_config.exists():
        return cursor_config

    global_config = current_dir / "mcp.json"
    if global_config.exists():
        return global_config

    # Search up parent directories
    for parent in current_dir.parents:
        cursor_config = parent / ".cursor/mcp.json"
        if cursor_config.exists():
            return cursor_config

        global_config = parent / "mcp.json"
        if global_config.exists():
            return global_config

    # Check user home directory
    home_dir = Path.home()
    home_cursor_config = home_dir / ".cursor/mcp.json"
    if home_cursor_config.exists():
        return home_cursor_config

    home_global_config = home_dir / "mcp.json"
    if home_global_config.exists():
        return home_global_config

    raise FileNotFoundError("No MCP config found. Searched current directory, parent directories, and home directory for .cursor/mcp.json or mcp.json")


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Load and parse MCP configuration file."""
    config_file = find_config(config_path)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_file}: {e}")

    if "mcpServers" not in config:
        raise ValueError(f"Config file {config_file} missing 'mcpServers' section")

    return config


def normalize_server_config(name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize server configuration to standard format."""
    # Accept both 'url' and 'serverUrl' for remote servers
    if "url" in server_config:
        server_config["serverUrl"] = server_config["url"]

    # Ensure we have the required fields
    normalized = {
        "name": name,
        **server_config
    }

    return normalized


def is_remote_server(server_config: Dict[str, Any]) -> bool:
    """Check if server configuration is for a remote server."""
    return "url" in server_config or "serverUrl" in server_config


def is_mcp_remote_proxy(server_config: Dict[str, Any]) -> bool:
    """Check if server uses mcp-remote as a proxy to remote server."""
    if "args" not in server_config:
        return False

    args = server_config["args"]
    return isinstance(args, list) and "mcp-remote" in args


def prepare_env_vars(env_config: Dict[str, str] | None) -> Dict[str, str]:
    """Prepare environment variables for the spawned process.

    Uses values from config file, with optional override from os.environ.
    Returns a dict of env var names to their values for the spawned process.
    """
    if not env_config:
        return {}

    resolved_env = {}

    for var_name, config_value in env_config.items():
        # Use value from terminal environment if set, otherwise use config value
        actual_value = os.environ.get(var_name, config_value)
        resolved_env[var_name] = actual_value

    return resolved_env


def extract_env_headers(env: Dict[str, str] | None) -> Dict[str, str]:
    """Extract headers from environment variables for example commands.

    Converts typical API key env vars to header format:
    - *_API_KEY -> x-{name}-api-key
    - *_TOKEN -> Authorization: Bearer {value}
    """
    if not env:
        return {}

    headers = {}
    for key, value in env.items():
        key_lower = key.lower()
        if key_lower.endswith('_api_key'):
            # Convert CONTEXT7_API_KEY -> x-context7-api-key
            prefix = key_lower[:-8]  # Remove '_api_key'
            headers[f"x-{prefix}-api-key"] = value
        elif key_lower.endswith('_token'):
            # Convert *_TOKEN -> Authorization header
            headers["Authorization"] = f"Bearer {value}"

    return headers