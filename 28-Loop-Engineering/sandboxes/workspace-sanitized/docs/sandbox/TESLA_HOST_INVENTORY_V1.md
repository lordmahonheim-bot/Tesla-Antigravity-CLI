# TESLA_HOST_INVENTORY_V1

Statut : Phase 1 — inventaire read-only
Racine Tesla : /home/lord-mahonheim/bifrost/tesla
Machine : MIDGARD
Utilisateur : lord-mahonheim

## Système

OS : Ubuntu 24.04.4 LTS
Kernel : Linux 6.17.0-35-generic x86_64
AppArmor : module chargé
Lecture détaillée AppArmor : privilèges insuffisants sans sudo

## Outils détectés

Docker CLI : présent — Docker version 29.5.2
Docker daemon : inactif
Docker socket : absent — /var/run/docker.sock
Podman : absent
Antigravity CLI : présent via /home/lord-mahonheim/.local/bin/agy
Version agy : 1.0.10
antigravity : absent du PATH
antigravity-cli : absent du PATH

## Runtimes détectés

runc : présent — /usr/bin/runc
runsc / gVisor : absent
kata-runtime : absent
firecracker : absent

## Chemins sensibles inventoriés

~/.gemini : présent
~/.codex : présent
~/.antigravity : absent
~/.antigravitycli : absent
~/.config/Antigravity : absent
~/.local/share/tesla-antigravity-sdk : présent
/home/lord-mahonheim/bifrost/tesla/DataBase : présent

## Antigravity IDE

Aucun lanceur Antigravity ou agy trouvé dans :
- ~/.local/share/applications
- /usr/share/applications

## Contraintes Phase 1 respectées

Aucun sudo utilisé.
Aucun service démarré.
Aucun conteneur lancé.
Aucun secret lu.
Aucune correction appliquée.
Aucune installation réalisée.

## Marqueurs

TESLA_HOST_INVENTORY_DRAFTED=1
TESLA_SANDBOX_PHASE_1_READ_ONLY=1
MAIN_RENDUE_A_MAHONHEIM=1
