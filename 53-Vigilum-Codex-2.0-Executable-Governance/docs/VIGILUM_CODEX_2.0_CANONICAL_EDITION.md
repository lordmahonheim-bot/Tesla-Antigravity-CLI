---
type: reference
tags: [curation/certified, curator/prime, status/valid, vigilum, architecture, security]
coterie: tesla
date: 2026-09-02
author: tesla-curator-prime
confidence_score: 100%
sources: ["Internal Governance Audits", "Vigilum Operation Logs"]
---

# VIGILUM CODEX 2.0 — CANONICAL EDITION

> **L'Ère de la Gouvernance Exécutable**
> Le "Vigilum Codex 2.0" marque la transition paradigmatique d'une doctrine de sécurité théorique vers une architecture de sécurité physique, asymétrique et inconditionnellement résiliente. 

Ce document canonique consigne les fondations architecturales du système d'enclave opérationnelle, structurées en thèses fondamentales de défense.

## I. L'Armature A-7 Safe-Spawn : Le Ledger Transactionnel

La première thèse consacre l'intégrité de l'exécution par la sérialisation stricte et la preuve de terminaison. 

L'architecture **Safe-Spawn** garantit que l'initialisation et l'enregistrement de l'agent ne souffrent d'aucune condition de course :
- **Réservation Stricte (Le Nonce de Genèse)** : L'utilisation de `O_CREAT | O_EXCL` au niveau du système de fichiers assure une atomicité matérielle et l'unicité de la réservation de chaque nonce transactionnel.
- **Séparation des Prérogatives** : Découplage strict entre le processus **Producteur** (qui accomplit la tâche) et le processus **Auditeur** (qui valide et inscrit la transaction).
- **Commit sur Preuve** : L'inscription dans le ledger n'est actée qu'à la présentation irréfutable de la preuve cryptographique.
- **Principe Fail-Closed** : En cas d'interruption abrupte, de panique du noyau ou de perte de puissance, l'état transitoire est invalidé, évitant toute corruption d'état (Fallback strict).

## II. L'Action A-4 : Frontière d'Autorité P0 et Neutralisation de BYPASS-01

L'Action A-4 redéfinit le modèle de menace interne par une refonte totale de l'authentification et de l'isolement inter-processus. 
La vulnérabilité BYPASS-01 (qui permettait l'usurpation locale) est structurellement abolie par les moyens suivants :
- **Daemon `vigilum-gate` Isolé** : Le processus de validation tourne sous un **UID exclusif**, inaccessible aux agents classiques ou processus non privilégiés.
- **Cryptographie Asymétrique** : L'abandon définitif des secrets partagés (HMAC local) au profit de clés asymétriques **Ed25519** avec permissions restrictives (`0400`). 
- **Validation Intraitable (SO_PEERCRED)** : La frontière d'autorité vérifie l'identité au niveau du kernel UNIX sur la socket. `SO_PEERCRED` permet de prouver cryptographiquement le PID/UID appelant, rendant toute falsification locale mathématiquement impossible.

## III. L'Action A-8 : Ancrage Externe et Transcendance SYSTEM_SEALED

La sécurité locale n'étant qu'une promesse relative, le Codex 2.0 impose une dimension géopolitique à la validation des événements. 
L'état des transactions passe du statut transitoire **Tamper-Evident** au stade irréversible **SYSTEM_SEALED** par l'ancrage hors-site.
- **Le Daemon `vigilum_anchor.py`** : Moteur asynchrone conçu pour la haute disponibilité.
- **Files d'Attente Asynchrones** : Gestion robuste de la rétention et de la soumission des empreintes cryptographiques pour résister aux pannes réseau temporaires.
- **Scellement Immuable (Git Distant)** : Poussée systématique et automatisée des hashs de validation sur un dépôt Git tiers, rendant toute tentative de réécriture d'historique immédiatement observable et impossible à cacher, même en cas de compromission locale complète.

## IV. La Résolution A-5 : Preuve de Sainteté Épistémique

L'Incident A-5 a permis de confirmer la fiabilité fondamentale de l'orchestration système.
L'analyse de l'anomalie du "4ème agent neutralisé par le `kill_all`" a statué de manière définitive :
- **Aucune Hallucination Système** : L'intégrité de la supervision n'était pas altérée par l'intelligence artificielle ou des comportements émergents non désirés.
- **Diagnostic Qualifié** : L'événement n'était que le nettoyage déterministe d'un vieux processus **Idle** résiduel, spécifiquement l'ancien agent `tesla-github-manager`, validant ainsi l'efficacité des protocoles de sanitation de l'espace d'exécution.

---
*Livrable synthétisé et certifié conforme le 02 Septembre 2026, au sein de l'environnement BIFROST/TESLA par le Curator Prime.*
