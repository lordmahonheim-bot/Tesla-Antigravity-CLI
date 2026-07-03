#!/usr/bin/env python3
# tesla-jules — Governed wrapper for Google Jules & Antigravity CLI
# Under the Vigilum Codex doctrine for Lord Mahonheim

import sys
import os
import subprocess
import re
import shutil

WORKSPACE = "/home/lord-mahonheim/bifrost/tesla"
JULES_BIN_PATH = os.path.expanduser("~/.npm-global/bin/jules")

def find_jules_bin():
    if os.path.exists(JULES_BIN_PATH):
        return JULES_BIN_PATH
    which_jules = shutil.which("jules")
    if which_jules:
        return which_jules
    print("[-] Error: jules binary not found in ~/.npm-global/bin/jules or PATH.")
    sys.exit(1)

def run_cmd(args, check=True):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check, cwd=WORKSPACE)
        return res.stdout.strip(), res.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"[-] Command failed: {' '.join(args)}")
        print(f"[-] Exit Code: {e.returncode}")
        print(f"[-] Stdout:\n{e.stdout}")
        print(f"[-] Stderr:\n{e.stderr}")
        sys.exit(e.returncode)

def get_git_repo():
    stdout, _ = run_cmd(["git", "remote", "get-url", "origin"])
    url = stdout.strip()
    # Support both SSH (git@github.com:owner/repo.git) and HTTPS (https://github.com/owner/repo.git)
    match = re.search(r'(?:git@github\.com:|https://github\.com/)([^/]+/[^/.]+)(?:\.git)?', url)
    if not match:
        print(f"[-] Error: Could not parse OWNER/REPOSITORY from remote URL: {url}")
        sys.exit(1)
    return match.group(1)

def assert_git_clean():
    stdout, _ = run_cmd(["git", "status", "--porcelain"])
    modified = [line for line in stdout.split("\n") if line.strip() and not line.startswith("??")]
    if modified:
        print("BLOCKED_GIT_NOT_CLEAN=1")
        print("REASON=Operational Jules actions require a clean working tree (no modified tracked files).")
        print("[-] Please commit or stash your changes before running this command.")
        sys.exit(1)

def print_jules_report():
    # Find all files modified or added in the working tree
    stdout, _ = run_cmd(["git", "status", "--porcelain", "--untracked-files=all"])
    modified_files = []
    for line in stdout.split("\n"):
        if not line.strip():
            continue
        # Extract filename (after status code, e.g. "M path/to/file")
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            modified_files.append(parts[1])

    report_found = False
    for filename in modified_files:
        filepath = os.path.join(WORKSPACE, filename)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Check for JULES_RESPONSE_TO_TESLA or Done_By=Jules
                if "JULES_RESPONSE_TO_TESLA" in content or "JULES_RESPONSE" in content or "Done_By=Jules" in content:
                    print(f"\n[+] Raw Jules Report extracted from {filename}:")
                    print("="*60)
                    # Extract the section
                    lines = content.split("\n")
                    printing = False
                    for line in lines:
                        if "JULES_RESPONSE_TO_TESLA" in line or "JULES_RESPONSE" in line:
                            printing = True
                        if printing:
                            print(line)
                            if "MAIN_RENDUE_A_MAHONHEIM" in line or "Main rendue" in line:
                                break
                    print("="*60)
                    report_found = True
            except Exception as e:
                print(f"[-] Failed to read file {filename} for report extraction: {e}")
    if not report_found:
        print("[!] Warning: No Jules-authored report (JULES_RESPONSE_TO_TESLA) found in applied modifications.")

def main():
    if len(sys.argv) < 2:
        print("Usage: tesla-jules [command] [args...]")
        print("Available Commands:")
        print("  login        Login to Google Labs account")
        print("  logout       Logout of Google Labs account")
        print("  repos        List connected repositories")
        print("  sessions     List active remote sessions")
        print("  mission      Create a remote session with explicit repository and allowlist")
        print("  pull         Rapatriement of session inside staging branch")
        sys.exit(1)

    cmd = sys.argv[1]
    jules_bin = find_jules_bin()

    if cmd == "login":
        subprocess.run([jules_bin, "login"])

    elif cmd == "logout":
        subprocess.run([jules_bin, "logout"])

    elif cmd == "repos":
        assert_git_clean()
        stdout, _ = run_cmd([jules_bin, "remote", "list", "--repo"])
        print(stdout)

    elif cmd == "sessions":
        assert_git_clean()
        stdout, _ = run_cmd([jules_bin, "remote", "list", "--session"])
        print(stdout)

    elif cmd == "mission":
        if len(sys.argv) < 3:
            print("Usage: tesla-jules mission \"your prompt here\"")
            sys.exit(1)
        prompt = sys.argv[2]
        assert_git_clean()
        repo = get_git_repo()
        
        # Format prompt with positive allowlist guidance to align with MVP 2
        structured_prompt = (
            f"You are Jules acting as a delegated remote agent.\n\n"
            f"Mission:\n{prompt}\n\n"
            f"Scope:\nOnly create or modify the files explicitly required for this task. "
            f"Inside the delivered files, you MUST write your own execution report under a section named "
            f"JULES_RESPONSE_TO_TESLA outlining what was done, what files were touched, and next steps.\n\n"
            f"Required markers:\n"
            f"ONLY_EXPECTED_FILE_CHANGED=1\n"
            f"JULES_WRITES_OWN_REPORT_IN_RESULT=1\n"
            f"Done_By=Jules\n"
            f"MAIN_RENDUE_A_MAHONHEIM=1"
        )
        
        print(f"[*] Dispatching mission to repository: {repo}...")
        subprocess.run([jules_bin, "remote", "new", "--repo", repo, "--session", structured_prompt])

    elif cmd == "pull":
        if len(sys.argv) < 3:
            print("Usage: tesla-jules pull <session_id>")
            sys.exit(1)
        session_id = sys.argv[2]
        assert_git_clean()
        
        # Step 1: Create staging branch
        branch_name = f"staging/jules_{session_id}"
        print(f"[*] Creating and switching to staging branch: {branch_name}...")
        run_cmd(["git", "checkout", "-b", branch_name])
        
        # Step 2: Pull and apply patch
        print(f"[*] Pulling remote session {session_id} and applying patch...")
        subprocess.run([jules_bin, "remote", "pull", "--session", session_id, "--apply"])
        
        # Step 3: Extract report
        print_jules_report()
        
        # Step 4: Output instructions
        print("\n[+] Pull and apply completed successfully in staging branch.")
        print(f"[*] Please run the diagnostics:")
        print(f"    1. Run pyright: `.venv/bin/pyright`")
        print(f"    2. Inspect changes: `git diff master`")
        print(f"    3. Merge to master when ready:")
        print(f"       `git checkout master && git merge {branch_name}` (Requires Ctrl+K confirmation)")

    else:
        print(f"[-] Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
