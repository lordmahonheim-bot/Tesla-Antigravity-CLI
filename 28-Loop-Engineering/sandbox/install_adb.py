#!/usr/bin/env python3
import os
import urllib.request
import zipfile
import shutil

URL = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
ZIP_PATH = "/tmp/platform-tools.zip"
EXTRACT_DIR = "/tmp/platform-tools-extracted"
BIN_DIR = "/home/lord-mahonheim/.local/bin"
TARGET_ADB = os.path.join(BIN_DIR, "adb")

def main():
    print("[*] Downloading Android Platform-Tools from Google...")
    try:
        urllib.request.urlretrieve(URL, ZIP_PATH)
        print("[+] Download complete.")
    except Exception as e:
        print(f"[-] Download failed: {e}")
        return

    print("[*] Extracting adb binary...")
    try:
        if os.path.exists(EXTRACT_DIR):
            shutil.rmtree(EXTRACT_DIR)
        
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
            
        adb_source = os.path.join(EXTRACT_DIR, "platform-tools", "adb")
        if os.path.exists(adb_source):
            os.makedirs(BIN_DIR, exist_ok=True)
            shutil.copy2(adb_source, TARGET_ADB)
            os.chmod(TARGET_ADB, 0o755)
            print(f"[+] ADB successfully installed to {TARGET_ADB}")
        else:
            print("[-] Could not find adb binary in zip.")
    except Exception as e:
        print(f"[-] Extraction failed: {e}")
    finally:
        # Cleanup
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)
        if os.path.exists(EXTRACT_DIR):
            shutil.rmtree(EXTRACT_DIR)

if __name__ == "__main__":
    main()
