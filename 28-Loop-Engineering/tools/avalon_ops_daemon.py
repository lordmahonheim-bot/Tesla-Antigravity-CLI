#!/usr/bin/env python3
import fcntl
import sys
import os
import threading

AVALON_DIR = "/home/lord-mahonheim/bifrost/tesla/Avalon"
LOCK_FILE = "/tmp/avalon_ops_daemon.lock"

# Securing the process_events callback with a threading lock
_process_lock = threading.Lock()

def process_events():
    with _process_lock:
        print("Changes detected, processing oneshot...")
        # Add actual zero-touch operations here
        log_file = os.path.join(AVALON_DIR, "daemon_log.md")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Run processed.\n")
        except Exception as e:
            print(f"Error writing to {log_file}: {e}")

def main():
    # Ensure exclusive execution via flock
    try:
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Daemon is already running.")
        sys.exit(1)
        
    os.makedirs(AVALON_DIR, exist_ok=True)
    
    # Run as a oneshot processor
    process_events()

if __name__ == "__main__":
    main()
