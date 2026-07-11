# 🛡 SIA_POLICY : Doctrine de Gouvernance

Ce document définit les règles de sécurité strictes du système **SIA-TESLA-H** (Self-Improving Harness) pour éviter tout emballement autonome.

## 1. Zéro Persistance Directe
Aucun processus automatisé ne possède les droits d'écriture directs sur la mémoire canonique (`SKILL.md`, `TESLA.json`, `FORCE_TOOLING`). Tout doit transiter via `PATCH_QUEUE.md` et subir la validation de l'Oversight Gate.

## 2. Hard-Caps et Circuit-Breakers
- **Boucle de Self-Healing (LSP)** : Limité à 3 essais par mission.
- **Budget de Token** : Hard-cap de 10-15k tokens par mission simple. Arrêt immédiat de l'agent en cas de dépassement.
- **Générations SIA** : Max 3 patchs générés par incident.

## 3. Critères d'Évaluation (Oversight Gate)
Le passage en production d'un patch nécessite un score supérieur à 85/100, basé sur :
- Tests Pyright / LSP (20%)
- Tests Unitaires & Non-régression (25%)
- Complétion de la mission (20%)
- Maintien des règles de sécurité (15%)
- Coût en Tokens (10%)
- Performance temporelle (5%)
- Maintenabilité (3%)
- Confiance (2%)

Toute modification induisant un bloat sémantique (dépassement de 150 lignes / 8k tokens par fichier de configuration) est systématiquement refusée, nécessitant une ré-ingénierie et compression par l'agent.
