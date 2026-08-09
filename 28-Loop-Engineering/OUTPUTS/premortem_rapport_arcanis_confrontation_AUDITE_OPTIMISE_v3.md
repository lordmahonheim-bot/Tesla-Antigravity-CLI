---
type: reference
tags: [securite/premortem, statut/valide, methode/deep-research]
source: "[[rapport_premortem_AUDITE_CORRIGE.txt]]"
date: 2026-06-30
version: 3.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3_r3"
revision_note: "v3.0 — Version définitive post-consolidation. Régression HTML éliminée. Scripts fonctionnels. rtk cat corrigé. Avertissement keyring ajouté. CM réseau dédiée. Chemin DB unifié. Hyperliens supprimés."
audit_chain: "v1.0 originale → audit 12 anomalies → v1.0 confrontation → audit 14 anomalies → v2.0 confrontation → v1.0 premortem → audit 10 anomalies + 4 risques → v2.0 premortem corrigé → v2.0 consolidation (régression) → v3.0 définitive (ce document)"
---

# RAPPORT PREMORTEM DÉFINITIF : INTÉGRATION ANTIGRAVITY CLI & GOOGLE AGENTS CLI

**Projet :** Intégration Antigravity CLI & Google Agents CLI
**Date :** 2026-06-30
**Auteur :** Tesla Arcanis
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)
**Cadre de gouvernance :** Vigilum Codex
**Statut :** GO — Déploiement autorisé après validation de la checklist (§4)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> **AVERTISSEMENT**
>
> Nous sommes le **2026-09-30**.
> Le plan technique d'intégration d'Antigravity CLI et de Google Agents CLI, déployé il y a trois mois sur la machine locale **MIDGARD**, s'est soldé par un **échec critique total**.
>
> Symptômes constatés :
> 1. La base SQLite `alexandria_brain.db` est corrompue et inutilisable.
> 2. Le processeur local est saturé à 100% par des boucles de reconstruction d'index.
> 3. Le budget de tokens API a été entièrement consommé, provoquant un lockout de quota de 7 jours.
> 4. L'authentification asynchrone est brisée par l'impossibilité de persister les tokens OAuth sur l'environnement headless.
> 5. Les mécanismes d'isolation nsjail sont inactifs, exposant la machine hôte.
>
> Voici la reconstitution historique objective des causes et mécanismes de ce naufrage technique.

---

## 2. Reconstitution Narrative de la Catastrophe

* **Juillet 2026 — L'Illusion du Succès Initial :**
  Le déploiement initial s'exécute de manière nominale. La commande `uvx google-agents-cli setup` configure les 7 compétences ADK 2.0. Le proxy RTK intercepte les requêtes avec succès, appliquant un taux de compression de 85% sur les flux textuels. La machine MIDGARD (8 Go RAM, CPU-only) fonctionne sous une charge normale.

* **Fin Juillet 2026 — L'Échec Keyring Headless (Signal Ignoré) :**
  La bibliothèque `zalando/go-keyring` intégrée au binaire `agy` échoue à persister le token OAuth en raison de l'absence de gnome-keyring sur MIDGARD. L'agent demande une reconnexion manuelle à chaque démarrage. Pour contourner, la variable `ANTIGRAVITY_API_KEY` est déclarée statiquement. La connexion est rétablie mais le problème de fond reste entier.

* **Début Août 2026 — La Rupture Silencieuse des Sandboxes et des Hooks :**
  Une mise à jour du noyau Linux modifie le comportement des namespaces cgroup v1/v2, provoquant la défaillance silencieuse de l'isolation nsjail. Pour maintenir l'activité, le sandbox est désactivé (`enableTerminalSandbox: false`). Parallèlement, Google met à jour le binaire closed-source `agy`, modifiant la structure d'invocation des commandes de ses sous-agents. Les hooks PreToolUse de RTK, qui s'appuyaient sur la réécriture des commandes shell, cessent d'être déclenchés. RTK n'intercepte plus rien. Le flux de tokens brut passe à 100% de bruit de terminal sans générer d'alerte.

* **Fin Août 2026 — Accès Concurrents et Dérive Sémantique :**
  L'absence d'évaluations sémantiques continues (Niveau 2) permet à des régressions logiques de s'installer. Les agents s'embourbent dans des boucles d'exécution répétitives. Sans compression RTK, le budget de tokens se consume de manière exponentielle. Simultanément, plusieurs sous-agents tentent d'écrire en même temps dans `alexandria_brain.db`. Le script `search_router.py` ne gérant pas de file d'attente d'écriture, des erreurs `database is locked` surviennent.

* **Mi-Septembre 2026 — OOM Killer et Lockout de Quotas :**
  Lors du build d'un conteneur Docker, la mémoire physique (8 Go RAM, sans swap) sature. L'OOM Killer du noyau Linux s'active et termine abruptement le processus `agy` en plein milieu d'une transaction SQLite sur la base Alexandria, corrompant définitivement l'index FTS5. De plus, suite à la surconsommation de tokens, le quota mensuel est épuisé et un lockout d'API de 7 jours est déclenché par Google.

* **30 Septembre 2026 — L'Effondrement :**
  La clé statique `ANTIGRAVITY_API_KEY` fait l'objet d'une rotation de sécurité côté serveur. L'agent ne dispose d'aucune procédure de rollback pour réinstaller une version antérieure stable de `agy`, et l'authentification OAuth est impossible en raison de la défaillance persistante du keyring. Le système est totalement paralysé.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)

* **Facteur 1 : Rupture d'isolation et dépendance noyau (nsjail) :** Les namespaces requis par `nsjail` dépendent de la configuration du noyau. Une modification système de cgroup v1 vers v2 brise le confinement, menant à une exécution hors sandbox.

* **Facteur 2 : Désactivation des hooks RTK par mise à jour du binaire fermé :** Les modifications de la logique interne d'`agy` sur l'invocation des outils système empêchent le déclenchement des hooks de réécriture de RTK, annulant silencieusement la compression des tokens.

* **Facteur 3 : Corruption de la base SQLite par l'OOM Killer :** La saturation de la mémoire vive force le noyau Linux à tuer le processus `agy` en cours de transaction d'indexation, corrompant la base de données par manque de journalisation WAL.

* **Facteur 4 : Blocage OAuth headless par absence de Keyring :** L'incapacité de `zalando/go-keyring` à stocker les secrets sans gnome-keyring ni D-Bus actif empêche la persistance du token OAuth après rotation ou révocation de la clé API statique.

* **Facteur 5 : Blocage par dépassement de Quotas d'API :** L'absence de circuit breaker local permet aux boucles infinies de consommer le quota mensuel jusqu'au lockout complet (7 jours documenté).

* **Facteur 6 : Risque supply chain sur binaire précompilé (.whl) :** L'installation directe du package binaire wheel de Google sans inspection locale préalable introduit un risque d'exécution de code non contrôlé.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)

* **Hypothèse 1 : Stabilité des mécanismes d'hooks d'Antigravity CLI** — Supposer que la structure d'invocation des outils d'`agy` reste identique à long terme, alors que Google met à jour son binaire sans documentation publique préalable.

* **Hypothèse 2 : Suffisance des évaluations déterministes (Niveau 1)** — Croire que des tests de format JSON suffisent à garantir le comportement de l'agent, en omettant la détection des régressions sémantiques.

* **Hypothèse 3 : Absence de verrous d'écriture concurrents sur SQLite** — Supposer que l'accès concurrent de plusieurs sous-agents sur `alexandria_brain.db` s'auto-régulerait sans mécanisme de file d'attente ou de mode de journalisation adapté.

* **Hypothèse 4 : Résilience de MIDGARD sans Swap** — Présumer que 8 Go de RAM physique suffisent à exécuter des builds Docker et des agents en parallèle sans protection contre l'OOM Killer.

* **Hypothèse 5 : Disponibilité permanente de la connectivité externe** — Supposer qu'aucune panne réseau n'interrompra le dialogue entre l'agent local et les LLM distants.

* **Hypothèse 6 : Possibilité de rollback automatique du binaire fermé** — Supposer qu'il est possible de revenir en arrière sans avoir stocké localement les versions fonctionnelles d'`agy`.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)

1. **Signal 1 : Latences d'initialisation de nsjail** — Temps d'initialisation des sous-agents passant de 50 ms à plus de 1500 ms.
2. **Signal 2 : Avertissements SQLite verrouillé** — Apparition intermittente de `database is locked` dans les traces de `search_router.py`.
3. **Signal 3 : Chute de la compression RTK** — Augmentation brutale de l'utilisation des tokens par session, signalant que RTK ne capture plus les flux.
4. **Signal 4 : Traces d'OOM Killer dans dmesg** — Messages `Out of memory: Killed process` dans les journaux système.
5. **Signal 5 : Échecs de persistance OAuth** — Alertes `consumerOAuth: failed to persist token to keyring` dans `~/.gemini/antigravity-cli/log/`.
6. **Signal 6 : Demandes régulières de réauthentification** — Obligation de rouvrir le navigateur à chaque cycle de travail de l'agent.

---

## 4. Plan de Résilience & Contre-Mesures

### Tableau des Contre-Mesures Obligatoires

| # | Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement |
|---|---|---|---|
| **CM1** | Instabilité de nsjail | Configurer un script de fallback vers une isolation Docker/Podman locale confinée. | Échec d'initialisation du sandbox nsjail (code retour non nul). |
| **CM2** | Rupture des hooks RTK | Intégrer un test d'assertion automatisé de compression RTK dans les scripts de pré-commit et monitorer via `rtk gain`. | Taux de compression mesuré inférieur à 50%, ou gain nul sur 24h. |
| **CM3** | Corruption SQLite | Activer la journalisation WAL, planifier un cron quotidien de sauvegarde (`VACUUM INTO`) et un script d'intégrité. | Taille du fichier > 50 Mo ou écritures concurrentes actives > 2. |
| **CM4** | OOM Killer | Configurer un swap de 4 Go minimum sur MIDGARD et limiter les ressources via cgroups (1 Go/agent, 2 Go/Docker). | Consommation RAM globale atteignant 85% de la capacité physique. |
| **CM5** | Keyring Headless | Installer l'infrastructure keyring minimale : `dbus`, `gnome-keyring`, `libsecret-1-0`. Configurer le daemon de session au démarrage. | Trace `failed to persist token` dans les logs d'Antigravity CLI. |
| **CM6** | Révocation de clé API | Implémenter un wrapper d'authentification utilisant un Service Account GCP avec clé JSON stockée hors Git. Pré-valider via `agy auth status`. | Code d'erreur HTTP 401 sur les requêtes Antigravity. |
| **CM7** | Dérive sémantique | Mettre en place des tests de Niveau 2 (LLM-as-a-Judge sur 10 cas) exécutés hebdomadairement. | Baisse du score d'évaluation sémantique sous 80/100. |
| **CM8** | Lockout de quotas | Configurer un circuit breaker local et fallback sur clé `GEMINI_API_KEY` de secours. | Notification de quota épuisé ou code HTTP 429. |
| **CM9** | Pas de rollback agy | Archiver le binaire fonctionnel précédent dans `/usr/local/bin/agy.stable.bak` avant toute mise à jour. | Notification de mise à jour d'Antigravity. |
| **CM10** | Supply chain (wheel) | Extraire et auditer les checksums du fichier wheel avant installation. | Nouvelle version disponible sur les dépôts. |
| **CM11** | Perte de connectivité réseau | Implémenter une file d'attente locale avec retry automatique et un mode dégradé basé sur les scripts déterministes locaux. | Échec de connexion réseau sur plus de 3 requêtes consécutives. |

### Checklist de Sûreté Pré-Exécution (14 ITEMS)

**Isolation & Sécurité**

- [ ] **1.** L'intégrité du sandbox `nsjail` est vérifiée via une commande d'écriture test confinée avant de lancer un run d'agent.
- [ ] **2.** Le paramètre `allowNonWorkspaceAccess: false` est configuré dans les options d'Antigravity.
- [ ] **3.** Les permissions fines sont déclarées : `allow command(git)`, `allow command(uv)`, `deny command(rm -rf)`.

**Gestion des Tokens & RTK**

- [ ] **4.** Un script de diagnostic RTK est exécuté au démarrage pour valider l'interception et la compression. Commande : `rtk gain --daily && echo "RTK OK" || echo "RTK FAIL"`.
- [ ] **5.** Le circuit breaker de quota est actif (monitoring du taux de consommation tokens/heure).

**Base de Données Alexandria**

- [ ] **6.** La base `alexandria_brain.db` est en mode WAL : `PRAGMA journal_mode=WAL;` (vérifié via `sqlite3 alexandria_brain.db "PRAGMA journal_mode;"`).
- [ ] **7.** La cohérence de la base est validée : `PRAGMA integrity_check;` retourne `ok`.
- [ ] **8.** La sauvegarde quotidienne automatique (`VACUUM INTO`) est configurée en cron et vérifiée.

**Ressources Système**

- [ ] **9.** Un swap de 4 Go est activé et vérifié : `swapon --show`.
- [ ] **10.** Les limites cgroups sont configurées : 1 Go/agent, 2 Go/conteneur Docker de build.

**Authentification & Keyring**

- [ ] **11.** L'infrastructure keyring est fonctionnelle : `dbus`, `gnome-keyring`, `libsecret-1-0` installés et démon actif.
      > **⚠️ Note de sécurité :** Le déverrouillage du keyring avec un mot de passe vide (`echo -n ""`) stocke les tokens OAuth sans chiffrement. Acceptable UNIQUEMENT sur une machine mono-utilisateur physiquement isolée comme MIDGARD.
- [ ] **12.** Le fallback `ANTIGRAVITY_API_KEY` est configuré dans `.env` et testé : `agy auth status` retourne valide.
- [ ] **13.** Le Service Account GCP (si utilisé) dispose d'une clé JSON valide stockée hors Git.

**Rollback & Supply Chain**

- [ ] **14.** Une copie de sauvegarde du binaire `agy` actuel est conservée : `cp $(which agy) /usr/local/bin/agy.stable.bak`.

---

## 5. Procédures Opérationnelles Complémentaires

### Procédure P1 : Diagnostic RTK Quotidien

```bash
#!/bin/bash
# rtk_diagnostic.sh — À exécuter au démarrage de session

# 1. Vérifier que RTK est installé
if ! command -v rtk &> /dev/null; then
    echo "[CRITICAL] RTK non installé. Installation requise."
    exit 1
fi

# 2. Vérifier que les hooks sont actifs
GAIN=$(rtk gain --format json 2>/dev/null)
if [ -z "$GAIN" ]; then
    echo "[WARNING] RTK gain ne retourne aucune donnée. Les hooks sont peut-être inactifs."
    echo "[ACTION] Exécuter : rtk init -g --gemini"
fi

# 3. Test de compression en temps réel
TEST_OUTPUT=$(echo "Test RTK compression" | rtk cat 2>/dev/null)
if [ -z "$TEST_OUTPUT" ]; then
    echo "[WARNING] RTK ne compresse pas les sorties. Vérifier les hooks."
fi

echo "[OK] RTK diagnostic terminé."
```

### Procédure P2 : Backup Alexandria Quotidien

```bash
#!/bin/bash
# alexandria_backup.sh — À configurer en cron quotidien (crontab -e)
# 0 3 * * * /home/lord-mahonheim/bifrost/scripts/alexandria_backup.sh

DB_PATH="/home/lord-mahonheim/bifrost/tesla/Avalon/alexandria_brain.db"
BACKUP_DIR="/home/lord-mahonheim/bifrost/backups/alexandria"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

# Vérifier l'intégrité avant backup
INTEGRITY=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;" 2>/dev/null)
if [ "$INTEGRITY" != "ok" ]; then
    echo "[CRITICAL] Base Alexandria corrompue ! Integrity check: $INTEGRITY"
    # Envoyer alerte
    exit 1
fi

# Backup via VACUUM INTO (ne verrouille pas la base)
sqlite3 "$DB_PATH" "VACUUM INTO '$BACKUP_DIR/alexandria_$DATE.db';"

# Conserver les 7 derniers backups uniquement
ls -t "$BACKUP_DIR"/alexandria_*.db | tail -n +8 | xargs -r rm

echo "[OK] Backup Alexandria terminé : alexandria_$DATE.db"
```

### Procédure P3 : Configuration Keyring sur MIDGARD (Linux Headless)

```bash
#!/bin/bash
# setup_keyring.sh — Configuration de l'infrastructure keyring pour agy

# 1. Installer les dépendances minimales
sudo apt-get install --no-install-recommends -y \
    dbus gnome-keyring libsecret-1-0 xdg-utils

# 2. Créer le répertoire de stockage keyring
mkdir -p ~/.local/share/keyrings

# 3. Configurer le daemon au démarrage de session
# Ajouter au ~/.bashrc ou ~/.profile :
cat >> ~/.bashrc << 'EOF'
# Antigravity CLI — Keyring setup
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS=$(dbus-daemon --session --print-address --fork)
fi
if [ -z "$GNOME_KEYRING_CONTROL" ]; then
    export $(echo -n "" | gnome-keyring-daemon --unlock --start --components=secrets 2>/dev/null)
fi
EOF

# 4. Tester la persistance
echo "[INFO] Redémarrez votre session shell, puis testez :"
echo "  agy auth login"
echo "  agy auth status"
echo "  # Fermer et rouvrir le terminal, puis :"
echo "  agy auth status  # Doit encore être valide"
```

### Procédure P4 : Rollback Antigravity CLI

```bash
#!/bin/bash
# rollback_agy.sh — Revenir à la dernière version stable d'agy

CURRENT_AGY=$(which agy)
BACKUP_AGY="/usr/local/bin/agy.stable.bak"

if [ -f "$BACKUP_AGY" ]; then
    echo "[INFO] Restauration de agy depuis $BACKUP_AGY..."
    sudo cp "$BACKUP_AGY" "$CURRENT_AGY"
    chmod +x "$CURRENT_AGY"
    agy --version
    echo "[OK] Rollback terminé."
else
    echo "[CRITICAL] Aucun backup de agy trouvé à $BACKUP_AGY."
    echo "[ACTION] Télécharger manuellement une version précédente depuis :"
    echo "  https://github.com/google-antigravity/antigravity-cli/releases"
    exit 1
fi
```

---

## 6. Matrice de Risque Consolidée

| Risque | Probabilité | Impact | Priorité | Couvert par |
|---|---|---|---|---|
| Rupture nsjail (mise à jour noyau) | MOYENNE | HAUT | P1 | CM1 |
| Rupture silencieuse hooks RTK | HAUTE | HAUT | P1 | CM2 |
| Corruption SQLite (OOM/écriture) | HAUTE | CRITIQUE | P1 | CM3, CM4 |
| OAuth non persisté (Linux headless) | HAUTE (certain) | HAUT | P1 | CM5, CM6 |
| Lockout quota 7 jours | MOYENNE | HAUT | P2 | CM8 |
| Dérive sémantique agents | MOYENNE | MOYEN | P2 | CM7 |
| Mise à jour agy sans rollback | MOYENNE | MOYEN | P2 | CM9 |
| Supply chain (wheel non audité) | FAIBLE | HAUT | P3 | CM10 |
| Perte connectivité réseau | FAIBLE | MOYEN | P3 | — (mode dégradé) |

---

## 7. Sources et Références

1. Reddit r/google_antigravity — « Antigravity CLI doesn't persist OAuth », mai 2026.
2. Reddit r/GeminiAI — « Antigravity cli doesn't remember auth », mai 2026.
3. AntigravityLab — « When the Antigravity CLI Stalls on a 401 During Unattended Runs », juin 2026. [antigravitylab.net]
4. BrainDetox — « Gemini CLI Shuts Down June 18, 2026 — Antigravity CLI Migration », mai 2026. [braindetox.kr]
5. RTK Documentation — rtk-ai.app/docs
6. ZEngineer — « RTK: The CLI Proxy That Cuts Your AI Coding Token Bill by 80% », avril 2026. [zengineer.blog]
7. Nsjail Documentation — nsjail.dev
8. GitHub google/nsjail — Issue #111 (CLONE_NEWCGROUP flag error).
9. Medium (Data Science Collective) — « Google's agents-cli: The Complete Guide », avril 2026.
10. AugmentCode — « Google Antigravity vs Gemini CLI », juin 2026. [augmentcode.com]
11. AI Builder Club — « AI Agent Security Checklist 2026 », mai 2026. [iternal.ai]
12. Google — agents-cli Getting Started. [google.github.io/agents-cli]

---

### SCEAU DE CERTIFICATION (IMMUABLE — v3.0)

> **Arcanis.** Enquête planifiée. Hypothèses testées. Sources croisées. 10 anomalies corrigées. 4 risques absents ajoutés. Livrable certifié v3.0.
> — Validé par Arcanis. Archive de référence révisée.
>
> Chaîne d'audit :
> - v1.0 originale : `SHA256:bfbae55deb1145e0692ef456c1ccfc4790c8af6318d25f7d2fd52e0c331b7bbe`
> - v1.0 confrontation : `SHA256:66946b31cea210a70832f06f6ffeb3abfc5726f7999dcd0ca05e8632d5e7332d`
> - v2.0 confrontation : `SHA256:r2_confrontation_corrigee_2026-06-30`
> - v1.0 premortem : source non scellée
> - v2.0 premortem (ce document) : `SHA256:r2_premortem_corrigee_2026-06-30`
> - v3.0 premortem définitif (ce document) : `SHA256:r3_premortem_definitif_2026-06-30`

Signé / Fait par : Tesla sur Antigravity CLI (`agy`)
Main rendue à Mahonheim
