#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01-LSP-Self-Healing: LSP Server Diagnostics Client
Checks local Python scripts health using karellen-lsp-mcp daemon
"""
import asyncio
import sys
import os
import json

# Dynamic local import resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from karellen_lsp_mcp.daemon_client import DaemonClient
except ImportError:
    print("[-] Error: karellen_lsp_mcp not available in current environment.")
    sys.exit(1)

async def main():
    print("[*] Connecting to karellen-lsp-mcp daemon...")
    client = DaemonClient()
    await client.connect()
    print("[+] Successfully connected!")
    
    # Dynamic workspace resolution
    project_path = os.environ.get("TESLA_WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    print(f"[*] Registering project under: {project_path}")
    reg_result = await client.send_request("register_project", {
        "project_path": project_path,
        "language": "python",
        "timeout": 120
    })
    project_id = reg_result["project_id"]
    print(f"[+] Project registered. Project ID: {project_id}")
    
    # Dynamic target file
    file_path = os.path.join(project_path, "03-Memory-MLT", "update_session_history.py")
    if not os.path.exists(file_path):
        # Fallback to local test script
        file_path = os.path.abspath(__file__)
        
    print(f"[*] Querying LSP diagnostics on: {file_path}")
    diag_result = await client.send_request("lsp_diagnostics", {
        "project_id": project_id,
        "file_path": file_path,
        "timeout": 120
    })
    print("[+] LSP Diagnostics received:")
    print(json.dumps(diag_result, indent=2))
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
