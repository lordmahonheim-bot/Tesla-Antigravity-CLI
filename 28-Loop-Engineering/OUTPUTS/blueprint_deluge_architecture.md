---
type: reference
tags: [curation/certified, curator/prime, status/valid, architecture, systemd, deluge]
coterie: tesla
date: 2026-07-26
author: tesla-curator-prime
confidence_score: 100%
sources: ["N1_online_research", "N2_deep_research_archi"]
---

# CERTIFIED REPORT: Blueprint d'Architecture - Systemd & Isolation pour Deluge (MIDGARD)

## 1. Diagnostic Summary
Conformément à la séquence Nœud 3 (DAG Deluge), ce blueprint d'architecture établit le modèle d'intégration de Deluge sur l'environnement MIDGARD. Il intègre un durcissement (hardening) du daemon, une isolation par utilisateur dédié, et une mitigation impérative des fuites mémoires liées au cache mmap de `libtorrent` 2.x via des limites de ressources (cgroups) imposées au niveau de Systemd.

Ce document constitue la spécification (Output N3) destinée à être implémentée par le Nœud 4 (Master-Code).

## 2. Plan d'Isolation de l'Utilisateur
L'utilisateur `deluge` est configuré comme un compte système sécurisé, sans accès shell. Ses données de configuration sont strictement cloisonnées.

*   **Identité et environnement cible** :
    ```bash
    # Création du groupe et de l'utilisateur (à intégrer dans le script par Master-Code)
    groupadd -r deluge
    useradd -r -g deluge -d /var/lib/deluge -s /usr/sbin/nologin -c "Deluge Daemon" deluge
    
    # Création du Home et du répertoire de configuration
    mkdir -p /var/lib/deluge/.config/deluge
    mkdir -p /var/log/deluge
    
    # Attribution des permissions strictes
    chown -R deluge:deluge /var/lib/deluge /var/log/deluge
    chmod 750 /var/lib/deluge
    chmod 700 /var/lib/deluge/.config/deluge
    chmod 750 /var/log/deluge
    ```

## 3. Modèle de Permissions (Arborescence de données)
La racine unifiée de données imposée (`/home/lord-mahonheim/midgard_data/`) doit être accessible en lecture/écriture par le daemon de façon sécurisée.

*   **Modèle d'ACL Unix pour `midgard_data`** :
    ```bash
    mkdir -p /home/lord-mahonheim/midgard_data/
    
    # Le propriétaire et le groupe doivent être 'deluge'
    chown -R deluge:deluge /home/lord-mahonheim/midgard_data/
    
    # Permission '2770' :
    # - Lecture/Ecriture/Exécution pour le User et le Group.
    # - Aucun accès pour les "Others" (0).
    # - Le Set-Group-ID (SGID, '2') force tous les sous-dossiers et nouveaux fichiers à hériter du groupe 'deluge'.
    chmod 2770 /home/lord-mahonheim/midgard_data/
    ```

## 4. Spécifications Architecturales Systemd
Le code des unités systemd est conçu avec un durcissement élevé (Directives `Protect*`, `Restrict*`). Le `ProtectHome=read-only` permet une sécurité globale tout en ouvrant uniquement l'arborescence cible via `ReadWritePaths`.

### 4.1 Unité A : `/etc/systemd/system/deluged.service`
```ini
[Unit]
Description=Deluge BitTorrent Client Daemon (deluged)
Documentation=man:deluged
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deluge
Group=deluge
UMask=0027

# Environnement et exécution
Environment="HOME=/var/lib/deluge"
ExecStart=/usr/bin/deluged -d -c /var/lib/deluge/.config/deluge -l /var/log/deluge/daemon.log -L info

# Politique de redémarrage
Restart=on-failure
TimeoutStopSec=300

# ----------------------------------------------------
# ISOLATION DE SÉCURITÉ & RESSOURCES (Mitigation N2)
# ----------------------------------------------------
# MITIGATION CRITIQUE (OOM mmap libtorrent 2.x) :
MemoryMax=1G

ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/home/lord-mahonheim/midgard_data /var/lib/deluge /var/log/deluge
PrivateTmp=true
NoNewPrivileges=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
RestrictNamespaces=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
```

### 4.2 Unité B : `/etc/systemd/system/deluge-web.service`
```ini
[Unit]
Description=Deluge Web UI (deluge-web)
Documentation=man:deluge-web
After=network-online.target deluged.service
Wants=deluged.service

[Service]
Type=simple
User=deluge
Group=deluge
UMask=0027

Environment="HOME=/var/lib/deluge"
ExecStart=/usr/bin/deluge-web -d -c /var/lib/deluge/.config/deluge -l /var/log/deluge/web.log -L info

Restart=on-failure

# ----------------------------------------------------
# ISOLATION DE SÉCURITÉ
# ----------------------------------------------------
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/var/lib/deluge /var/log/deluge
PrivateTmp=true
NoNewPrivileges=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
RestrictNamespaces=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
```

## 5. Architectural Recommendations (Pour Master-Code)
1. **Rechargement du Daemon** : Obligation d'exécuter `systemctl daemon-reload` après la création/modification des fichiers `.service`.
2. **Ports** : Si une configuration UFW (pare-feu) est requise, le port web de l'UI (généralement `8112/tcp`) doit être exposé en accord avec la politique de filtrage de MIDGARD. Le port daemon (`58846/tcp`) peut rester restreint à `localhost`.
3. **Logrotate** : Il est recommandé que le noeud Master-Code génère une configuration `/etc/logrotate.d/deluge` basique pour purger `/var/log/deluge/*.log`.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
