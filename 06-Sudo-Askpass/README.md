# Secure Graphical Sudo Authentication

## TTY Risks & NOPASSWD Mitigation
Executing administrative commands inside non-interactive shells or within terminal logs creates significant security risks. If password queries occur on standard TTY inputs without protection, passwords might be captured in execution logs. Conversely, granting broad `NOPASSWD` permissions in `sudoers` creates serious privilege escalation vulnerabilities.

## Persistent Sudo Configuration
To resolve this, we leverage the native `SUDO_ASKPASS` protocol. When `sudo` is called with the `-A` option, it diverts password acquisition to an external script, avoiding TTY hijacking and log exposure.

## Graphical Askpass Loop with Zenity
This repository contains a secure graphical prompt wrapper:
1. **`sudo-askpass-zenity`**: A simple shell wrapper around Zenity that renders a secure password dialog box.
2. **`sudogui`**: A wrapper script that configures `SUDO_ASKPASS`, verifies X11/Wayland display availability, and runs `sudo -A` with your command arguments.

To use the wrapper:
```bash
./06-Sudo-Askpass/scripts/sudogui apt update
```
*Note: Make sure `zenity` is installed on your Linux system (`sudo apt install zenity`).*
