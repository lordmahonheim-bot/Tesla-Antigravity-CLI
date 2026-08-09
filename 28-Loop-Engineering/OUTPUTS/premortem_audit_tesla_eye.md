---
type: reference
tags: [premortem/certified, resilience/audit, status/valid]
coterie: tesla
date: 2026-07-24
author: tesla-premortem
premortem_score: 95%
decision: RECOMMENDED
---

# PREMORTEM CERTIFICATION REPORT: TESLA-EYE PASSIVE SURVEILLANCE

## 1. Executive Summary & Scoring Table
L'implémentation de la surveillance passive par `tesla-master-code` a été auditée. Les mécanismes de verrouillage et les déclencheurs systemd ont été analysés pour écarter tout risque de boucle infinie ou d'emballement du CPU.

**Score Global : 95% - GO FINAL**

La séparation stricte entre le dossier de surveillance (`~/Pictures/Screenshots`) et le dossier de traitement (`/tmp/tesla_eye_processing`) élimine le risque de boucle de réentrance inhérent à l'utilisation des unités `.path` de systemd. Le verrouillage `flock` apporte une robustesse supplémentaire contre la concurrence déloyale.

## 2. Verifications & Assumption Matrix
| Assumption | Verification Status | Confidence |
| :--- | :--- | :--- |
| Le dossier source est exempt d'écritures cycliques du script | **VALIDATED** (Le traitement se fait dans `/tmp/`) | 100% |
| Un seul traitement est actif à la fois | **VALIDATED** (Lock `flock -n 200` + `Type=oneshot`) | 100% |
| Le script ne crashera pas sur des noms de fichiers spéciaux | **VALIDATED** (Utilisation de `find` + null separators) | 90% |

## 3. Failure Scenarios (FMEA Matrix)
| Identified Failure Mode | Probability | Severity | Detectability | RPN | Mitigation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Boucle Infinie / Réentrance** (Écrire dans le dossier écouté) | 1 | 5 | 1 | **5** | Séparation stricte `WATCH_DIR` vs `PROCESSING_DIR`. `PathChanged` au lieu de `PathModified`. |
| **Surcharge CPU** (Multiprocessing des événements rapides) | 1 | 4 | 2 | **8** | Unité Systemd `Type=oneshot` (file d'attente) combinée à un verrou `flock -n 200` bloquant l'exécution concurrente. |
| **Engorgement du dossier Screenshots** (Lenteur de `find`) | 3 | 2 | 3 | **18** | Acceptable à court terme. La commande `find` et `sort` pourrait devenir lente avec plus de 10 000 fichiers. |
| **Perte d'évènements rapides** (Capture pendant un run) | 3 | 2 | 2 | **12** | Le `flock -n` fera silencieusement échouer l'instance concurrente. Systemd rattrapera via l'évènement `PathChanged` suivant, mais seul le dernier fichier sera traité. Acceptable pour ce cas d'usage. |

## 4. Signal Analysis & Drift Indicators
- **Indicateur de dérive :** Le temps d'exécution du script `tesla_eye_watcher.sh`. S'il dépasse 1 seconde, c'est le signe que la commande `find` est en train de s'engorger à cause du nombre de screenshots dans le dossier source.
- **Seuil d'alerte :** > 5000 fichiers dans `~/Pictures/Screenshots`.

## 5. Risk Knowledge Graph Cascades
- [systemd.path] --déclenche--> [systemd.service] --lance--> [tesla_eye_watcher.sh]
- Si [tesla_eye_watcher.sh] crashe, [systemd.service] remonte une erreur (pas de relance automatique car pas de `Restart=always`, ce qui est souhaitable pour éviter un DoS en cas d'erreur de script systématique).
- Le verrou [flock] protège le CPU de [systemd.path] qui recevrait un flood d'évènements.

---
*Signed and certified on MIDGARD by Tesla Premortem.*
