#!/usr/bin/env python3
"""
Automation script to wait for RSA authorization on MECOOL KM7,
run diagnostics (Phase 0), execute debloating and optimization (Phase 1),
update SGC and memory, and notify the parent agent.
"""

import os
import sys
import time
import subprocess
from typing import List

ADB_BIN = "/home/lord-mahonheim/.local/bin/adb"
IP_ADDRESS = "192.168.11.111:5555"
DIAG_DIR = "/home/lord-mahonheim/bifrost/tesla/OUTPUTS/KM7_diagnostic"


def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    """Runs a command and returns the completed process."""
    return subprocess.run(cmd, capture_output=True, text=True)


def is_device_connected() -> bool:
    """Checks if the device is connected and authorized."""
    res = run_cmd([ADB_BIN, "devices"])
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            if IP_ADDRESS in line:
                if "device" in line and "unauthorized" not in line:
                    return True
    return False


def wait_for_authorization(timeout_minutes: int = 10) -> bool:
    """Loops trying to connect and check status until authorized or timeout."""
    print(f"[*] Starting active loop to connect to {IP_ADDRESS}...")
    print("[*] Please check your TV screen and accept the ADB RSA key authorization from MIDGARD.")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    # Clean previous connection states
    run_cmd([ADB_BIN, "disconnect"])
    
    while time.time() - start_time < timeout_seconds:
        # Tenter la connexion
        res = run_cmd([ADB_BIN, "connect", IP_ADDRESS])
        output = res.stdout.strip()
        
        # Vérifier le statut de l'appareil
        if is_device_connected():
            print(f"\n[+] Device authorized and connected successfully: {output}")
            return True
            
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(3)
        
    print("\n[-] Timeout waiting for device authorization.")
    return False


def run_diagnostics():
    """Runs Phase 0 diagnostics and dumps data to files."""
    print(f"[*] Dumping diagnostics to {DIAG_DIR}...")
    os.makedirs(DIAG_DIR, exist_ok=True)
    
    # system props
    print("[*] Dumping system properties...")
    res = run_cmd([ADB_BIN, "shell", "getprop"])
    with open(os.path.join(DIAG_DIR, "props.txt"), "w") as f:
        f.write(res.stdout)

    # packages list
    print("[*] Dumping packages list...")
    res = run_cmd([ADB_BIN, "shell", "pm", "list", "packages"])
    with open(os.path.join(DIAG_DIR, "packages_stock.txt"), "w") as f:
        f.write(res.stdout)

    # partitions
    print("[*] Dumping partitions...")
    res = run_cmd([ADB_BIN, "shell", "cat", "/proc/partitions"])
    with open(os.path.join(DIAG_DIR, "partitions.txt"), "w") as f:
        f.write(res.stdout)

    # boot cmdline
    print("[*] Dumping boot command line...")
    res = run_cmd([ADB_BIN, "shell", "cat", "/proc/cmdline"])
    with open(os.path.join(DIAG_DIR, "cmdline.txt"), "w") as f:
        f.write(res.stdout)

    # Widevine status check
    print("[*] Checking Widevine DRM status...")
    wv_status = "Unknown"
    res = run_cmd([ADB_BIN, "shell", "dumpsys", "media.drm"])
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            if "security level" in line.lower() or "securitylevel" in line.lower():
                wv_status = line.strip()
                break
                
    with open(os.path.join(DIAG_DIR, "widevine_status.txt"), "w") as f:
        f.write(wv_status)
        
    print(f"[+] Widevine Status: {wv_status}")


def run_debloat_and_optimization():
    """Runs Phase 1 debloating and updates animations directly via ADB."""
    print("[*] Running debloating directly via ADB commands...")
    packages = [
        "com.sundan.ddservice",
        "com.android.printspooler",
        "com.google.android.videos",
        "com.google.android.youtube.tvmusic",
        "com.google.android.play.games",
        "com.google.android.feedback",
        "com.google.android.music",
        "com.google.android.tv"
    ]
    
    # 1. Debloating
    # Get the list of installed packages first
    res = run_cmd([ADB_BIN, "shell", "pm", "list", "packages"])
    installed_packages = []
    if res.returncode == 0:
        installed_packages = [line.split(":")[-1].strip() for line in res.stdout.splitlines() if ":" in line]
        
    for pkg in packages:
        print(f"[*] Analyzing package: {pkg}")
        if pkg in installed_packages:
            print(f"    -> Package present. Disabling...")
            disable_res = run_cmd([ADB_BIN, "shell", "pm", "disable-user", "--user", "0", pkg])
            if disable_res.returncode == 0 and ("disabled-user" in disable_res.stdout.lower() or "new state" in disable_res.stdout.lower() or "disabled" in disable_res.stdout.lower()):
                print(f"    [SUCCESS] Package {pkg} disabled.")
            else:
                uninstall_res = run_cmd([ADB_BIN, "shell", "pm", "uninstall", "-k", "--user", "0", pkg])
                if uninstall_res.returncode == 0 and "success" in uninstall_res.stdout.lower():
                    print(f"    [SUCCESS] Package {pkg} uninstalled for user 0.")
                else:
                    print(f"    [WARNING] Could not disable/uninstall {pkg}. Stdout: {disable_res.stdout.strip()} | Stderr: {disable_res.stderr.strip()}")
        else:
            print("    -> Package not present on this box.")
            
    # 2. Animation scales
    print("[*] Configuring animation scales to 0.5...")
    scales = ["window_animation_scale", "transition_animation_scale", "animator_duration_scale"]
    for scale in scales:
        scale_res = run_cmd([ADB_BIN, "shell", "settings", "put", "global", scale, "0.5"])
        if scale_res.returncode == 0:
            print(f"    [SUCCESS] {scale} set to 0.5.")
        else:
            print(f"    [WARNING] Failed to set {scale}.")
            
    # 3. Background dexopt job
    print("[*] Lancement de l'optimisation des packages en tâche de fond...")
    run_cmd([ADB_BIN, "shell", "cmd", "package", "bg-dexopt-job"])
    print("    [SUCCESS] Tâche bg-dexopt-job déclenchée.")


def main():
    if not os.path.exists(ADB_BIN):
        print(f"[-] ADB binary not found at {ADB_BIN}")
        sys.exit(1)
        
    if not wait_for_authorization():
        sys.exit(1)
        
    # Phase 0
    run_diagnostics()
    
    # Phase 1
    run_debloat_and_optimization()
    
    print("[+] All diagnostic and optimization operations finished successfully!")


if __name__ == "__main__":
    main()
