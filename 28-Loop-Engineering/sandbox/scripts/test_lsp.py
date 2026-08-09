#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_lsp.py — Test LSP server diagnostics and definition lookup.

import asyncio
import sys
import os
import json

# Ensure parent or venv imports are resolved
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from karellen_lsp_mcp.daemon_client import DaemonClient

async def main():
    print("[*] Connecting to karellen-lsp-mcp daemon...")
    client = DaemonClient()
    await client.connect()
    print("[+] Connected successfully!")
    
    project_path = "/home/lord-mahonheim/bifrost/tesla"
    print(f"[*] Registering project at: {project_path}")
    reg_result = await client.send_request("register_project", {
        "project_path": project_path,
        "language": "python",
        "timeout": 120
    })
    project_id = reg_result["project_id"]
    print(f"[+] Project registered. Project ID: {project_id}")
    
    file_path = os.path.join(project_path, "memory/update_session_history.py")
    print(f"[*] Running diagnostics for file: {file_path}")
    diag_result = await client.send_request("lsp_diagnostics", {
        "project_id": project_id,
        "file_path": file_path,
        "timeout": 120
    })
    print("[+] Diagnostics result:")
    print(json.dumps(diag_result, indent=2))
    
    # Try reading definition of datetime at line 6, char 26 of update_session_history.py (from datetime import datetime)
    print(f"[*] Running definition lookup at line 6, character 26 of {file_path}")
    def_result = await client.send_request("lsp_read_definition", {
        "project_id": project_id,
        "file_path": file_path,
        "line": 6,
        "character": 26,
        "timeout": 120
    })
    print("[+] Definition lookup result:")
    print(json.dumps(def_result, indent=2))
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
