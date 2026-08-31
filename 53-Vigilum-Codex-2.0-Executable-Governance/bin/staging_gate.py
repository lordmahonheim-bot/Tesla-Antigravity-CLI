#!/usr/bin/env python3
"""Vigilum Codex 2.1 — Double-Track Public Staging Gate (E2).

Deterministic enforcement of the RETEX corrective action
"Double Track Staging Public ($N+1$)": every sealing operation requires the
explicit inspection of the public registry ``MVP-GITHUB/`` and the computation
of milestone $N+1$ strictly from that public registry (Gravure sur Marbre,
Phase 4 — décorrélation taxonomique).

Sub-commands
------------
next-milestone --registry <MVP-GITHUB>     Compute N+1 from the public registry.
verify --registry <MVP-GITHUB> --milestone N
    Material check of milestone N: module directory exists, canonical README
    present (badge + Objective + Installation sections — English strict),
    at least one engineering sub-directory. Fail-closed otherwise.
git-status --repo <dir>                    Informational git status snapshot.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXIT_PASS = 0
EXIT_BLOCKED = 1
EXIT_USAGE = 64
EXIT_UNKNOWN = 66

_MILESTONE_RE = re.compile(r"^(\d+)-")


def registry_milestones(registry: Path) -> list[int]:
    if not registry.is_dir():
        raise UnknownState(f"REGISTRY_MISSING:{registry}")
    milestones: list[int] = []
    for entry in registry.iterdir():
        match = _MILESTONE_RE.match(entry.name) if entry.is_dir() else None
        if match:
            milestones.append(int(match.group(1)))
    return sorted(milestones)


class UnknownState(RuntimeError):
    """Raised when the observable state prevents a deterministic answer."""


def cmd_next_milestone(registry: Path) -> tuple[int, dict]:
    try:
        milestones = registry_milestones(registry)
    except UnknownState as exc:
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN", "reason": str(exc), "registry": str(registry)}
    last = milestones[-1] if milestones else 0
    return EXIT_PASS, {
        "verdict": "PASS",
        "registry": str(registry),
        "milestones_public": milestones,
        "last_milestone": last,
        "next_milestone": last + 1,
        "note": "N+1 is computed strictly from the public registry (décorrélation "
                "taxonomique — Gravure sur Marbre Phase 4).",
    }


def cmd_verify(registry: Path, milestone: int) -> tuple[int, dict]:
    try:
        milestones = registry_milestones(registry)
    except UnknownState as exc:
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN", "reason": str(exc), "registry": str(registry)}

    matches = sorted(entry for entry in registry.iterdir() if entry.is_dir() and _MILESTONE_RE.match(entry.name)
                     and int(_MILESTONE_RE.match(entry.name).group(1)) == milestone)
    if not matches:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "MILESTONE_ABSENT_FROM_PUBLIC_REGISTRY",
            "milestone": milestone,
            "registry": str(registry),
            "known_milestones": milestones,
        }
    if len(matches) > 1:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "MILESTONE_AMBIGUOUS_MULTIPLE_DIRS",
            "milestone": milestone,
            "matches": [str(m) for m in matches],
        }

    module_dir = matches[0]
    problems: list[str] = []

    readme = module_dir / "README.md"
    if not readme.is_file():
        problems.append("README_MISSING")
    else:
        text = readme.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            problems.append("README_EMPTY")
        if "![Status]" not in text:
            problems.append("README_BADGE_STATUS_MISSING")
        if "## Objective" not in text:
            problems.append("README_SECTION_OBJECTIVE_MISSING")
        if "## Installation" not in text:
            problems.append("README_SECTION_INSTALLATION_MISSING")
        if "## Security" not in text and "Security and Governance" not in text:
            problems.append("README_SECTION_SECURITY_MISSING")

    engineering_dirs = [name for name in ("core", "bin", "src", "tests", "schemas", "docs", "scripts")
                        if (module_dir / name).is_dir()]
    if not engineering_dirs:
        problems.append("MODULE_ENGINEERING_DIRS_MISSING")

    if problems:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "PUBLIC_STAGING_INCOMPLETE",
            "milestone": milestone,
            "module": module_dir.name,
            "violations": problems,
            "note": "Phase 4 (Public Staging) is mandatory before any mission closure "
                    "for public chantiers.",
        }

    return EXIT_PASS, {
        "verdict": "PASS",
        "milestone": milestone,
        "module": module_dir.name,
        "readme": str(readme),
        "engineering_dirs": engineering_dirs,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def cmd_git_status(repo: Path) -> tuple[int, dict]:
    if not (repo / ".git").exists() and not (repo / ".git").is_dir():
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN", "reason": "NOT_A_GIT_REPOSITORY", "repo": str(repo)}
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=str(repo), capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return EXIT_UNKNOWN, {"verdict": "UNKNOWN", "reason": f"GIT_STATUS_ERROR:{exc}", "repo": str(repo)}
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    untracked = sum(1 for line in lines if line.startswith("??"))
    modified = sum(1 for line in lines if line.startswith(" M") or line.startswith("M "))
    staged = sum(1 for line in lines if line.startswith(("A ", "M ", "D ", "R ")))
    return EXIT_PASS, {
        "verdict": "INFO",
        "repo": str(repo),
        "porcelain_lines": len(lines),
        "untracked": untracked,
        "modified": modified,
        "staged": staged,
        "note": "Informational snapshot — an INFO verdict is never a PASS "
                "(Invariant P4: absence of error is not success).",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Double-Track Public Staging Gate (Phase 4, $N+1$)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_next = sub.add_parser("next-milestone", help="Compute N+1 from the public registry")
    p_next.add_argument("--registry", type=Path, required=True)
    p_next.set_defaults(func=lambda a: cmd_next_milestone(a.registry))

    p_verify = sub.add_parser("verify", help="Material verification of milestone N public staging")
    p_verify.add_argument("--registry", type=Path, required=True)
    p_verify.add_argument("--milestone", type=int, required=True)
    p_verify.set_defaults(func=lambda a: cmd_verify(a.registry, a.milestone))

    p_status = sub.add_parser("git-status", help="Informational git status snapshot")
    p_status.add_argument("--repo", type=Path, required=True)
    p_status.set_defaults(func=lambda a: cmd_git_status(a.repo))

    args = parser.parse_args()
    code, result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
