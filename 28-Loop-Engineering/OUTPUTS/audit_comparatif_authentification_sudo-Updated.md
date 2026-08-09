---
type: reference
tags: [securite/audit, technique/comparatif, statut/valide]
source: "[[solution_authentification_sudo_optimisee.txt]]"
date: 2026-06-28
version: 1.2-Updated
---

# AUDIT COMPARATIF : ARCHITECTURE D'AUTHENTIFICATION SUDO SUR MIDGARD (CORRIGÉ & DURCI V1.2)
**Date de l'audit :** 2026-06-28  
**Analyste :** Tesla (sur Antigravity CLI)  
**Destinataire :** Mahonheim (Abdellah MOUHTAJ)

---

## 1. Confrontation Objective des Deux Approches

Nous comparons ici la **Solution Initiale** (délégation ciblée sans mot de passe `NOPASSWD`) avec la **Solution Proposée** (saisie graphique sécurisée via `sudogui` avec Zenity et délai d'attente illimité).

### Tableau d'Analyse Comparative

| Critère de Performance | Solution Initiale (NOPASSWD) | Solution Proposée (Zenity Askpass + `passwd_timeout=0`) |
| :--- | :--- | :--- |
| **Sécurité Globale** | **Moyenne** : Élimine la barrière d'authentification. Même restreint, l'accès sans mot de passe à des utilitaires système augmente la surface d'attaque en cas de compromission locale. | **Excellente** : Conserve le principe du mot de passe. Aucun droit n'est accordé sans une validation physique consciente de l'opérateur. |
| **Ergonomie & Saisie** | **Immédiate** : Aucune intervention requise, le script s'exécute de manière totalement fluide en tâche de fond. | **Très Bonne** : Affiche une boîte de dialogue graphique claire, sans délai d'expiration stressant (`passwd_timeout=0`). |
| **Résilience d'Environnement** | **Parfaite** : Fonctionne dans tous les contextes (sessions SSH, environnements non graphiques, démons système sans TTY ni DISPLAY). | **Moyenne** : Dépend de la session graphique locale GNOME (nécessite les variables `$DISPLAY` et `$XDG_RUNTIME_DIR` pour lier la sandbox à l'écran). |
| **Intégrité de l'Historique** | **Parfaite** : Aucun mot de passe n'est saisi ou écrit dans les flux système. | **Parfaite** : Le mot de passe est capturé de manière sécurisée par Zenity et n'apparaît pas dans l'historique shell ou les logs. |

---

## 2. Synthèse et Verdict Technique

### Les Limites des deux extrêmes :
- **La faiblesse de NOPASSWD** est le risque sécuritaire lié à l'utilisation de jokers `*` ou au ciblage de disques amovibles (comme `/dev/sdb`) dont l'identifiant physique peut changer selon l'ordre de branchement matérielle.
- **La faiblesse du Askpass Graphique** est son incapacité à s'exécuter dans des tâches de fond purement non interactives (comme un démon de surveillance d'arrière-plan ou un cron) sans polluer l'écran de l'utilisateur avec des fenêtres intrusives à chaque itération.

### Verdict : L'Architecture Hybride Optimale & Sécurisée (V1.2)
Pour allier la performance technique maximale, la gouvernance de sécurité et l'opérabilité :

1. **Pour les actions de modification/écriture initiées par Tesla (ex: réparer, monter, reformater) :**
   Appliquer de manière exclusive la **Solution Proposée (Zenity Askpass via `sudogui`)**. Cela garantit la sécurité absolue de MIDGARD en demandant une validation mot de passe à l'écran, sans aucune contrainte de temps (`passwd_timeout=0`).
   
2. **Pour les tâches d'arrière-plan de monitoring automatique (Démon `hardware_guard` sous systemd) :**
   Autoriser la directive `NOPASSWD` de façon **strictement bornée** uniquement pour le disque interne fixe et stable de la machine.
   
   - **Disque interne de MIDGARD :** `/dev/sda` (Western Digital 931.5 Go, immuable).
   - **Disques amovibles (Clé USB /dev/sdb et autres) :** Exclusion stricte de la règle `NOPASSWD`. Toute interrogation de monitoring ou d'administration de ces volumes amovibles passera par `sudogui` (saisie de mot de passe graphique sécurisée) pour interdire toute usurpation ou conflit de montage lors de changements d'ordre de branchement.

---

## 3. Guide d'Implémentation Étape par Étape

### Étape 1 : Création de l'assistant askpass graphique (`sudogui`)
Exécuter ces commandes dans votre terminal :
```bash
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/sudo-askpass-zenity" <<'EOF'
#!/bin/sh
exec /usr/bin/zenity \
  --password \
  --title="Authentification Tesla (MIDGARD)" \
  --text="Une autorisation sudo est requise par Tesla.\n\nSaisissez votre mot de passe pour continuer." \
  --width=460
EOF
chmod 700 "$HOME/.local/bin/sudo-askpass-zenity"
```

### Étape 2 : Configuration du script wrapper de sécurité (`sudogui`)
```bash
cat > "$HOME/.local/bin/sudogui" <<'EOF'
#!/bin/sh
export SUDO_ASKPASS="$HOME/.local/bin/sudo-askpass-zenity"
if [ -z "$DISPLAY" ]; then
  export DISPLAY=":0"
fi
if [ -z "$XDG_RUNTIME_DIR" ]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi
exec sudo -A "$@"
EOF
chmod 700 "$HOME/.local/bin/sudogui"
```

### Étape 3 : Configuration de la politique de sécurité sudoers (Version Durcie V1.2)
Création d'un fichier temporaire pour valider la syntaxe avec `visudo` avant installation physique :
```bash
# 1. Écriture du fichier de configuration temporaire
cat > /tmp/99-tesla-security <<'EOF'
Defaults passwd_timeout=0

lord-mahonheim ALL=(root) NOPASSWD: /usr/sbin/smartctl -a /dev/sda
EOF

# 2. Validation de la syntaxe et installation sécurisée
sudo visudo -cf /tmp/99-tesla-security && \
sudo install -m 0440 /tmp/99-tesla-security /etc/sudoers.d/99-tesla-security && \
sudo visudo -c
```

---
*Rapport d'audit technique comparatif corrigé, validé et mis à jour (V1.2-Updated) sur MIDGARD par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
