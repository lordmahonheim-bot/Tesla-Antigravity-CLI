# Google AI Studio × MIDGARD × Tesla × Antigravity
## Solution retenue et plan d’intervention — TERMINATOR, sans Chrome

**Date : 20 septembre 2026**
**Nature : guide de déploiement et de réception sur MIDGARD.**

## 1. Définir le résultat final

À l’issue de l’intervention, MIDGARD dispose d’un parcours opérationnel dans **TERMINATOR** permettant de transmettre un prompt explicitement approuvé à l’API Gemini, de récupérer une réponse dans un fichier privé et de la relire avant toute utilisation dans l’écosystème Tesla.

Le résultat final comprend :

1.1. Une fenêtre TERMINATOR organisée en trois panneaux : **édition**, **contrôle**, **IA**.

1.2. Le client `tools/tesla_ai.py`, fonctionnant avec Python 3.10 ou supérieur, sans Chrome et sans dépendance Python externe pour les appels Gemini.

1.3. Un diagnostic matériel local enregistré et les 28 tests du client et de la passerelle SPARK exécutés avec succès.

1.4. Une génération Gemini réelle, autorisée explicitement, produisant un artefact privé, non exécutable et relu par l’opérateur.

1.5. Une session IA terminée sans clé Gemini conservée dans ses variables d’environnement.

1.6. Un artefact approuvé disponible pour une reprise **manuelle** dans le workflow Antigravity existant. La procédure ne lance ni code généré ni commande d’exécution AGY.

**La réception n’est acquise qu’après l’étape 13 sur MIDGARD. Les tests déjà réussis dans l’environnement d’audit ne remplacent pas cette réception locale.**

## 2. Fixer la solution retenue

2.1. Utiliser exclusivement la chaîne suivante :

```text
TERMINATOR sur MIDGARD
    → prompt local relu et approuvé
    → tools/tesla_ai.py
    → API Gemini en HTTPS
    → artefact Markdown privé
    → retrait de la clé et fermeture du sous-shell IA
    → revue humaine
    → mise à disposition pour le workflow Antigravity manuel
```

2.2. Utiliser **Neovim** pour l’édition et la revue. Ne pas ajouter de plugin IA, de modèle local ou d’indexation automatique du dépôt.

2.3. Limiter la génération à un appel à la fois, 64 Kio de prompt maximum et 2 048 tokens de sortie. Conserver zéro relance automatique et un délai réseau de 30 secondes par opération socket.

2.4. Conserver SPARK comme service distinct en lecture seule. Ses corrections sont vérifiées par les tests ; cette intervention ne démarre pas de passerelle, ne crée pas de tunnel et ne modifie pas son déploiement existant. La clé Gemini ne lui est jamais transmise.

2.5. Conserver les réglages actuels du noyau, du swap, de ZRAM et de `/tmp`. Cette intervention ne modifie ni `sysctl`, ni `fstab`, ni la configuration personnelle de TERMINATOR.

## 3. Réunir les prérequis et appliquer la règle d’exécution

**Lieu : MIDGARD, dans le terminal local existant.**

3.1. Disposer d’une session graphique Ubuntu/Debian, des droits nécessaires pour installer des paquets et d’un accès réseau autorisé aux dépôts de paquets ainsi qu’à l’API Gemini.

3.2. Disposer d’une copie locale du dépôt contenant les corrections auditées, notamment :

```text
tools/tesla_ai.py
tests/test_tesla_ai.py
tests/test_spark_gateway.py
58-Spark-MCP-Gateway/requirements.txt
EXPORT/To_RENA/CODE_EDITOR/templates/terminator-headless.config
```

3.3. Disposer au préalable d’une clé Gemini valide, accessible depuis le gestionnaire de secrets approuvé. Le projet Google associé doit avoir des autorisations, quotas, conditions de traitement des données et limites de dépenses acceptés. Ne pas inscrire cette clé dans le document ou le dépôt.

3.4. Disposer du workflow Antigravity local déjà installé et validé pour les tâches manuelles habituelles. Son installation et sa configuration ne sont pas modifiées par cette procédure.

3.5. Exécuter les étapes dans l’ordre, puis les commandes de chaque bloc **ligne par ligne**. N’avancer qu’après obtention du résultat attendu. **Toute commande en erreur ou tout contrôle non satisfait arrête l’intervention à l’étape concernée.** Ne pas contourner un contrôle, relancer une génération ou appliquer un correctif système pendant ce parcours.

**Critère de passage : les prérequis 3.1 à 3.4 sont réunis et la règle 3.5 est appliquée.**

## 4. Positionner le dépôt et préparer le dossier privé

**Lieu : terminal local existant.**

4.1. Ouvrir un shell Bash dédié, désactiver la trace des commandes et retirer les variables Gemini éventuellement héritées :

```bash
bash --noprofile --norc
set +x
unset GEMINI_API_KEY GOOGLE_API_KEY
umask 077
```

4.2. Saisir le chemin absolu du dépôt local :

```bash
read -r -e -p 'Chemin absolu du dépôt Tesla-Antigravity-CLI : ' TESLA_ROOT
cd -- "$TESLA_ROOT"
export TESLA_ROOT="$(pwd -P)"
test "$(git rev-parse --show-toplevel)" = "$TESLA_ROOT"
git status --short --branch
```

4.3. Vérifier les fichiers nécessaires :

```bash
test -f tools/tesla_ai.py
test -f tests/test_tesla_ai.py
test -f tests/test_spark_gateway.py
test -f 58-Spark-MCP-Gateway/requirements.txt
test -f EXPORT/To_RENA/CODE_EDITOR/templates/terminator-headless.config
```

4.4. Créer un dossier privé dédié à cette intervention :

```bash
test ! -L .tesla-ai
install -d -m 700 .tesla-ai
mkdir -m 700 .tesla-ai/intervention
git check-ignore .tesla-ai/intervention/prompt.txt
git status --porcelain=v1 > .tesla-ai/intervention/git-avant.txt
```

Le dossier `intervention` doit être nouveau. Sa présence préalable fait échouer `mkdir` et arrête cette réception, afin de ne pas mélanger ou écraser les éléments d’une exécution antérieure.

**Critère de passage : le dépôt est celui attendu, tous les fichiers sont présents, le dossier privé est créé et `git check-ignore` affiche le chemin contrôlé. La branche courante et les modifications existantes sont conservées.**

## 5. Installer les outils et vérifier le diagnostic local

**Lieu : même terminal, à la racine du dépôt.**

5.1. Installer les outils retenus :

```bash
sudo apt update
sudo apt install python3 python3-venv git terminator neovim procps util-linux
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10 minimum requis"'
command -v python3 git terminator nvim free swapon lsblk vmstat
```

5.2. Enregistrer le diagnostic et afficher les mesures système :

```bash
python3 tools/tesla_ai.py doctor > .tesla-ai/intervention/diagnostic.json
cat .tesla-ai/intervention/diagnostic.json
free -h
swapon --show
lsblk -d -o NAME,ROTA,SIZE,MODEL
vmstat 1 5
```

5.3. Confirmer que les mesures proviennent bien de MIDGARD, que Python est compatible et que TERMINATOR, Neovim et Git sont détectés. Pour cette réception, appliquer les seuils conservateurs suivants : `MemAvailable_KiB` dans le diagnostic doit être supérieur ou égal à **1 048 576** ; sur chacune des quatre dernières lignes de `vmstat 1 5`, `si` et `so` doivent être nuls et `wa` inférieur ou égal à **20**. Ignorer la première ligne de mesures, qui représente une moyenne depuis le démarrage. Ces seuils sont des critères de réception, pas une garantie de performance sous toute charge.

**Critère de passage : tous les outils sont disponibles, le diagnostic est enregistré et les trois seuils sont satisfaits. Aucun réglage mémoire ou disque n’est modifié.**

## 6. Exécuter la validation technique hors ligne

**Lieu : même terminal, à la racine du dépôt.**

6.1. Créer un environnement Python réservé aux tests dans le dossier privé, puis installer les dépendances de la passerelle :

```bash
python3 -m venv .tesla-ai/intervention/venv
.tesla-ai/intervention/venv/bin/python -m pip install -r 58-Spark-MCP-Gateway/requirements.txt
.tesla-ai/intervention/venv/bin/python -m pip check
```

6.2. Exécuter les tests et conserver leur résultat :

```bash
.tesla-ai/intervention/venv/bin/python -m unittest discover -s tests -v > .tesla-ai/intervention/tests.txt 2>&1
cat .tesla-ai/intervention/tests.txt
```

Les tests simulent les appels Gemini et GitHub. Ils ne nécessitent aucune clé et n’exécutent pas le code généré.

**Critère de passage : `pip check` ne signale aucune incohérence et le compte rendu se termine par `Ran 28 tests` puis `OK`, sans échec ni erreur.**

## 7. Ouvrir et préparer les trois panneaux TERMINATOR

**Lieu de lancement : même terminal, à la racine du dépôt.**

7.1. Ouvrir la configuration indépendante fournie :

```bash
terminator --no-dbus \
  --config "$TESLA_ROOT/EXPORT/To_RENA/CODE_EDITOR/templates/terminator-headless.config" \
  --layout tesla-headless
```

7.2. Affecter les panneaux sans changer la disposition :

| Identifiant | Position | Fonction |
|---|---|---|
| **P1** | Gauche, haut | Édition du prompt et revue de la réponse |
| **P2** | Gauche, bas | Contrôles locaux et réception |
| **P3** | Droite | Appels Gemini, puis fermeture du sous-shell contenant la clé |

7.3. Dans le menu de groupement de TERMINATOR, sélectionner **« Broadcast off » / diffusion désactivée**. Vérifier qu’une frappe dans un panneau n’apparaît pas dans les autres. Ne saisir aucun secret avant ce contrôle.

7.4. Exécuter le bloc suivant séparément dans **P1, puis P2, puis P3** :

```bash
bash --noprofile --norc
set +x
unset GEMINI_API_KEY GOOGLE_API_KEY
umask 077
cd -- "$TESLA_ROOT"
test "$(pwd -P)" = "$TESLA_ROOT"
test -d .tesla-ai/intervention
```

**Critère de passage : les trois panneaux sont ouverts à la racine du dépôt, la diffusion clavier est désactivée et aucune clé Gemini n’est chargée dans leurs shells de travail.**

## 8. Préparer et approuver le prompt de réception

**Lieu : P1 — édition.**

8.1. Créer le prompt de réception, sans données privées :

```bash
nvim -u NONE -i NONE -n -- .tesla-ai/intervention/prompt.txt
```

8.2. Saisir exactement le texte suivant :

```text
Réponds uniquement par une courte checklist Markdown numérotée de cinq points.
Sujet : préparer la revue humaine d'un artefact de code avant son utilisation
manuelle dans un workflow Antigravity local.
Ne fournis aucune commande shell, aucun script et aucun appel d'outil.
Rappelle que l'artefact ne doit pas être exécuté automatiquement.
```

8.3. Enregistrer et quitter Neovim avec `Échap`, puis `:wq`, puis `Entrée`.

8.4. Lire le fichier et vérifier sa taille :

```bash
cat .tesla-ai/intervention/prompt.txt
python3 - <<'PY'
from pathlib import Path
p = Path('.tesla-ai/intervention/prompt.txt')
raw = p.read_bytes()
assert 0 < len(raw) <= 65536, 'Prompt vide ou trop volumineux'
raw.decode('utf-8')
print('Prompt UTF-8 valide :', len(raw), 'octets')
PY
```

8.5. Approuver explicitement l’envoi de **ce fichier** à Google. Ne rien y ajouter après cette approbation.

**Critère de passage : le prompt correspond au texte prévu, ne contient aucun secret et son envoi est approuvé.**

## 9. Authentifier, sélectionner le modèle et générer l’artefact

**Lieu : P3 — IA.**

9.1. Exécuter le bloc complet suivant. Les parenthèses créent un sous-shell temporaire. Le bloc s’arrête dès qu’une commande échoue et supprime ses variables de clé à sa fermeture.

```bash
(
  set -e
  set +x
  umask 077
  trap 'unset GEMINI_API_KEY GOOGLE_API_KEY' EXIT
  unset GOOGLE_API_KEY

  read -r -s -p 'Clé Gemini — saisie masquée : ' GEMINI_API_KEY
  printf '\n'
  test -n "$GEMINI_API_KEY"
  export GEMINI_API_KEY

  python3 tools/tesla_ai.py models --allow-cloud \
    > .tesla-ai/intervention/modeles.txt
  test -s .tesla-ai/intervention/modeles.txt
  cat .tesla-ai/intervention/modeles.txt

  read -r -p 'Copier un identifiant exact de la liste : ' TESLA_GEMINI_MODEL
  grep -Fxq -- "$TESLA_GEMINI_MODEL" .tesla-ai/intervention/modeles.txt

  python3 tools/tesla_ai.py generate \
    --allow-cloud \
    --model "$TESLA_GEMINI_MODEL" \
    --max-output-tokens 2048 \
    --timeout 30 \
    --retries 0 \
    --output-dir .tesla-ai/intervention \
    < .tesla-ai/intervention/prompt.txt \
    > .tesla-ai/intervention/generation.json

  cat .tesla-ai/intervention/generation.json
)
```

9.2. Saisir la clé uniquement à l’invite masquée. À la seconde invite, copier un identifiant complet affiché dans la liste ; ne pas le remplacer par un nom de modèle supposé.

9.3. Attendre le retour au shell P3. Ne lancer aucune autre commande dans le sous-shell IA et ne relancer pas automatiquement une requête en erreur. L’autorisation d’envoi ne garantit pas la gratuité ; interrompre le client n’annule pas nécessairement un traitement déjà engagé par Google.

**Critère de passage : le bloc termine avec succès et affiche un objet JSON contenant `artifact`, `"executed": false` et `"review_required": true`.**

## 10. Confirmer le retrait de la clé et contrôler l’artefact

**Lieu : P3, puis P2.**

10.1. Dans P3, confirmer que le shell parent ne contient plus de variable de clé :

```bash
test -z "${GEMINI_API_KEY+x}"
test -z "${GOOGLE_API_KEY+x}"
```

La fermeture du sous-shell retire ses variables ; elle ne révoque pas la clé Google et ne transforme pas l’environnement en coffre-fort.

10.2. Dans P2, contrôler les métadonnées, l’emplacement et les permissions :

```bash
python3 - <<'PY'
import json
import os
from pathlib import Path

folder = Path('.tesla-ai/intervention')
meta = json.loads((folder / 'generation.json').read_text(encoding='utf-8'))
assert meta['executed'] is False, 'Exécution inattendue'
assert meta['review_required'] is True, 'Revue non déclarée'
artifact = Path(meta['artifact'])
assert not artifact.is_symlink(), 'Lien symbolique refusé'
assert artifact.resolve().parent == folder.resolve(), 'Emplacement inattendu'
assert artifact.is_file(), 'Artefact absent'
assert artifact.name.startswith('review-') and artifact.suffix == '.md'
assert artifact.stat().st_uid == os.getuid(), 'Propriétaire inattendu'
assert artifact.stat().st_mode & 0o777 == 0o600, 'Permissions du fichier incorrectes'
assert folder.stat().st_mode & 0o777 == 0o700, 'Permissions du dossier incorrectes'
assert artifact.read_text(encoding='utf-8').strip(), 'Artefact vide'
print('Artefact prêt pour revue :', artifact)
PY
```

**Critère de passage : les variables de clé sont absentes de P3 et tous les contrôles de l’artefact réussissent.**

## 11. Effectuer la revue humaine

**Lieu : P1 — édition.**

11.1. Ouvrir le fichier exact désigné par les métadonnées, sans le modifier :

```bash
ARTIFACT="$(python3 -c 'import json; print(json.load(open(".tesla-ai/intervention/generation.json"))["artifact"])')"
nvim -R -u NONE -i NONE -n -- "$ARTIFACT"
```

11.2. Vérifier que la réponse contient la checklist demandée, reste pertinente pour une revue préalable à l’utilisation manuelle dans Antigravity et ne contient ni commande shell, ni script, ni instruction d’exécution automatique.

11.3. Fermer Neovim avec `Échap`, puis `:q`, puis `Entrée`.

11.4. Approuver l’artefact uniquement si les contrôles précédents sont satisfaits. Une réponse non conforme arrête la réception. Aucun texte produit par le modèle ne doit être traité comme une instruction autorisée à modifier le système.

**Critère de passage : l’artefact est approuvé par l’opérateur, sans avoir été exécuté ou appliqué au dépôt.**

## 12. Vérifier l’état du dépôt et du matériel

**Lieu : P2 — contrôle.**

12.1. Confirmer que l’intervention n’a modifié aucun fichier suivi ni ajouté de fichier visible hors du dossier ignoré :

```bash
git status --porcelain=v1 > .tesla-ai/intervention/git-apres.txt
diff -u .tesla-ai/intervention/git-avant.txt .tesla-ai/intervention/git-apres.txt
git status --short --branch
git check-ignore .tesla-ai/intervention/generation.json
```

12.2. Contrôler de nouveau les ressources et appliquer les mêmes seuils qu’à l’étape 5.3 :

```bash
python3 tools/tesla_ai.py doctor > .tesla-ai/intervention/diagnostic-apres.json
cat .tesla-ai/intervention/diagnostic-apres.json
free -h
vmstat 1 5
```

**Critère de passage : `diff` ne produit aucune différence, le dossier d’intervention reste ignoré par Git et les trois seuils de l’étape 5.3 sont satisfaits sur les nouvelles mesures. Aucun commit, push, changement de branche ou réglage système n’est effectué.**

## 13. Prononcer la réception et remettre le résultat

**Lieu : P2 — contrôle.**

13.1. Confirmer successivement les six points suivants :

1. Les trois panneaux TERMINATOR fonctionnent et leur diffusion clavier est désactivée.
2. Le diagnostic MIDGARD est enregistré et les 28 tests sont réussis.
3. L’appel Gemini réel a produit un artefact privé sans exécution automatique.
4. Les variables de clé Gemini ont été retirées du shell IA.
5. L’artefact a été relu et approuvé ; le dépôt est resté dans son état initial.
6. Le fichier approuvé est disponible pour une reprise manuelle ultérieure dans le workflow Antigravity existant ; aucun automatisme d’exécution n’a été ajouté.

13.2. Enregistrer la réception seulement après validation de ces six points :

```bash
python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path

p = Path('.tesla-ai/intervention/RECEPTION.md')
with p.open('x', encoding='utf-8') as f:
    f.write('# Réception MIDGARD — parcours Gemini dans TERMINATOR\n\n')
    f.write('Date UTC : ' + datetime.now(timezone.utc).isoformat() + '\n\n')
    f.write('Les six contrôles de réception ont été validés par l’opérateur.\n')
    f.write('Artefact relu, non exécuté, disponible pour reprise manuelle dans Antigravity.\n')
    f.write('Aucun déploiement SPARK distant ni exécution AGY certifié par cette réception.\n')
print('Réception enregistrée :', p)
PY
```

13.3. Conserver les éléments de réception dans `.tesla-ai/intervention/` : diagnostic, résultat des tests, prompt de réception, liste des modèles, métadonnées de génération, artefact approuvé et procès-verbal. Ce dossier reste local, privé et exclu de Git.

**Point d’arrivée : le parcours Gemini → artefact privé → revue humaine est réceptionné sur MIDGARD, dans TERMINATOR et sans Chrome. Le résultat est disponible pour le workflow Antigravity manuel, sans exécution automatique et sans modification de l’infrastructure SPARK existante.**
