#!/usr/bin/env python3
"""
Script to connect to MECOOL KM7 via ADB, auto-detecting the IP address
and extracting diagnostic data.
"""

import os
import sys
import socket
import subprocess
import threading
from typing import List, Optional

DIAG_DIR = "/home/lord-mahonheim/bifrost/tesla/OUTPUTS/KM7_diagnostic"


def get_local_ip_and_subnet() -> Optional[str]:
    """Gets the local IP of the system to determine the subnet."""
    try:
        # Create a dummy connection to get the local interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable, just triggers local IP selection
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None


def get_arp_ips() -> List[str]:
    """Extracts IP addresses from the local ARP cache."""
    ips = []
    try:
        # Try reading /proc/net/arp
        if os.path.exists("/proc/net/arp"):
            with open("/proc/net/arp", "r") as f:
                lines = f.readlines()[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if parts and len(parts) > 0:
                        ips.append(parts[0])
        # Also run arp -an as fallback
        output = subprocess.check_output(["arp", "-an"], stderr=subprocess.DEVNULL).decode()
        for line in output.splitlines():
            # e.g., "? (192.168.1.50) at ..."
            if "(" in line and ")" in line:
                ip = line.split("(")[1].split(")")[0]
                if ip not in ips:
                    ips.append(ip)
    except Exception:
        pass
    return ips


def check_port_5555(ip: str, timeout: float = 0.5) -> bool:
    """Checks if port 5555 is open on a given IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, 5555))
        s.close()
        return result == 0
    except Exception:
        return False


def scan_subnet(subnet_prefix: str) -> List[str]:
    """Scans the /24 subnet on port 5555 using threads."""
    found_ips = []
    lock = threading.Lock()
    threads = []

    def worker(ip: str):
        if check_port_5555(ip):
            with lock:
                found_ips.append(ip)

    for i in range(1, 255):
        ip = f"{subnet_prefix}.{i}"
        t = threading.Thread(target=worker, args=(ip,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return found_ips


def detect_box_ip() -> Optional[str]:
    """Attempts to auto-detect the MECOOL KM7 IP."""
    print("[*] Starting auto-detection of the MECOOL KM7 box...")

    # Step 1: Check ARP Cache first
    arp_ips = get_arp_ips()
    print(f"[*] Found {len(arp_ips)} devices in local ARP cache. Checking port 5555...")
    for ip in arp_ips:
        if check_port_5555(ip, timeout=1.0):
            print(f"[+] Found active device with ADB port 5555 open: {ip} (via ARP)")
            return ip

    # Step 2: Scan the subnet
    local_ip = get_local_ip_and_subnet()
    if local_ip:
        print(f"[*] Local IP detected: {local_ip}")
        parts = local_ip.split(".")
        if len(parts) == 4:
            subnet_prefix = ".".join(parts[:3])
            print(f"[*] Scanning subnet {subnet_prefix}.0/24 for port 5555...")
            found = scan_subnet(subnet_prefix)
            if found:
                print(f"[+] Found ADB devices: {found}")
                return found[0]
    else:
        print("[-] Could not detect local IP.")

    return None


def run_adb_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    """Runs an ADB command and returns the completed process."""
    if cmd and cmd[0] == "adb":
        cmd[0] = "/home/lord-mahonheim/.local/bin/adb"
    return subprocess.run(cmd, capture_output=True, text=True)


def check_widevine_status() -> str:
    """Checks the status of Widevine DRM via ADB."""
    print("[*] Retrieving Widevine DRM status...")
    wv_status = "Unknown"
    
    # Method 1: dumpsys media.drm
    res = run_adb_cmd(["adb", "shell", "dumpsys", "media.drm"])
    if res.returncode == 0:
        lines = res.stdout.splitlines()
        for line in lines:
            if "security level" in line.lower() or "securitylevel" in line.lower():
                wv_status = line.strip()
                print(f"[+] Widevine Security Level found in dumpsys: {wv_status}")
                return wv_status

    # Method 2: getprop
    res = run_adb_cmd(["adb", "shell", "getprop"])
    if res.returncode == 0:
        for line in res.stdout.splitlines():
            if "widevine" in line.lower() or "drm" in line.lower():
                if "security" in line.lower() or "level" in line.lower():
                    print(f"[+] Widevine property found: {line.strip()}")
                    wv_status = line.strip()

    return wv_status


def main():
    # Make sure output directory exists
    os.makedirs(DIAG_DIR, exist_ok=True)

    # 1. Connect
    ip = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ip" and len(sys.argv) > 2:
            ip = sys.argv[2]
        else:
            ip = sys.argv[1]
        print(f"[*] IP address provided via command line: {ip}")
    else:
        ip = detect_box_ip()
        if not ip:
            print("[-] Auto-detection failed.")
            try:
                ip_input = input("Please enter the IP address of your MECOOL KM7 box: ").strip()
                if not ip_input:
                    print("[-] No IP address provided. Exiting.")
                    sys.exit(1)
                ip = ip_input
            except (KeyboardInterrupt, EOFError):
                print("\n[-] Non-interactive mode and no IP provided. Exiting.")
                sys.exit(1)

    # Determine the address (with port if specified, otherwise default to :5555)
    adb_address = ip if ":" in ip else f"{ip}:5555"

    print(f"[*] Attempting connection to ADB at {adb_address}...")
    # Disconnect first to ensure clean state
    run_adb_cmd(["adb", "disconnect"])
    
    res = run_adb_cmd(["adb", "connect", adb_address])
    print(res.stdout.strip())
    
    if "connected" not in res.stdout.lower():
        print(f"[-] Failed to connect to {adb_address}. Please ensure wireless debugging is enabled on the device.")
        sys.exit(2)

    print("[+] ADB Connection established successfully!")

    # 2. Extract diagnostics
    print(f"[*] Dumping diagnostics to {DIAG_DIR}...")

    # system props
    print("[*] Extracting system properties...")
    res = run_adb_cmd(["adb", "shell", "getprop"])
    with open(os.path.join(DIAG_DIR, "props.txt"), "w") as f:
        f.write(res.stdout)

    # packages list
    print("[*] Extracting packages list...")
    res = run_adb_cmd(["adb", "shell", "pm", "list", "packages"])
    with open(os.path.join(DIAG_DIR, "packages_stock.txt"), "w") as f:
        f.write(res.stdout)

    # partitions
    print("[*] Extracting partitions...")
    res = run_adb_cmd(["adb", "shell", "cat", "/proc/partitions"])
    with open(os.path.join(DIAG_DIR, "partitions.txt"), "w") as f:
        f.write(res.stdout)

    # boot cmdline
    print("[*] Extracting boot command line...")
    res = run_adb_cmd(["adb", "shell", "cat", "/proc/cmdline"])
    with open(os.path.join(DIAG_DIR, "cmdline.txt"), "w") as f:
        f.write(res.stdout)

    # Widevine status check
    wv = check_widevine_status()
    with open(os.path.join(DIAG_DIR, "widevine_status.txt"), "w") as f:
        f.write(wv)

    print("[+] Diagnostics completed and saved successfully!")


if __name__ == "__main__":
    main()
