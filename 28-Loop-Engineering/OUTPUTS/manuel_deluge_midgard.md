# Manuel Opératoire : Déploiement Deluge (Nœud 5)

**Tags:** #Deluge #Midgard #Torrent #Documentation #SysAdmin #Zéro-Touch
**Date:** 2026-07-26

Ce manuel détaille la procédure de déploiement et de gestion du client BitTorrent Deluge sur Midgard via le script d'installation automatisé.

---

## 1. Exécution du Déploiement (Zéro-Touch)

Le script d'installation configure `deluged`, `deluge-web` et `deluge-console`, en sécurisant l'environnement sous un utilisateur de service dédié (`deluge`).

Exécutez le script avec les privilèges d'administration :

```bash
sudo bash /home/lord-mahonheim/bifrost/tesla/.agents/scripts/install_deluge_midgard.sh
```

> [!IMPORTANT]
> L'installation est entièrement automatisée. Attendez la fin de l'exécution pour passer aux étapes de vérification.

## 2. Vérification de l'État des Services

Vérifiez que les démons système sont actifs et tournent correctement :

```bash
# Vérifier le daemon principal (deluged)
sudo systemctl status deluged

# Vérifier l'interface web (deluge-web)
sudo systemctl status deluge-web
```

> [!TIP]
> Si un service nécessite un redémarrage, utilisez : `sudo systemctl restart deluged deluge-web`

## 3. Accès à l'Interface Web (WebUI)

L'interface Web est accessible depuis n'importe quel navigateur sur le réseau.

- **URL d'accès :** `http://<IP_DE_MIDGARD>:8112`
- **Mot de passe par défaut :** `deluge`

> [!WARNING]
> Lors de la première connexion, le système vous invitera à modifier le mot de passe par défaut. Il est impératif d'appliquer ce changement immédiatement par mesure de sécurité.

## 4. Accès CLI Headless (Console)

Puisque le daemon est exécuté sous l'utilisateur de service restreint `deluge`, vous **devez** impérativement usurper cette identité pour utiliser la console CLI. 

Pour lancer la console interactive :

```bash
sudo -u deluge deluge-console
```

> [!NOTE]
> Ne lancez pas `deluge-console` avec votre compte standard ou via `root`. Seul l'utilisateur `deluge` possède les configurations requises (`~/.config/deluge/`) pour s'authentifier automatiquement au daemon local.
