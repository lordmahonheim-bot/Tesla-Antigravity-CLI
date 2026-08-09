# TESLA_SANDBOX_THREAT_MODEL_V1

Statut : Phase 0 — modèle de menace initial
Racine Tesla : /home/lord-mahonheim/bifrost/tesla
Autorité finale : Mahonheim

## Menaces principales

1. Fuite de secrets hôte.
2. Écriture accidentelle hors sandbox.
3. Corruption du projet réel.
4. Exécution non bornée consommant CPU, RAM, disque ou PIDs.
5. Accès réseau non autorisé.
6. Exfiltration via logs, artefacts ou DNS.
7. Confusion entre workspace réel et copie jetable.
8. Persistance non voulue de credentials, caches ou cookies.
9. Altération ou suppression de logs.
10. Application prématurée d’un patch généré en sandbox.

## Mitigations validées

- Aucun montage de HOME.
- Aucun montage de .ssh, .env, .gemini, .codex, .config, .local ou .antigravitycli.
- Utilisateur non-root dans la sandbox.
- Réseau default-deny.
- Quotas CPU, RAM, disque, I/O et PIDs.
- TTL et nettoyage automatique.
- Logs capturés hors contrôle direct de l’agent.
- Artefacts sortants scannés.
- Validation Mahonheim pour secrets, hôte, Git réel, cloud, publication et suppression durable.

## Marqueurs

TESLA_SANDBOX_THREAT_MODEL_DRAFTED=1
TESLA_SANDBOX_PHASE_0_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
