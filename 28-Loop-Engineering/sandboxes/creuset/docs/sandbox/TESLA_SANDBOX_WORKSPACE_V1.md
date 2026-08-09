# TESLA_SANDBOX_WORKSPACE_V1

Statut : Phase 5 — workspace jetable et scan secrets
Racine Tesla : /home/lord-mahonheim/bifrost/tesla

## Livrables Phase 5

- sandbox/scripts/export-workspace-sanitized.sh
- sandbox/scanner/scan-secrets.sh
- docs/sandbox/TESLA_SANDBOX_WORKSPACE_V1.md

## Export workspace sanitizé

Cible :
sandboxes/workspace-sanitized

Script :
sandbox/scripts/export-workspace-sanitized.sh

Exclusions critiques :
- .git/
- .env
- .env.*
- .ssh/
- .gnupg/
- .gemini/
- .codex/
- .config/
- .local/
- .antigravity/
- .antigravitycli/
- DataBase/
- node_modules/
- __pycache__/
- .pytest_cache/
- sandboxes/
- artifacts/sandbox/
- logs/sandbox/
- sandbox/scanner/

Correction appliquée :
- --delete-excluded ajouté à rsync

## Scanner secrets

Script :
sandbox/scanner/scan-secrets.sh

Contrôles :
- fichiers .env, .env.*, *.pem, *.key
- motifs api_key, token, password, credential, client_secret, private_key assignés
- marqueurs BEGIN RSA, BEGIN OPENSSH, BEGIN PRIVATE

## Incident Phase 5

Premier scan :
SECRET_PATTERN_RISK=1

Cause :
Le scanner avait été exporté dans la copie et détectait ses propres motifs regex.

Correction :
- exclusion de sandbox/scanner/
- suppression du résidu dans sandboxes/workspace-sanitized/
- ajout de --delete-excluded au script rsync
- réexport propre

## Résultat vérifié

WORKSPACE_FORBIDDEN_CONTENT_FOUND=0
SECRET_SCAN_OK=1
SCAN_TARGET=sandboxes/workspace-sanitized

## Contraintes respectées

Aucun Docker run.
Aucun réseau.
Aucun secret hôte lu.
Aucun contenu secret affiché.
Aucune zone HOME sensible montée.
Aucune modification système.

## Marqueurs

TESLA_SANDBOX_WORKSPACE_DRAFTED=1
TESLA_SANDBOX_WORKSPACE_EXPORT_VALIDATED=1
TESLA_SANDBOX_SECRET_SCAN_VALIDATED=1
TESLA_SANDBOX_PHASE_5_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
