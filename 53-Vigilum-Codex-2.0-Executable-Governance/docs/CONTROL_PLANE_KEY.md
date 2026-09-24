# Clé du Plan de Contrôle (Control Plane Key)

La "Gate R" (Executable Governance) nécessite une clé de contrôle d'accès pour fonctionner : `TESLA_CONTROL_PLANE_KEY`.

## Usage
Cette clé prouve l'autorité du Souverain lors de l'exécution de la validation de gouvernance (notamment via `test_runner.py`).

### Local / Développement
Sur la machine souveraine (MIDGARD), la clé est résolue via un mécanisme dégradé ou configurée dans l'environnement local `~/.bashrc` ou `.env`.
\`\`\`bash
export TESLA_CONTROL_PLANE_KEY="<clé_secrète>"
\`\`\`

### Intégration Continue (CI)
Dans GitHub Actions, cette clé doit être fournie via les **Secrets du Dépôt** :
\`\`\`yaml
env:
  TESLA_CONTROL_PLANE_KEY: ${{ secrets.TESLA_CONTROL_PLANE_KEY }}
\`\`\`

## Code de Retour 66 (UNKNOWN)
Si la clé est absente, non reconnue, ou mal formée, la Gate R renverra formellement le code `66` (`UNKNOWN`).
Ce code signifie "état d'autorité non déterminé" et bloque le workflow (Fail-closed) sans exposer d'informations sur l'état des règles sous-jacentes.
