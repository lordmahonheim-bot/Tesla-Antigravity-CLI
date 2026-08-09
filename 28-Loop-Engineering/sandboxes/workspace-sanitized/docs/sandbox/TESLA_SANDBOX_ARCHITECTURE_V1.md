# TESLA_SANDBOX_ARCHITECTURE_V1

Statut : Phase 2 — architecture et fallback
Racine Tesla : /home/lord-mahonheim/bifrost/tesla
Autorité finale : Mahonheim

## Décision d’architecture

Architecture retenue :

- POC : Docker/runc gouverné.
- V1 cible : OpenSandbox + Docker + gVisor.
- V2 optionnelle : Kata Containers ou Firecracker si besoin d’isolation microVM.

## Rôles

MIDGARD :
- hôte permanent ;
- conserve secrets, mémoire durable, artefacts validés et Git réel ;
- ne devient pas zone d’impact.

Sandbox :
- espace jetable ;
- absorbe tests, builds, exécutions, installations locales et erreurs ;
- fonctionne sans montage des zones sensibles.

Broker Tesla :
- choisit le profil de risque ;
- crée la sandbox ;
- injecte une copie sanitizée du workspace ;
- applique quotas, TTL et réseau ;
- collecte logs et artefacts ;
- scanne les sorties ;
- bloque les frontières critiques.

## État Phase 1 utilisé

Docker CLI : présent.
Docker daemon : inactif.
runc : présent.
runsc / gVisor : absent.
Kata : absent.
Firecracker : absent.
AppArmor : chargé.
Antigravity CLI : agy 1.0.5.

## Principe de suite

Phase 2 documente l’architecture.
Aucun service Docker ne doit être démarré dans cette phase.
Aucune installation gVisor ne doit être faite dans cette phase.
Aucun changement système ne doit être appliqué dans cette phase.

## Marqueurs

TESLA_SANDBOX_ARCHITECTURE_DRAFTED=1
TESLA_SANDBOX_PHASE_2_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
