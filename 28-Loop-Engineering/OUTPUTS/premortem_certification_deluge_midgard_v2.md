---
type: reference
tags: [premortem/certified, resilience/audit, status/valid]
coterie: tesla
date: 2026-07-26
author: tesla-premortem
premortem_score: 100%
decision: RECOMMENDED
---

# PREMORTEM CERTIFICATION REPORT: DELUGE MIDGARD V2

## 1. Executive Summary & Scoring Table
L'audit V2 du script d'installation `install_deluge_midgard.sh` (réécrit par Master-Code) a été complété. Les trois correctifs d'urgence exigés lors du précédent NO-GO ont été vérifiés et validés :
1. Les limites de mémoire (`MemoryHigh=1G` / `MemoryMax=2G`) sont bien définies dans `deluged.service`, prévenant le bug d'OOM Thrashing de libtorrent 2.x.
2. Le `UMask=0002` a été ajouté aux services systemd pour garantir le partage de droits de groupe.
3. La directive `RestrictSUIDSGID` a été retirée, permettant la création correcte des dossiers SGID sans erreurs `EPERM`.

La robustesse de l'architecture est désormais conforme aux standards MIDGARD. Le déploiement est officiellement autorisé.

**Score Global : 100%**
**Décision : RECOMMENDED (GO OFFICIEL)**

## 2. Verifications & Assumption Matrix
| Assumption | Verification Status | Confidence |
| :--- | :--- | :--- |
| libtorrent 2.x mmap bug triggers OOM Thrashing without limits. | VALIDATED | 100% |
| Deluge's default UMask 022 breaks atomic moves for media group. | VALIDATED | 100% |
| Systemd `RestrictSUIDSGID` blocks SGID bit inheritance on subfolders. | VALIDATED | 100% |

## 3. Failure Scenarios (FMEA Matrix)
| Identified Failure Mode | Probability | Severity | Detectability | RPN | Mitigation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| OOM Thrashing via libtorrent 2.x | 4 | 5 | 2 | 40 | Enforced `MemoryHigh=1G` & `MemoryMax=2G` in `deluged.service` |
| Group permission denied on Sonarr/Radarr import | 5 | 4 | 1 | 20 | Added `UMask=0002` globally in systemd |
| SGID permission inheritance failure (EPERM) | 5 | 3 | 2 | 30 | Removed `RestrictSUIDSGID` from unit boundaries |

## 4. Signal Analysis & Drift Indicators
- **OOM Kill Events**: Surveillance des journaux (journalctl) pour toute invocation du OOM Killer visant le daemon `deluged` (si la limite de 2G est atteinte).
- **Import Failures**: Monitoring des journaux applicatifs Sonarr/Radarr pour détecter tout `Access Denied` ou échec d'Atomic Move.

## 5. Risk Knowledge Graph Cascades
- `[deluged.service]` --(OOM Bug)--> `[Host RAM Exhaustion]` --(Mitigated by)--> `[MemoryMax=2G]`
- `[deluged.service]` --(UMask=022)--> `[Sonarr/Radarr EPERM]` --(Mitigated by)--> `[UMask=0002]`
- `[deluged.service]` --(RestrictSUIDSGID)--> `[SGID Breakage]` --(Mitigated by)--> `[Unit Config Adjustment]`

---
*Signed and certified on MIDGARD by Tesla Premortem.*
