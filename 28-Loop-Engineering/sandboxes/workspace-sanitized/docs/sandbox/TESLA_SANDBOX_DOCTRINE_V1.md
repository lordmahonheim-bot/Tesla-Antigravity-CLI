# TESLA_SANDBOX_DOCTRINE_V1

Statut : Phase 0 — doctrine initiale
Racine Tesla : /home/lord-mahonheim/bifrost/tesla
Autorité finale : Mahonheim

## Doctrine

Tesla doit agir librement dans une sandbox isolée, jetable, observable et gouvernée.

L’hôte MIDGARD conserve la permanence, les secrets, la mémoire durable et les artefacts validés.

La sandbox absorbe les expérimentations, les erreurs, les tests, les builds, les installations locales et les effets de bord.

Le Broker gouverne les passages entre Tesla, la sandbox et l’hôte.

## Règles cardinales

- Liberté opérationnelle dans la sandbox.
- Protection stricte de l’hôte.
- Aucun secret monté dans la sandbox.
- Réseau default-deny.
- Quotas CPU, RAM, disque, I/O et PIDs.
- Artefacts sortants scannés.
- Validation Mahonheim aux frontières critiques.
- Main rendue à chaque gate.

## Frontières critiques

Validation explicite requise pour :
- secrets ;
- hôte ;
- Git réel ;
- cloud ;
- compte externe ;
- publication ;
- suppression durable ;
- AppArmor ;
- kernel ;
- sysctl ;
- paiement ;
- sécurité critique.

## Marqueurs

TESLA_SANDBOX_DOCTRINE_DRAFTED=1
TESLA_SANDBOX_PHASE_0_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
