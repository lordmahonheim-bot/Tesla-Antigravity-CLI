# TESLA_SANDBOX_POLICY_MATRIX_V1

Statut : Phase 2 — matrice de politique sandbox
Racine Tesla : /home/lord-mahonheim/bifrost/tesla

## Niveaux de risque

N0 READ-ONLY : lecture de copie, analyse, rapport. Réseau off. Validation non requise.
N1 WORKSPACE WRITABLE : écriture dans copie jetable. Réseau off. Validation non requise.
N2 CODE EXECUTION : Python, Node, shell, tests, builds. Réseau off par défaut. Validation non requise.
N3 BROWSER AUTOMATION : Chromium ou Playwright sandboxé. Réseau allowlist. Validation selon cible.
N4 NETWORK CONTROLLED : pip, npm, GitHub allowlist. Réseau default-deny. Profil validé avant usage.
N5 EXTERNAL ACCOUNT GATED : CLI IA, API externe, cloud léger. Validation Mahonheim requise.
N6 HOST SYSTEM GATED : hôte, secrets, Git réel, AppArmor, kernel, publication. Validation obligatoire.

## Règles transversales

Aucun secret monté.
Aucun HOME monté.
Aucun Docker socket monté.
Aucun conteneur privileged.
Artefacts sortants scannés.
Logs capturés hors contrôle direct de l’agent.

## Marqueurs

TESLA_SANDBOX_POLICY_MATRIX_DRAFTED=1
TESLA_SANDBOX_PHASE_2_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
