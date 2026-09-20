# Google AI Studio / Gemini × Tesla × Antigravity — TERMINATOR, sans Chrome

**Révision : 2026-09-19 — procédure de référence de CODE_EDITOR.**
Statut : code testé hors ligne ; déploiement MIDGARD, clé Google et AGY **à valider localement**.
Les autres études sont historiques, pas des certifications d'exécution.

## 1. Architecture corrigée

```text
TERMINATOR sur MIDGARD (3 panneaux, diffusion clavier désactivée)
  ├─ Neovim/Helix : édition et revue humaine
  ├─ Git + mesures système : vérification des changements
  └─ tools/tesla_ai.py : prompt explicitement relu → HTTPS Gemini REST
                         ← .tesla-ai/review-<aléatoire>.md (0600)
                                     │
                         revue, copie manuelle des changements, tests
                                     │
                         AGY installé : capacités à vérifier, pas d'auto-run

SPARK MCP : /mcp authentifié → statut du processus + GitHub en lecture seule
            aucun outil shell, aucune génération Gemini facturable distante
```

**AI Studio est l'interface de gestion/prototypage ; le client utilise la Gemini
Developer API, pas une automatisation de l'interface web.** Il ne reproduit ni
les espaces de travail AI Studio, ni son Build mode. Il ne s'agit pas de Vertex AI.
Aucune dépendance Chrome, Chromium, Playwright, Node, Docker ou SDK Google pour
le client local : Python **3.10+**, bibliothèque standard uniquement.
TERMINATOR est un émulateur graphique de terminal, pas un navigateur ; le client
fonctionne aussi sans serveur graphique.

## 2. Diagnostic avant installation

Depuis la racine du dépôt, dans un terminal existant :

```bash
python3 tools/tesla_ai.py doctor
free -h
swapon --show
lsblk -d -o NAME,ROTA,SIZE,MODEL
vmstat 1 5
command -v terminator nvim hx agy antigravity
```

Ces commandes ne modifient pas le système. `doctor` ne fait aucun appel réseau et
n'affiche pas de secret. Les valeurs décrivent **la machine qui exécute la commande**,
pas nécessairement MIDGARD. Un périphérique virtuel peut masquer sa nature HDD/SSD.

Profil MIDGARD déclaré dans les archives : i7-10510U, environ 8 Go RAM, HDD.
Ce profil n'a pas été remesuré à distance. Sur MIDGARD :

- Un seul appel de génération à la fois ; commencer avec 2 048 tokens de sortie.
- Prompt limité à 64 Kio ; pas d'indexation de dépôt, de watcher ni de modèle local.
- Un éditeur léger ; n'activer que les LSP indispensables, à la demande.
- Observer `MemAvailable`, les colonnes `si/so` et `wa` de `vmstat` pendant une tâche.
  Si la mémoire disponible reste sous environ 1 Go ou que le swap/I/O sature,
  réduire les tâches concurrentes. Ce seuil est un point de départ, pas une garantie.
- **Ne pas** faire `swapoff -a`, monter `/tmp` à chaud ou réécrire `fstab`/`sysctl`.
  ZRAM peut aider, mais choisir taille, priorité du swap et swappiness après mesures
  et sauvegarde de la configuration existante. `swappiness=1` n'est pas universel,
  notamment avec ZRAM ; tmpfs consomme de la mémoire et peut lui-même être swappé.

## 3. TERMINATOR, sans remplacer votre configuration

Si nécessaire, installer les paquets de votre distribution après vérification :
`sudo apt install terminator neovim` (action manuelle, pas exécutée par ce guide).
Puis, depuis la racine du dépôt, **avant de charger une clé** :

```bash
terminator --no-dbus \
  --config "$PWD/EXPORT/To_RENA/CODE_EDITOR/templates/terminator-headless.config" \
  --layout tesla-headless
```

Le modèle ouvre trois shells, sans commande d'agent automatique, et borne le
scrollback à 2 000 lignes. Il ne touche pas `~/.config/terminator/config`.
La disposition graphique reste à vérifier sur votre installation TERMINATOR.
Alternative native : `Ctrl+Shift+E`, puis `Ctrl+Shift+O` dans le panneau gauche.
**Désactiver la diffusion des frappes vers tous les panneaux**, particulièrement
avant une saisie de secret. Vérifier le répertoire courant dans chaque panneau.

## 4. Authentification — clé éphémère dans le seul panneau IA

Précondition : une clé Gemini autorisée et un projet avec quotas adaptés.
Ne pas mettre la clé dans `.bashrc`, le dépôt, le prompt, une commande en clair ou
un argument de processus. Pas besoin de `GOOGLE_API_KEY` pour ce client : seule
`GEMINI_API_KEY` est lue, afin d'éviter une priorité ambiguë entre deux clés.

Dans Bash, ouvrir un sous-shell dédié ; les autres panneaux restent sans clé :

```bash
bash
set +x
read -r -s -p 'Clé Gemini (saisie masquée) : ' GEMINI_API_KEY
printf '\n'
export GEMINI_API_KEY
python3 tools/tesla_ai.py models --allow-cloud
```

La clé demeure accessible aux processus de ce sous-shell et potentiellement aux
processus autorisés du même compte : ce n'est pas un coffre-fort. Ne pas lancer
AGY ou du code généré dans ce sous-shell. Pour une utilisation persistante,
préférer le gestionnaire de secrets local déjà approuvé, sans keyring déverrouillé
avec mot de passe vide.

La documentation Google consultée annonce le passage aux **authorization keys
liées à un compte de service**, avec rejet des clés standard en septembre 2026.
Vérifier le type de votre clé et les règles actuelles du projet ; le client ne
crée ni ne migre de clé. Une erreur 403 n'implique pas uniquement une clé incorrecte.
Si aucune clé n'existe, suivre le provisionnement officiel depuis un environnement
approuvé **sans Chrome** ; ne pas confondre cette étape administrative avec le
parcours CLI quotidien. Ne jamais transmettre une clé dans une conversation.

## 5. Génération explicite, bornée, sans exécution

Choisir un identifiant retourné par `models` (pas de modèle ancien imposé) :

```bash
read -r -p 'Identifiant du modèle listé : ' TESLA_GEMINI_MODEL
export TESLA_GEMINI_MODEL
install -d -m 700 .tesla-ai
```

Dans le panneau éditeur **sans clé**, créer `.tesla-ai/prompt.txt` : ne conserver
que le contexte nécessaire, anonymisé, dont vous autorisez l'envoi à Google.
Les conditions de traitement des données et la facturation dépendent du projet
et du niveau de service. `--allow-cloud` est une autorisation d'envoi, pas une
preuve d'anonymisation ni une garantie de gratuité.

Dans le panneau IA :

```bash
python3 tools/tesla_ai.py generate --allow-cloud \
  --max-output-tokens 2048 --timeout 30 < .tesla-ai/prompt.txt
unset GEMINI_API_KEY
exit
```

Le programme renvoie le chemin JSON de l'artefact et `"executed": false` :

- Clé dans l'en-tête HTTPS `x-goog-api-key`, jamais dans l'URL ; redirections refusées.
- Réponse bornée à 2 Mio, génération à 8 192 tokens maximum configurable.
- Réponse vide, bloquée, tronquée ou avec appel d'outil : erreur, pas d'artefact.
- Aucun retry par défaut. `--retries 1` ou `2` autorise seulement les retries
  429/503. Un `Retry-After` numérique ≤ 30 s est respecté ; délai plus long/date :
  arrêt. Ne pas relancer aveuglément : quotas/coûts supplémentaires possibles.
- Timeout réseau par opération socket, **pas une échéance globale**. `Ctrl+C`
  interrompt le client ; cela n'annule pas forcément une facturation déjà engagée.
- Artefacts uniques, mode 0600, dossier 0700, pas de bit exécutable ni écrasement.
  Utiliser un workspace de confiance (parents non modifiables par un tiers).
- `.tesla-ai/` ignoré par Git ; aucune sauvegarde automatique du prompt/historique.
  Votre `prompt.txt` reste local jusqu'à suppression manuelle.

Dans le panneau éditeur sans clé, ouvrir le fichier indiqué pour revue :

```bash
# Remplacer le nom par le chemin réellement retourné.
nvim -u NONE -i NONE -n -- .tesla-ai/review-IDENTIFIANT.md
```

Traiter la sortie comme non fiable, y compris les commandes qu'elle suggère.
L'absence d'auto-exécution n'est pas un sandbox pour une exécution ultérieure.
Ne jamais faire `eval`, `source`, `bash` ou `python` sur la sortie sans validation.

## 6. Passage à Antigravity et Git

Le dépôt ne prouve ni la syntaxe `agy run`, ni celle de `antigravity run`, ni
l'existence d'une sandbox. **Ces commandes ne sont donc pas générées ni lancées.**
Dans le panneau sans clé, vérifier le binaire réellement installé avec
`command -v agy` / `command -v antigravity`, puis sa version et son `--help`.
Consigner la version et les protections disponibles avant d'y confier une tâche.

Après revue, reporter manuellement les changements souhaités dans des fichiers
ciblés ; exécuter les tests connus du projet dans un environnement isolé et sans
secrets. Une revue visuelle ou Bandit ne garantit pas l'innocuité.

```bash
git status --short --branch
git diff --check
git diff -- chemin/du/fichier
```

Rester sur la branche de travail courante. Ne pas effectuer de checkout, pull,
commit, push, application de patch ou changement de configuration automatique.
Le bridge n'a aucune dépendance aux hooks RTK, à Alexandria ou à un bus Tesla
privé ; leur présence et leur compatibilité restent à vérifier localement.

## 7. SPARK et vérification reproductible

La passerelle reste optionnelle pour Gemini. Elle n'obtient pas la clé Gemini.
Voir [sa procédure](../../../58-Spark-MCP-Gateway/README.md) pour l'authentification
et les limites d'exposition ; ne pas ouvrir un tunnel pour ce seul client CLI.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r 58-Spark-MCP-Gateway/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Le client seul se teste sans dépendance externe :
`python3 -m unittest discover -s tests -p test_tesla_ai.py -v`.

Voir [l'audit](AUDIT_AIStudio_MIDGARD_2026-09-19.md) pour les défauts, preuves et
limites. Aucun appel Gemini réel, aucune session graphique TERMINATOR, aucune
connexion SPARK distante ni exécution AGY n'est certifiée par ces tests hors ligne.

## Sources primaires consultées

- [Clés et migration Google](https://ai.google.dev/gemini-api/docs/api-key)
- [REST models.list / capacités](https://ai.google.dev/api/models)
- [REST generateContent](https://ai.google.dev/api/generate-content)
- [SDK MCP Python officiel](https://github.com/modelcontextprotocol/python-sdk)

Ces références évoluent ; le modèle disponible et le provisionnement du projet
font foi lors de la validation réelle. Une échéance Firebase n'est pas un
prérequis technique de cette intégration.
