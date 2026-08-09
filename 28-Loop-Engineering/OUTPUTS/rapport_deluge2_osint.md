# Rapport d'OSINT Technique : Deluge 2.x & libtorrent 2.x (2026)

**Mission :** Veille technique sur la sécurisation de Deluge 2.x, l'usage de deluge-console et la mitigation des problèmes de cache RAM (mmap) induits par libtorrent 2.x sur MIDGARD.

---

## 1. Sécurisation du Daemon `deluged` et de sa WebUI
- **Daemon (`deluged` - Port 58846)** :
  - **Fichier `auth`** : Configurer `~/.config/deluge/auth` au format `user:password:10` (10 octroie les droits admin). 
  - **Permissions** : Sécuriser ce fichier avec un `chmod 600` pour empêcher toute fuite de credentials locaux.
  - **Exposition Distante** : L'option `allow_remote` dans `core.conf` ne doit être passée à `True` que si c'est strictement nécessaire.
  - **Privilèges** : Ne jamais exécuter le daemon en tant que `root`. Si conteneurisé (via linuxserver.io par ex.), mapper correctement `PUID` et `PGID`.
- **WebUI (Port 8112)** :
  - Modifier immédiatement le mot de passe par défaut (`deluge`).
  - **Exposition** : Ne **jamais** exposer le port 8112 directement sur internet. Le masquer derrière un tunnel VPN (Tailscale/WireGuard) ou un reverse proxy sécurisé (Traefik, Nginx) imposant l'HTTPS.

---

## 2. Usage Headless de `deluge-console` en local (Conformité TRaSH Guides)
- **Concept** : Le "Thin Client" en mode headless permet l'administration via la CLI (pratique pour l'automatisation de scripts comme `deluge-mover.py`).
- **Lancement** :
  - Si le daemon tourne en systemd sous un user spécifique : `sudo -u deluge deluge-console`.
  - Via Docker : Exécuter la console dans le shell interactif du conteneur (`docker exec -it <container> deluge-console`).
- **Intégration TRaSH Guides (Midgard)** : 
  - L'arborescence unifiée `/home/lord-mahonheim/midgard_data/{torrents, media}/` doit être montée **à sa racine** dans le conteneur (ex. `/data`). C'est indispensable pour que Sonarr/Radarr et Deluge partagent le même mountpoint et puissent déclencher des **Hardlinks (Atomic Moves)** instantanés pour éviter la duplication des fichiers.
- **Dépannage d'accès local** : En cas d'erreur "Password does not match", le client local (localclient) doit être proprement renseigné dans le fichier `auth`, ou la connexion `hostlist.conf` forcée sur le profil défini.

---

## 3. Best Practices : Mitigation du Cache libtorrent 2.x (mmap)
**Contexte (Le "Faux" Memory Leak)** : Avec libtorrent 2.x, le modèle d'E/S a été revu pour utiliser des **Memory-Mapped Files (`mmap`)**. Au lieu d'utiliser un cache géré manuellement, le moteur délègue le cache des pièces du torrent au système d'exploitation (OS). Conséquence : la RAM apparente (sous `buff/cache`) s'envole, ce qui est souvent pris à tort pour une fuite mémoire, mais peut parfois provoquer un OOM-kill du container si la RAM est physiquement saturée.

**Stratégies 2026 de Mitigation :**

1. **Systemd `MemoryMax` (Recommandé en Bare-metal)** :
   - Encadrer la consommation mémoire au niveau du cgroup pour éviter l'instabilité de l'OS.
   - Éditer `sudo systemctl edit deluged` et ajouter :
     ```ini
     [Service]
     MemoryMax=1G
     ```
     *(Ajuster la limite selon la RAM physique allouée à MIDGARD).*
2. **Paramétrage via le plugin `ltConfig`** :
   - Charger l'extension `ltConfig` (configurable via le client GTK bureau pointé sur le daemon headless).
   - Sélectionner le preset **"Low Memory"** pour réduire les buffers, ou brider manuellement les paramètres spécifiques du cache libtorrent.
3. **Downgrade Stratégique (Fallback Docker)** :
   - Si les crashs OOM persistent en production malgré les limites, la communauté recommande l'usage d'images Docker taggées `libtorrentv1` qui reviennent à l'ancien paradigme d'E/S de libtorrent 1.2.x, exempt de cette gestion agressive mmap.
4. **Surveillance de la RAM** : Analyser avec `free -m`. Si la mémoire est majoritairement affectée dans `buff/cache`, c'est le comportement normal attendu de libtorrent 2.x. L'OS libérera ce cache en cas de pression mémoire ailleurs sur le serveur.
