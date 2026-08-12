import os
from mcp.server.fastmcp import FastMCP
from e2b import Sandbox

# Initialize FastMCP server
mcp = FastMCP("tesla_forge_mcp")

# Global reference to the active sandbox
active_sandbox: Sandbox | None = None

@mcp.tool()
def create_forge() -> str:
    """Instantiates an E2B Sandbox with the tesla-forge-v1 template."""
    global active_sandbox
    if active_sandbox is not None:
        return "Sandbox already exists."
    
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        return "E2B_API_KEY environment variable is missing."

    try:
        active_sandbox = Sandbox(
            template="tesla-forge-v1",
            api_key=api_key,
            timeout=300, # 5 minutes timeout
        )
        return f"Forge created successfully. Sandbox ID: {active_sandbox.id}"
    except Exception as e:
        return f"Failed to create forge: {e}"

@mcp.tool()
def forge_exec(command: str) -> str:
    """Executes a shell command in the active sandbox."""
    global active_sandbox
    if active_sandbox is None:
        return "No active forge sandbox. Call create_forge first."
    
    try:
        process = active_sandbox.process.start(command)
        process.wait()
        output = process.stdout
        error = process.stderr
        res = f"Stdout:\n{output}\n"
        if error:
            res += f"Stderr:\n{error}\n"
        return res
    except Exception as e:
        return f"Execution failed: {e}"

@mcp.tool()
def forge_write_file(path: str, content: str) -> str:
    """Writes a file to the specified path in the active sandbox."""
    global active_sandbox
    if active_sandbox is None:
        return "No active forge sandbox. Call create_forge first."
    
    try:
        active_sandbox.filesystem.write(path, content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Failed to write file: {e}"

@mcp.tool()
def forge_read_file(path: str) -> str:
    """Reads a file from the active sandbox."""
    global active_sandbox
    if active_sandbox is None:
        return "No active forge sandbox. Call create_forge first."
    
    try:
        content = active_sandbox.filesystem.read(path)
        return content
    except Exception as e:
        return f"Failed to read file: {e}"

@mcp.tool()
def forge_sync_to_midgard(remote_path: str, local_path: str) -> str:
    """Downloads a file from the sandbox and saves it locally to MIDGARD."""
    global active_sandbox
    if active_sandbox is None:
        return "No active forge sandbox. Call create_forge first."
    
    try:
        content_bytes = active_sandbox.filesystem.read_bytes(remote_path)
        with open(local_path, "wb") as f:
            f.write(content_bytes)
        return f"Successfully synced {remote_path} to {local_path}"
    except AttributeError:
        try:
            content_str = active_sandbox.filesystem.read(remote_path)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content_str)
            return f"Successfully synced {remote_path} to {local_path} as text."
        except Exception as inner_e:
            return f"Failed to sync file as text: {inner_e}"
    except Exception as e:
        return f"Failed to sync file: {e}"

@mcp.tool()
def forge_destroy() -> str:
    """Destroys the active sandbox."""
    global active_sandbox
    if active_sandbox is None:
        return "No active forge sandbox."
    
    try:
        active_sandbox.kill()
        active_sandbox = None
        return "Forge destroyed successfully."
    except Exception as e:
        return f"Failed to destroy forge: {e}"

if __name__ == "__main__":
    mcp.run()
