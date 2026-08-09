# TESLA_SANDBOX_POC_DOCKER_V1

Statut : Phase 4 — POC isolation de base
Racine Tesla : /home/lord-mahonheim/bifrost/tesla
Runtime POC : Docker/runc
Image locale utilisée : curlimages/curl:latest

## Prévol Docker actif

Docker version : 29.5.2
Runtime par défaut : runc
Cgroup driver : systemd
Security options : AppArmor, seccomp builtin, cgroupns
Docker service : active
Docker socket : présent

## POC minimal offline

Commande exécutée avec :
- --rm
- --network none
- --read-only
- --cap-drop ALL
- --security-opt no-new-privileges
- --memory 128m
- --cpus 0.5
- --pids-limit 64
- aucun volume
- aucun pull réseau

Résultat :
- uid=100(curl_user)
- gid=101(curl_group)
- working directory : /home/curl_user
- TESLA_SANDBOX_POC_MINIMAL_OK=1
- aucun conteneur résiduel

## POC artefact contrôlé

Emplacement autorisé :
artifacts/sandbox/poc-basic/

Premier essai :
- échec propre : Permission denied
- cause : dossier hôte UID/GID 1000, conteneur par défaut UID 100

Correction sûre :
- relance avec --user "$(id -u):$(id -g)"
- aucun chmod
- aucun chown
- aucun HOME monté
- aucun Docker socket monté
- aucun réseau

Artefacts créés :
- artifacts/sandbox/poc-basic/id.txt
- artifacts/sandbox/poc-basic/pwd.txt
- artifacts/sandbox/poc-basic/result.txt

Contenus vérifiés :
- id.txt : uid=1000 gid=1000 groups=1000
- pwd.txt : /home/curl_user
- result.txt : TESLA_SANDBOX_ARTIFACT_OK=1

Nettoyage :
- aucun conteneur résiduel curlimages/curl:latest après le test artefact

## Verdict

TESLA_SANDBOX_POC_DOCKER_MINIMAL_OK=1
TESLA_SANDBOX_ARTIFACT_EXPORT_OK=1
TESLA_SANDBOX_NO_NETWORK_USED=1
TESLA_SANDBOX_NO_HOME_MOUNT=1
TESLA_SANDBOX_NO_DOCKER_SOCKET_MOUNT=1
TESLA_SANDBOX_NO_RESIDUAL_CONTAINER=1

## Marqueurs

TESLA_SANDBOX_POC_DOCKER_DRAFTED=1
TESLA_SANDBOX_PHASE_4_ACTIVE=1
MAIN_RENDUE_A_MAHONHEIM=1
