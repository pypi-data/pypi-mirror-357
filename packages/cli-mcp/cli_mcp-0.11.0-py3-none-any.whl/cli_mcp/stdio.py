from __future__ import annotations
import asyncio
import json
import os
import re
import signal
import sys
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

URL_REGEX = re.compile(r"https?://(?:127\.0\.0\.1|localhost|0\.0\.0\.0):\d+/?.*")


async def _stdio_call(
    process: asyncio.subprocess.Process,
    method: str,
    params: Dict[str, Any] | None = None,
    request_id: int = 1,
) -> Any:
    """Send a JSON-RPC request over stdio and get the response."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params is not None:
        request["params"] = params

    # Send request
    request_json = json.dumps(request) + "\n"
    if process.stdin:
        process.stdin.write(request_json.encode('utf-8'))
        await process.stdin.drain()

    # Read response
    if process.stdout:
        response_line = await process.stdout.readline()
        response_data = response_line.decode('utf-8').strip()

        if not response_data:
            raise RuntimeError("No response received from stdio server")

        try:
            response = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {e}")

        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            raise RuntimeError(f"JSON-RPC error: {error_msg}")

        return response.get("result")

    raise RuntimeError("Process stdout not available")


async def detect_server_url(
    command: str,
    args: List[str],
    env: Dict[str, str] | None = None,
    timeout: float = 15.0,
) -> Optional[str]:
    """Spawn a process and try to detect a server URL from its output.

    Returns the detected URL or None if no URL found within timeout.
    """
    # Prepare environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    process = None
    try:
        # Start the process
        process = await asyncio.create_subprocess_exec(
            command,
            *args,
            env=process_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def read_stream(stream) -> Optional[str]:
            """Read from a stream and look for URLs."""
            try:
                while True:
                    line = await stream.readline()
                    if not line:
                        break

                    text = line.decode('utf-8', errors='ignore')
                    match = URL_REGEX.search(text)
                    if match:
                        return match.group(0)
            except Exception:
                pass
            return None

        # Read from both stdout and stderr concurrently
        try:
            url = await asyncio.wait_for(
                asyncio.gather(
                    read_stream(process.stdout),
                    read_stream(process.stderr),
                    return_exceptions=True
                ),
                timeout=timeout
            )

            # Check results from both streams
            for result in url:
                if isinstance(result, str) and result:
                    return result

        except asyncio.TimeoutError:
            pass

        return None

    except Exception as e:
        logger.debug(f"Error detecting server URL: {e}")
        return None

    finally:
        # Clean up the process
        if process is not None:
            try:
                if process.returncode is None:  # Process is still running
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=3.0)
                    except asyncio.TimeoutError:
                        process.kill()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=1.0)
                        except asyncio.TimeoutError:
                            pass  # Give up gracefully
            except Exception:
                pass


async def spawn_stdio_server(
    command: str,
    args: List[str],
    env: Dict[str, str] | None = None,
) -> asyncio.subprocess.Process:
    """Spawn a stdio MCP server process."""
    # Prepare environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    process = await asyncio.create_subprocess_exec(
        command,
        *args,
        env=process_env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    return process


async def list_tools_stdio(
    command: str,
    args: List[str],
    env: Dict[str, str] | None = None,
) -> List[Dict[str, Any]]:
    """List tools from a stdio MCP server."""
    process = await spawn_stdio_server(command, args, env)

    try:
        # Initialize the server
        await _stdio_call(
            process,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "cli-mcp",
                    "version": "0.1.1"
                }
            },
            request_id=1,
        )

        # Get tools list
        result = await _stdio_call(process, "tools/list", request_id=2)
        tools = result.get("tools", []) if result else []

        return tools

    finally:
        # Clean up the process
        try:
            if process.stdin:
                process.stdin.close()
                await process.stdin.wait_closed()

            if process.returncode is None:  # Process is still running
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    process.kill()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        pass  # Give up gracefully
        except Exception:
            pass


async def call_tool_stdio(
    command: str,
    args: List[str],
    tool_name: str,
    tool_args: Dict[str, Any],
    env: Dict[str, str] | None = None,
) -> Any:
    """Call a tool on a stdio MCP server."""
    process = await spawn_stdio_server(command, args, env)

    try:
        # Initialize the server
        await _stdio_call(
            process,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "cli-mcp",
                    "version": "0.1.1"
                }
            },
            request_id=1,
        )

        # Call the tool
        result = await _stdio_call(
            process,
            "tools/call",
            {"name": tool_name, "arguments": tool_args},
            request_id=2,
        )

        return result

    finally:
        # Clean up the process
        try:
            if process.stdin:
                process.stdin.close()
                await process.stdin.wait_closed()

            if process.returncode is None:  # Process is still running
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    process.kill()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        pass  # Give up gracefully
        except Exception:
            pass