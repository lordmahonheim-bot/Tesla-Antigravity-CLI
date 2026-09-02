#!/usr/bin/env python3
"""
Vigilum Anchor Daemon (Node N2)
Reads the cryptographic state of Gate 2 and anchors it to a remote Git repository
using signed commits, ensuring an immutable audit trail.
"""

import os
import sys
import fcntl
import time
import logging
import subprocess
from pathlib import Path

# Configuration via Environment with safe defaults
CHAIN_HEAD_PATH = Path(os.environ.get("VIGILUM_CHAIN_HEAD", "/home/lord-mahonheim/bifrost/tesla/runtime/gate2/chain_head.sha256"))
REPO_DIR = Path(os.environ.get("VIGILUM_REPO_DIR", "/home/lord-mahonheim/bifrost/tesla/MVP-GITHUB/53-Vigilum-Codex-2.0-Executable-Governance/core/anchor/repo_anchor"))
KEY_PATH = Path(os.environ.get("VIGILUM_KEY_PATH", "/etc/vigilum/keys/id_ed25519_anchor"))
REMOTE_BRANCH = os.environ.get("VIGILUM_REMOTE_BRANCH", "audit-trail")
CHECK_INTERVAL = int(os.environ.get("VIGILUM_CHECK_INTERVAL", 900))  # Default 15 minutes
MAX_RETRIES = int(os.environ.get("VIGILUM_MAX_RETRIES", 5))
RETRY_DELAY = int(os.environ.get("VIGILUM_RETRY_DELAY", 60))

# Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "vigilum-anchor"}',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logger = logging.getLogger("vigilum-anchor")

def check_key_permissions(key_path: Path) -> None:
    """Enforces 0400 permissions on the cryptographic key."""
    if not key_path.exists():
        logger.error(f"Key not found at {key_path}")
        sys.exit(1)
    stat = key_path.stat()
    perms = stat.st_mode & 0o777
    if perms != 0o400:
        logger.warning(f"Key permissions are {oct(perms)}, enforcing 0400.")
        try:
            key_path.chmod(0o400)
        except PermissionError:
            logger.error("Failed to set 0400 permissions on key. Insufficient privileges.")
            sys.exit(1)

def read_chain_head() -> str | None:
    """Safely reads the chain head using POSIX file locks to prevent race conditions."""
    if not CHAIN_HEAD_PATH.exists():
        logger.warning(f"Chain head file {CHAIN_HEAD_PATH} does not exist.")
        return None
        
    try:
        with open(CHAIN_HEAD_PATH, "r", encoding="utf-8") as f:
            # POSIX file lock (shared lock for reading)
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return f.read().strip()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error reading chain head: {e}")
        return None

def run_git_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Executes a Git command with isolated SSH environment."""
    env = os.environ.copy()
    # Explicitly force SSH to use the specific anchor key
    env["GIT_SSH_COMMAND"] = f"ssh -i {KEY_PATH} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
    
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )
    except subprocess.TimeoutExpired as e:
        logger.error(f"Git command timed out: {e}")
        return subprocess.CompletedProcess(args=e.cmd, returncode=124, stdout="", stderr="Command timed out")
    except Exception as e:
        logger.error(f"Unexpected error running git command: {e}")
        return subprocess.CompletedProcess(args=["git"] + args, returncode=1, stdout="", stderr=str(e))

def ensure_repo_setup() -> None:
    """Ensures the local Git buffer repository is initialized and configured for signed commits."""
    if not (REPO_DIR / ".git").exists():
        logger.info(f"Initializing Git repository in {REPO_DIR}")
        REPO_DIR.mkdir(parents=True, exist_ok=True)
        run_git_command(["init"], REPO_DIR)
        run_git_command(["config", "user.name", "vigilum-anchor"], REPO_DIR)
        run_git_command(["config", "user.email", "anchor@midgard.local"], REPO_DIR)
        
        # Configure commit signing with SSH
        run_git_command(["config", "gpg.format", "ssh"], REPO_DIR)
        run_git_command(["config", "user.signingkey", str(KEY_PATH)], REPO_DIR)
        run_git_command(["config", "commit.gpgsign", "true"], REPO_DIR)
        
        # Create empty initial commit to create the branch properly
        run_git_command(["commit", "--allow-empty", "-m", "Initial anchor branch creation"], REPO_DIR)
        run_git_command(["branch", "-m", REMOTE_BRANCH], REPO_DIR)
    else:
        res = run_git_command(["branch", "--show-current"], REPO_DIR)
        if res.returncode == 0 and res.stdout.strip() != REMOTE_BRANCH:
            run_git_command(["checkout", REMOTE_BRANCH], REPO_DIR)

def create_anchor_commit(sha256: str) -> bool:
    """Creates a signed, empty commit anchoring the provided SHA256 state."""
    res = run_git_command(["log", "-1", "--pretty=%B"], REPO_DIR)
    if res.returncode == 0 and sha256 in res.stdout:
        logger.info(f"SHA256 {sha256} is already the latest anchor. Skipping commit.")
        return False

    logger.info(f"Creating signed empty commit for SHA256: {sha256}")
    res = run_git_command(["commit", "--allow-empty", "-S", "-m", f"Anchor state: {sha256}"], REPO_DIR)
    
    if res.returncode != 0:
        logger.error(f"Commit failed: {res.stderr.strip()}")
        return False
    return True

def push_to_remote() -> bool:
    """Pushes local queue of commits to the remote. Local Git repo acts as the asynchronous queue."""
    res = run_git_command(["remote"], REPO_DIR)
    if "origin" not in res.stdout:
        logger.warning("No remote 'origin' configured. Commits are queued locally.")
        return False
        
    logger.info("Pushing anchored states to remote...")
    for attempt in range(1, MAX_RETRIES + 1):
        res = run_git_command(["push", "origin", REMOTE_BRANCH], REPO_DIR)
        if res.returncode == 0:
            logger.info("Push successful. Remote audit trail updated.")
            return True
            
        logger.warning(f"Push attempt {attempt}/{MAX_RETRIES} failed: {res.stderr.strip()}")
        if attempt < MAX_RETRIES:
            logger.info(f"Waiting {RETRY_DELAY} seconds before retry...")
            time.sleep(RETRY_DELAY)
            
    logger.error("All push attempts failed. Changes safely queued in local Git history.")
    return False

def check_queue_size() -> None:
    """Monitors the local un-pushed queue size as a drift indicator."""
    res = run_git_command(["log", f"origin/{REMOTE_BRANCH}..HEAD", "--oneline"], REPO_DIR)
    if res.returncode == 0:
        unpushed_count = len([line for line in res.stdout.splitlines() if line.strip()])
        if unpushed_count > 5:
            logger.warning(f"Local queue has {unpushed_count} un-pushed anchors. Network disruption prolonged.")

def main() -> None:
    logger.info("Starting Vigilum Anchor Daemon...")
    check_key_permissions(KEY_PATH)
    ensure_repo_setup()
    
    while True:
        try:
            head_sha = read_chain_head()
            if head_sha:
                if create_anchor_commit(head_sha):
                    push_to_remote()
                    check_queue_size()
            else:
                logger.info("No valid chain head found to anchor.")
                
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
