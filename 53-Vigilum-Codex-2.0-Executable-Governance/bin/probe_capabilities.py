#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Tri-State Capability Health Probe (E6 / Invariant U-006).

Deterministic probe enforcing the tripartite capability model:
  PASS              observable and functioning normally
  FAIL              observable and failing (syntax error, broken dependency)
  UNKNOWN-CONFINED  unobservable / uninstantiated (P3: UNKNOWN != PASS)

Strict doctrine: an unobservable tool is ALWAYS marked UNKNOWN-CONFINED
and NEVER coerced into a PASS or PASS_UNOBSERVED.

Generates: runtime/capability_health.json
Exit: 0 when required capabilities are PASS and optional are PASS or UNKNOWN-CONFINED.
      66 when a critical capability is UNKNOWN.
      1 when any capability is FAIL.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

REQUIRED_DEFAULT: list[dict[str, Any]] = [
    {"name": "python3", "cmd": "python3", "probe": ["-c", "import sys"]},
    {"name": "bash", "cmd": "bash", "probe": ["--version"]},
    {"name": "git", "cmd": "git", "probe": ["--version"]},
]

OPTIONAL_DEFAULT: list[dict[str, Any]] = [
    {"name": "jq", "cmd": "jq", "probe": ["--version"]},
    {"name": "pyright", "cmd": "pyright", "probe": ["--version"]},
    {"name": "flake8", "cmd": "flake8", "probe": ["--version"]},
    {"name": "pyyaml", "cmd": "python3", "probe": ["-c", "import yaml"]},
]


def _smoke(cmd: str, probe_args: list[str]) -> int | None:
    """Return exit code of the smoke test, or None if the command is absent."""
    resolved = shutil.which(cmd)
    if resolved is None:
        return None
    try:
        proc = subprocess.run([resolved, *probe_args], capture_output=True, text=True,
                              timeout=30, check=False)
        return proc.returncode
    except (OSError, subprocess.SubprocessError):
        return 1


def probe_tool(tool: dict[str, Any]) -> dict[str, Any]:
    code = _smoke(str(tool["cmd"]), [str(a) for a in tool.get("probe", [])])
    if code is None:
        status = "UNKNOWN-CONFINED"
    elif code == 0:
        status = "PASS"
    else:
        status = "FAIL"
    return {
        "capability": tool["name"],
        "command": tool["cmd"],
        "status": status,
        "smoke_exit_code": code,
        "note": "non observable — jamais assimilé à PASS (P3)" if status == "UNKNOWN-CONFINED"
                else ("dégradé — interdit de valider implicitement (P3)" if status == "FAIL" else ""),
    }


def probe_set(required: list[dict[str, Any]], optional: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    results = [probe_tool(tool) for tool in required + optional]
    by_name = {r["capability"]: r["status"] for r in results}
    required_names = {t["name"] for t in required}

    required_fail = [n for n in required_names if by_name.get(n) == "FAIL"]
    required_unknown = [n for n in required_names if by_name.get(n) == "UNKNOWN-CONFINED"]
    any_fail = [r["capability"] for r in results if r["status"] == "FAIL"]

    if required_fail:
        verdict, exit_code = "FAIL", EXIT_FAIL
    elif required_unknown or any_fail:
        verdict, exit_code = "UNKNOWN", EXIT_UNKNOWN
    else:
        verdict, exit_code = "PASS", EXIT_PASS

    return exit_code, {
        "protocol": "Invariant U-006 — Sonde Tri-State",
        "version": "2.1.1",
        "verdict": verdict,
        "exit_code": exit_code,
        "required": sorted(required_names),
        "required_fail": required_fail,
        "required_unknown": required_unknown,
        "optional_degraded": [r["capability"] for r in results if r["status"] != "PASS"
                              and r["capability"] not in required_names],
        "capabilities": results,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "note": "UNKNOWN-CONFINED est un statut formel documenté — jamais un PASS implicite (P3).",
    }


def _parse_tools(specs: list[str]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for spec in specs:
        parts = spec.split("=", 1)
        name = parts[0].strip()
        cmd = parts[1].strip() if len(parts) > 1 else name
        tools.append({"name": name, "cmd": cmd, "probe": ["--version"]})
    return tools


def main() -> int:
    parser = argparse.ArgumentParser(description="Tri-state capability probe (U-006)")
    parser.add_argument("--root", type=Path, default=Path("."), help="Workspace root (evidence target)")
    parser.add_argument("--tool", action="append", default=[], help="Probe a single capability (name[=cmd])")
    parser.add_argument("--required", action="append", default=[], help="Required capability (name[=cmd])")
    parser.add_argument("--optional", action="append", default=[], help="Optional capability (name[=cmd])")
    args = parser.parse_args()

    if args.tool:
        required = _parse_tools(args.tool)
        optional: list[dict[str, Any]] = []
    else:
        required = _parse_tools(args.required) if args.required else list(REQUIRED_DEFAULT)
        optional = _parse_tools(args.optional) if args.optional else list(OPTIONAL_DEFAULT)

    exit_code, result = probe_set(required, optional)

    root = args.root.resolve()
    runtime_dir = root / "runtime"
    try:
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "capability_health.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["evidence"] = str(runtime_dir / "capability_health.json")
    except OSError as exc:
        result["evidence_error"] = str(exc)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
