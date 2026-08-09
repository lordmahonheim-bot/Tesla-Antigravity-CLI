---
type: reference
tags: [premortem/certified, resilience/audit, status/valid]
coterie: tesla
date: 2026-07-26
author: tesla-premortem
premortem_score: 35%
decision: REJECTED
---

# PREMORTEM CERTIFICATION REPORT: DELUGE MIDGARD DEPLOYMENT (NODE 6)

## 1. Executive Summary & Scoring Table
The current deployment script for Deluge on MIDGARD is fundamentally flawed due to conflicting security isolations and permission models. 
- The combination of `RestrictSUIDSGID=true` and an SGID `2770` directory will cause immediate EPERM failures on torrent directory creation. 
- The `UMask=0027` prevents the Sonarr/Radarr stack from fully managing or deleting files. 
- The `MemoryMax=1G` constraint is strictly incompatible with libtorrent 2.x's mmap caching behavior (cgroups v2 counts page cache) and will lead to persistent OOM-kill loops on large torrents.

The deployment plan is **REJECTED** and must be refactored by Master Code before execution.

## 2. Verifications & Assumption Matrix
| Assumption | Verification Status | Confidence |
| :--- | :--- | :--- |
| `MemoryMax=1G` safely limits Deluge RAM without crashing. | REFUTED | HIGH |
| SGID + `chmod 2770` allows Radarr full atomic moves. | REFUTED | HIGH |
| `RestrictSUIDSGID=true` adds security with no functional impact. | REFUTED | HIGH |

## 3. Failure Scenarios (FMEA Matrix)
| Identified Failure Mode | Probability | Severity | Detectability | RPN | Mitigation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| OOM Thrashing via libtorrent mmap | 5 | 4 | 2 | 40 | Change `MemoryMax=1G` to `MemoryHigh=1G` and `MemoryMax=2G` (or 3G). |
| Atomic Move Failure (UMask 0027) | 5 | 4 | 2 | 40 | Change `UMask=0027` to `UMask=0002` in `deluged.service` (group needs write). |
| EPERM on Torrent Start (RestrictSUIDSGID) | 5 | 5 | 1 | 25 | Remove `RestrictSUIDSGID=true` (incompatible with SGID inheritance). |

## 4. Signal Analysis & Drift Indicators
- **OOM-Kill Loops**: Systemd logs will show `deluged` frequently restarting due to SIGKILL from the OOM killer when page cache fills the 1G limit.
- **Access Denied Logs**: Sonarr/Radarr logs will show permission errors when attempting to delete or hardlink completed torrents from Deluge's directories.
- **Zero-Byte Torrents / EPERM**: Torrents will instantly fail to download in the Deluge UI because `mkdir` fails under `RestrictSUIDSGID` when inheriting SGID.

## 5. Risk Knowledge Graph Cascades
- `deluged.service (RestrictSUIDSGID)` ──(blocks)──> `SGID inheritance` ──(causes)──> `mkdir EPERM` ──(escalates_to)──> **Zero downloads possible**.
- `libtorrent 2.x (mmap)` ──(exposes)──> `Page cache saturation` ──(triggers)──> `cgroup MemoryMax` ──(causes)──> `OOM Killer` ──(escalates_to)──> **Service instability & data corruption risk**.
- `UMask 0027` ──(strips)──> `Group write access` ──(blocks)──> `Sonarr/Radarr cleanup` ──(escalates_to)──> **Storage exhaustion (duplicate files)**.

---
*Signed and certified on MIDGARD by Tesla Premortem.*
