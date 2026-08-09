# USB Resilience & Physical Intervention

## Inconsistency Diagnostics (Dirty NTFS Bit)
Physical external media, especially NTFS-formatted drives used across dual-boot environments (Linux & Windows), frequently experience improper unmounts. This sets the **NTFS Dirty Bit**, which prevents modern Linux kernels from mounting the partition in write mode, defaulting it to read-only or failing altogether.

## Local `ntfs3` Driver Mount Command
This project exploits the high-performance kernel-native `ntfs3` driver introduced in Linux 5.15+. The script enforces read-write mounting even after minor failures using the `force` mount option, falling back gracefully to read-only (`ro`) to protect user data from corruption when hard inconsistencies are detected.

## Automated repair and mount script
The utility `repair_mount_usb.sh` automates the repair and mount procedure:
1. Validates that the targeted path points to a valid block device.
2. Clears volume inconsistencies using `ntfsfix`.
3. Creates the mount directory if not present.
4. Mounts the volume securely with the `ntfs3` driver.

Usage:
```bash
./05-USB-Resilience/examples/repair_mount_usb.sh [DEVICE_PATH] [MOUNT_POINT]
# Example:
# ./05-USB-Resilience/examples/repair_mount_usb.sh /dev/sdb1 /media/DISK
```
*Note: Requires root/sudo privileges to execute filesystem checks and mounting.*
