# OPEN_SANDBOX_RISK_ASSESSMENT_V1

Statut : Phase 2 — évaluation prudente du candidat OpenSandbox
Racine Tesla : /home/lord-mahonheim/bifrost/tesla

## Position retenue

OpenSandbox est retenu comme candidat principal de control plane pour la V1.
Docker/runc reste le fallback POC gouverné.
gVisor reste la cible runtime renforcée V1.

## Risques identifiés

1. Dépendance externe non encore validée localement.
2. Fonctionnalités exactes à confirmer avant usage.
3. Risque de surcomplexité si intégré trop tôt.
4. Risque de mauvaise configuration réseau ou volumes.
5. Risque de confusion entre control plane et frontière de sécurité.
6. Besoin d’un fallback Docker gouverné si OpenSandbox échoue.

## Conditions avant adoption

- Audit documentaire dédié.
- Test hors secrets.
- Aucun montage HOME.
- Aucun Docker socket exposé à l’agent.
- Réseau default-deny.
- Quotas appliqués.
- Logs capturés.
- Artefacts scannés.
- Validation Mahonheim avant intégration active.

## Décision Phase 2

GO pour documenter OpenSandbox comme candidat.
NO-GO pour installation ou intégration active maintenant.
Fallback obligatoire : wrapper Docker/runc gouverné.

## Marqueurs

OPEN_SANDBOX_RISK_ASSESSMENT_DRAFTED=1
TESLA_SANDBOX_FALLBACK_DEFINED=1
TESLA_SANDBOX_PHASE_2_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
