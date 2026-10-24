# Audit du dépôt `Tesla-Antigravity-CLI` — Rapport complet

**Date :** 2026-10-24
**Périmètre :** `lordmahonheim-bot/Tesla-Antigravity-CLI`, branche `main` @ `7140b38`
**Méthode :** audit statique + reproduction locale de la CI + inspection GitHub (API `gh`). Aucun code métier nécessitant MIDGARD, une base Alexandria ou des clés API n'a été exécuté.

---

## 1. Résumé exécutif

### Verdict en une phrase

Le dépôt contient **deux modules d'ingénierie réellement solides** (53-Gouvernance exécutable et 60-Ouroboros, testés, fail-closed, CI verte) noyés dans un **monorepo-vitrine de 59 dossiers** où la documentation (29 242 lignes) dépasse le code Python (21 152 lignes), où près de la moitié des modules sont des coquilles documentaires, et où **les promesses du README ne sont pas toutes vraies** (Pyright annonce 98 erreurs, pas 0 ; il y a 59 modules numérotés, pas 60 « fully populated »).

Le risque principal n'est pas technique mais **structurel** : sans tri (produire / archiver / supprimer), chaque nouveau chantier aggrave la duplication, la dette de vérité et le coût de maintenance. La bonne nouvelle : les fondations de gouvernance pour faire ce tri proprement existent déjà dans le dépôt.

### Notes par dimension (sur 10)

| Dimension | Note | Justification courte |
|---|---:|---|
| Architecture & périmètre | **3** | 59 modules plats, doublons fonctionnels, 40 % du volume = 1 projet hors sujet (Cluedo) |
| Qualité de code (modules 53/60) | **8** | Stdlib-only, typé, testé, fail-closed, divulgation honnête des skips |
| Qualité de code (reste du repo) | **4** | 141 erreurs Ruff masquées, `print` partout, chemins absolus, forks divergents |
| Tests & CI | **6** | CI verte et sérieuse sur 2 modules ; 57 modules sans aucun filet |
| Dépendances & reproductibilité | **3** | 3 fichiers de dépendances pour ~15 bibliothèques tierces importées |
| Sécurité | **6** | Gitleaks, scrubbers, actions épinglées par SHA ; mais surface publique et alertes Dependabot coupées |
| Documentation | **4** | Volume énorme, valeur inégale : 4 README d'une ligne, liens `file://` morts, doublon strict |
| Hygiène Git / GitHub | **5** | Ruleset + PR + Dependabot OK ; description vide, 0 release, binaires sans LFS |
| Découvrabilité / produit | **2** | Aucun point d'entrée installable, GitHub classe le repo en « HTML » |

### Les 5 actions à plus fort levier

1. **Trier les 59 modules en 4 statuts** (`core`, `skill`, `experimental`, `archived`) et sortir Cluedo + Archives + OUTPUTS du repo principal.
2. **Rendre le README vrai** : corriger Pyright (98 erreurs), le compte de modules, les versions Python — puis verrouiller par la CI.
3. **Déclarer les dépendances** (un `pyproject.toml` racine ou un `requirements` par module code) pour rendre Pyright et les tests reproductibles sur clone propre.
4. **Tuer les duplications divergentes** : une seule source par SKILL (16≠48, 11≠47, 09≠47≠49), un seul `update_session_history`, un seul Alexandria canonique.
5. **Réactiver Dependabot Alerts** et ajouter les garde-fous CI manquants (shellcheck, liens morts, matrice Python).

---

## 2. Méthodologie et preuves

| Contrôle | Commande / source | Résultat |
|---|---|---|
| Inventaire fichiers | `find`, `du`, `wc -l` | 491 fichiers, 8,5 Mo (voir §3) |
| Tests module 53 | `python3 53-.../bin/test_runner.py` | ✅ PASS — 183 tests, 26 skips divulgués, 11 tests bash hooks OK |
| Tests module 60 | `python3 60-.../scripts/self_test.py` | ✅ 14/14 PASS |
| Compilation Python | `python3 -m compileall .` | ✅ 0 erreur de syntaxe |
| Lint | `ruff check .` (v0.16.8, config du repo) | ✅ vert — mais 141 erreurs masquées par `ruff.toml` (voir §5.3) |
| Typage | `pyright --outputjson` | ❌ 98 erreurs, 11 warnings, 109 fichiers (voir §5.2) |
| Secrets | grep motifs + `git ls-files` + historique Gitleaks CI | ✅ aucun secret tracké détecté |
| GitHub | `gh repo view`, `gh pr/issue/run list`, API rulesets/community | voir §5.7–5.8 |

**Limites de l'audit :** clone local *shallow* (l'historique complet a été lu via l'API GitHub, pas en local) ; Pyright exécuté sans environnement virtuel complet — les 76 `reportMissingImports` mesurent donc à la fois un vrai problème de déclaration des dépendances *et* l'absence d'installation locale ; aucun test d'intrusion ni exécution des démons (Telegram, broker, voice) ; les compteurs `grep` (timeouts subprocess, `print`) sont des heuristiques, pas une analyse AST exhaustive.

---

## 3. Cartographie quantitative

### 3.1 Volumes

| Type | Fichiers | Lignes | Commentaire |
|---|---:|---:|---|
| Markdown (`.md`) | 215 | 29 242 | **Plus de doc que de code** |
| Python (`.py`) | 111 | 21 152 | Concentré dans 53 (101 fichiers au total) et 60 (31) |
| Shell (`.sh`) | 62 | 4 028 | + scripts sans extension (06-Sudo) |
| JSON / YAML / TOML | 55 | — | Configs, schémas, evidence |
| Binaires (PDF/PNG/HTML) | 11 | — | Cluedo + carrousel LinkedIn |

**Total : 491 fichiers, 8,5 Mo.** Le seul dossier `45-Cluedo-Grands-Detectives-2023` pèse **3,4 Mo soit ~40 % du dépôt**, dont un HTML de 2,9 Mo. Conséquence visible : GitHub classe le langage principal du dépôt en **HTML (3,05 Mo)** devant Python (0,88 Mo).

### 3.2 Les 59 modules numérotés (01–60, **13 absent**)

- **9 modules ne contiennent qu'un seul fichier** (39, 42, 56, 08, 38, 43, 52, 40, 57).
- **27 modules n'ont aucun code** `.py`/`.sh` (07, 08, 09, 14, 19, 20, 21, 22, 23, 29, 31, 32, 38, 39, 40, 41, 42, 43, 45, 47, 48, 49, 51, 52, 56, 57, 59). Nuance importante : pour les modules « Skill » (47, 48, 49…), le Markdown *est* le produit — le problème n'est pas l'absence de code, c'est l'absence de **statut explicite** distinguant « skill livré », « spécification », « stub » et « abandonné ».
- **4 README font exactement 1 ligne** (08-Premortem, 38-Promotion, 43-Avalon, 52-Fix-Maintenance) ; 57 n'a même pas de `README.md`.
- **2 modules concentrent l'ingénierie testée** : 53 (101 fichiers) et 60 (31 fichiers). Le 3ᵉ plus gros, 28-Loop-Engineering (23 fichiers), contient 19 Markdown pour 1 fichier de code.

### 3.3 Hors modules : la racine et les dossiers satellites

Racine : `ABOUT_ME.md`, `MY_BRANDING.md`, `MY_COMPANY.md` (439 lignes), `PLAN-QUOTIDIEN.md` (607), `PLAN-SPARK-SCHEDULES.md` (370), `AGY-Project-MAIN-LIST.md` (84 Ko, 733 lignes), `list.txt` (copie de `ls`). Dossiers satellites : `Archives-MVP-GITHUB/` (26 fichiers, copies d'anciens modules), `EXPORT/` (26), `OUTPUTS/` (25, dont livrables LinkedIn et rapports datés), `GENESE-v1/`, `LEARN/`, `PROTOCOLES/`, `SPARK-MCP-Gateways/` (12 fichiers dont 10 scripts `test_inspect*.py` exploratoires), `tools/`, `docs/` (1 fichier).

---

## 4. Points forts — à préserver

1. **Module 53, niveau nettement au-dessus du reste.** Cœur *stdlib-only* assumé et documenté, principe « UNKNOWN != PASS » avec 26 skips divulgués au lieu d'être cachés, hooks fail-closed, anti-replay, attestations. 183 tests `unittest` + 11 tests bash, tous verts en reproduction locale.
2. **Module 60 cohérent de bout en bout** : chaîne proposer → formatter → broker → sandbox → committer, gating fail-closed vérifié par le self-test (14/14), quarantaine AST, scrubber de secrets.
3. **Hygiène secrets exemplaire** : `.gitignore` strict (bases, vecteurs, `.env`, transcripts, `runtime/`), Gitleaks en CI sur historique complet (`fetch-depth: 0`), aucun `.db`/secret tracké, scrubbers regex dans 17, 33 et 60.
4. **Supply-chain CI propre** : actions épinglées par **SHA complet** (pas par tag), `permissions: contents: read`, Dependabot hebdomadaire groupé (pip ×3 + actions), Ruff épinglé (`ruff==0.16.8`).
5. **Bonnes pratiques ponctuelles réelles** : `shell=True` = 0, `eval`/`exec` = 0, `except:` nu = 0, SQLite en `mode=rw` + WAL + clés étrangères (module 17), ID-lock sur le bot Telegram (module 37).
6. **Processus GitHub fonctionnel** : ruleset « Tesla Main Guard » actif, checks requis, 12 PR traitées (10 mergées), 14 issues Q1–Q12 toutes fermées — la boucle plan → PR → merge tourne.
7. **Fichiers communautaires présents** : LICENSE MIT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, CODEOWNERS (profil communauté GitHub : 71 %).

---

## 5. Constats détaillés

### 5.1 Architecture : un monorepo sans frontières

- **Doublons fonctionnels non tranchés** : Alexandria ×3 (02, 12, 33 + 15-Obsidian), Premortem ×2 (08 stub 1 ligne, 20), Web-Raider ×2 (04 code, 21 skill), Gouvernance ×4 (09, 27, 31, 53), GitHub ×4 (09, 10, 47, 49), MCP ×5 (37, 55, 56, 58, 59 + `SPARK-MCP-Gateways/` hors numérotation), Capability ×3 (24?, 25, 26 avec `00_canonical_sync.sh` **strictement identique** dans 25 et 26).
- **Forks de code divergents** : `search_router.py` et `indexer_hybrid.py` existent en 02 et 33 avec des contenus différents ; `update_session_history.py` fait 162 lignes en 03 et 505 lignes en 17 sous le même nom. Impossible de savoir quelle copie fait foi.
- **SKILL.md dupliqués et divergents** (diff en lignes) : Master-Code 16↔48 : 82 ; Video-Director 18↔48 : 31 ; Arcanis 11↔47 : **753** ; GitHub 09↔47 : 424 et 47↔49 : **1 174**. Chaque copie évoluera seule — c'est une machine à incohérence documentaire.
- **Périmètre pollué** : un manuel de jeu Cluedo (PDF + HTML 2,9 Mo), des livrables LinkedIn (PDF/PNG générés), des exports datés et des archives vivent dans le même repo que le code de gouvernance. `Archives-MVP-GITHUB/` duplique à l'identique d'anciens fichiers (hash MD5 identiques) alors que Git *est* l'archive.
- **Nommage incohérent** : `23-Architecture-Entr` (tronqué), `51-Conducteur-Absolu-v3.2.1` (version dans le nom de dossier), `31-Vigilum-Gateway-V2.1`, `52-Fix-Maintenance-...` (un correctif promu « module »), numéro 13 manquant sans explication, fichier `58-Tesla-Spark-MCP-Gateway.py` commençant par un chiffre (non importable comme module Python), un fichier avec espaces et accent (`La grille de rédaction d'un rapport analytique.md`).

### 5.2 Dette de vérité : le README promet plus que le repo

| Affirmation (README / badges) | Réalité mesurée |
|---|---|
| « Pyright reports 0 errors » | **98 erreurs**, 11 warnings (76 imports manquants + **22 vraies erreurs de typage** : `reportArgumentType` ×8, `reportOptionalMemberAccess` ×7…) sur 37 fichiers |
| « All 60 subprojects exist and are fully populated » | 59 dossiers (13 absent), 9 à un seul fichier, 4 README d'une ligne |
| Badge Python 3.12+ / tableau 3.10+ / CI 3.10 | Le module 55 exige **Python ≥ 3.14** et est exclu de Pyright comme de la CI |
| « Feature Highlights v3.0.0 » | **Aucun tag, aucune release** sur GitHub |
| Arborescence `MVP-GITHUB/` | Le dépôt s'appelle `Tesla-Antigravity-CLI` |
| Workflow numéroté 1,2,3,4,**6**,7… | Étape 5 manquante |

C'est le constat le plus important de l'audit : un système dont la doctrine est « NO PROOF, NO PARITY, NO PUBLISH » ne peut pas laisser sa page d'accueil contredire ses propres outils de preuve. Chaque écart est mineur ; leur accumulation détruit la crédibilité du dispositif.

### 5.3 Qualité de code : vert en surface, dette masquée en dessous

- `ruff check` passe **parce que `ruff.toml` ignore 36 règles**. En réactivant les principales : **141 erreurs**, dont **111 `BLE001`** (exceptions attrapées à l'aveugle), 12 `try/except/pass`, 6 `try/except/continue`, 2 redéfinitions, 1 `B023` (variable de boucle capturée — bug latent classique). Le choix d'ignorer peut se défendre, mais il n'est **ni justifié règle par règle, ni assorti d'un plafond** (ratchet) empêchant la dette de croître.
- **Observabilité faible** : 690 `print()` contre 6 fichiers utilisant `logging`. Pour des démons et des hooks de gouvernance, c'est un handicap de diagnostic réel.
- **Subprocess** : 73 appels `run`/`Popen`, seulement 28 occurrences de `timeout=` dans tout le code — une partie significative des exécutions peut donc pendre indéfiniment (le bot Telegram, lui, a bien un timeout de 600 s).
- **Shell inégal** : 36 scripts sur 62 seulement ont un `set -e` (tout le Capability-Bus en est dépourvu) ; aucun `shellcheck` en CI.
- **Portabilité** : 10 chemins `/home/lord-mahonheim/...` codés en dur dans le code `.py`/`.sh` (35-Voice ×3, 37-Telegram, 54-Backup, 53, 60…), et des dizaines de liens `file:///home/...` morts pour tout autre lecteur dans la documentation — alors que le README liste précisément ce défaut comme « problème résolu ».
- **Bug concret relevé** (`37-MCP-Telegram/daemon/telegram_bot_daemon.py`) : `synapse_path = "$TESLA_ROOT/memory/TELEGRAM_SYNAPSE.md"` est une chaîne Python littérale — la variable n'est jamais interpolée, l'écriture échoue ou crée un dossier `$TESLA_ROOT` parasite. S'y ajoutent un parseur `.env` maison fragile et un `urlopen` sans timeout dans `send_message`.
- Divers : 12 fichiers Python sans shebang alors que d'autres sont exécutables ; 3 scripts `.sh` trackés non exécutables (dont `lint_all.sh`, invoqué via `bash` en CI — ça passe, mais c'est fragile) ; 2 fichiers Markdown en CRLF sans `.gitattributes` pour verrouiller.

### 5.4 Tests : une forteresse et un désert

- Modules 53 + 60 : ~197 tests automatisés, CI dédiée, manifests de tests, ledgers d'evidence. C'est le standard à généraliser.
- **Les 57 autres modules n'ont aucun test automatisé** alors que plusieurs contiennent du code réel et risqué (02/33 indexation, 17 base de données, 18 vidéo, 34 Reddit, 37 Telegram, 35 voix en shell).
- `SPARK-MCP-Gateways/` contient 10 fichiers `test_*.py` qui ne sont pas des tests mais des scripts d'inspection jetables (`test_inspect.py` → `test_inspect6.py`) : ils polluent la découverte Pyright (11 erreurs à eux seuls) et tromperont tout futur `pytest` à la racine.
- Aucune mesure de couverture, aucun seuil. `01-LSP-Self-Healing/examples/test_lsp.py` est un exemple, pas un test du module 01.

### 5.5 CI : sérieuse mais étroite et partiellement figée

- **Un seul Python testé (3.10)**, alors que le badge promet 3.12+ et le module 55 exige 3.14 : aucune matrice, le module 55 n'est jamais testé en CI.
- Le job `gate-r-reconcile` rejoue la réconciliation sur **un ledger figé daté du 2026-09-24** (nom de fichier en dur dans le YAML) : il prouve que l'outil sait relire une vieille preuve, pas que le code courant produit une preuve valide.
- `mirror-guard.yml` **échoue systématiquement** dès qu'une PR touche `LEARN/`, `PROTOCOLES/` ou `AGY-Project-MAIN-LIST.md` — y compris pour une correction légitime du propriétaire. Un garde qui bloque tout finit contourné ou désactivé ; un diff/label d'approbation serait plus durable.
- Le dossier `evidence/` du module 53 accumule un JSON par exécution (18 fichiers visibles) : sans politique de rétention, le repo grossit à chaque run commité.
- Manquent : shellcheck, vérification des liens Markdown, lint Markdown, cache pip, `concurrency` (annulation des runs obsolètes), timeouts de jobs.
- Historique : la CI a été rouge sur les branches Dependabot avant d'être verte sur `main` — vérifier que le vert actuel vient d'un correctif et non d'un contournement.
- Les hooks locaux (`.githooks` fail-closed, bonne idée) ne sont actifs que si `core.hooksPath` est configuré : ce prérequis doit être documenté et/ou automatisé (`tools/install_hooks.sh` existe mais n'est pas mis en avant dans le README).

### 5.6 Dépendances : le maillon faible de la reproductibilité

- **3 fichiers de dépendances pour tout le dépôt** : `53/requirements.txt` (`pynacl>=1.6.2`, exemplairement commenté), `37/.../requirements.txt` (`mcp` **sans aucune borne de version**), `55/pyproject.toml` (description restée « Add your description here »).
- Pourtant le code importe : `chromadb`, `mcp`, `google.genai`, `starlette`, `uvicorn`, `reportlab`, `playwright`, `numpy`, `Pillow`, `requests`, `python-dotenv`, `frontmatter`… Aucun module 02, 15, 17, 18, 33, 34, 44, 58 ne peut être installé proprement par un tiers. **C'est la cause directe des 76 `reportMissingImports` Pyright** et de l'impossibilité de tenir la promesse « 0 erreur ».
- Pas de `pyproject.toml` racine, pas de lockfile global, pas d'environnement de dev reproductible (`uv.lock` existe uniquement pour le module 55).
- **Dependabot Alerts est désactivé** alors que Dependabot Updates fonctionne : les CVE des dépendances ne remonteront pas (à réactiver dans Settings → Security, avec secret scanning / push protection si disponibles, et envisager CodeQL).

### 5.7 Sécurité & vie privée : bon socle, surface à réduire

Points forts déjà cités (§4). Points de vigilance :

- **Dépôt public riche en informations personnelles et opérationnelles** : nom civil complet dans `AGY-Project-MAIN-LIST.md`, chemins domestiques détaillés, architecture interne (MIDGARD, vaults, synapses), plans quotidiens, branding et stratégie d'entreprise (`MY_COMPANY.md`, `ABOUT_ME.md`, `PLAN-QUOTIDIEN.md`). Même sans secret technique, c'est une surface d'ingénierie sociale. À déplacer en dépôt privé ou à expurger.
- **Le démon Telegram est, par conception, une exécution de code à distance** : tout message de l'ID autorisé est passé à `agy -p`. L'ID-lock est présent (bien), mais il n'y a ni sandbox, ni journal d'audit signé, ni liste blanche de commandes, ni confirmation pour les actions destructrices. À traiter comme un composant critique : le documenter comme tel, le confiner (utilisateur dédié, comme déjà recommandé pour le broker Ed25519 du module 53).
- **Gouvernance contournable côté serveur** : `required_approving_review_count: 0` et `enforce_admins: false` (cf. `docs/BRANCH_PROTECTION.md`) — les hooks locaux fail-closed peuvent être sautés (`--no-verify`) sans qu'une revue ne compense. Pour un repo solo c'est un choix défendable, mais il doit être assumé et écrit.
- `SECURITY.md` renvoie à « l'e-mail du profil corporate » sans le nommer : inutilisable par un rapporteur externe. Ajouter un canal concret (GitHub Private Vulnerability Reporting) et un délai de réponse visé.
- Les scrubbers regex maison (17, 33, 60) sont utiles mais ne remplacent pas Gitleaks en pre-commit local ; leurs motifs divergent d'un module à l'autre (encore la duplication).

### 5.8 Documentation & GitHub : beaucoup de texte, peu de navigation

- 29 242 lignes de Markdown, dont des SKILL de 900–1 000 lignes et un doublon **strictement identique** (`PROTOCOLES/GRAVURE-SUR-MARBRE.md` = `PROTOCOLE_CANONIQUE_...md`, 534 lignes chacun).
- `AGY-Project-MAIN-LIST.md` (733 lignes) fait office de registre mais ses liens pointent vers `file:///home/...` : mort pour tout lecteur GitHub. Aucun tableau de bord généré (module → statut → code → tests → dernière preuve).
- GitHub : **description vide, aucun topic, pas de homepage, Wiki activé** (surface documentaire concurrente du repo — à désactiver si inutilisé), 0 étoile/0 fork, profil communauté à 71 % (manquent : templates d'issues/PR).
- Fichiers marqueurs trackés sans valeur : `EXPORT/.keep`, `.keep2`, `.test-push-main`, `.trigger_mirror`, `list.txt` (régénérable par `ls`).
- Binaires trackés sans Git LFS ni `.gitattributes` : chaque régénération du carrousel ou du manuel alourdit l'historique pour toujours.

---

## 6. Axes d'amélioration priorisés

> Priorités : **P0** = vérité/sécurité, à faire avant tout nouveau chantier · **P1** = structure, sous 2 semaines · **P2** = industrialisation · **P3** = confort/produit. Effort : S < ½ j, M = 1–3 j, L > 3 j.

| # | Axe | Prio | Effort | Impact |
|---:|---|:---:|---|---|
| 1 | **Vérité du README + verrouillage CI** : corriger compte de modules, versions, promesse Pyright ; ajouter Pyright en CI (mode rapport puis bloquant après résorption) | P0 | S/M | Restaure la crédibilité de toute la gouvernance |
| 2 | **Réactiver Dependabot Alerts** (+ secret scanning/push protection, CodeQL) et rendre `SECURITY.md` actionnable | P0 | S | Ferme l'angle mort CVE/secrets |
| 3 | **Sortir le personnel et le hors-sujet** : `MY_*`, `ABOUT_ME`, `PLAN-*`, Cluedo, livrables LinkedIn → dépôt privé ou releases ; corriger le bug `$TESLA_ROOT` du bot Telegram au passage | P0 | S | −50 % de volume, surface OSINT réduite, langage GitHub redevenu « Python » |
| 4 | **Triage des 59 modules** avec statut explicite dans chaque README (`core/skill/experimental/archived`) + tableau de bord généré ; archiver les stubs dans `archives/` ou les supprimer (Git conserve l'historique) | P1 | M | Rend le repo navigable ; stoppe l'entropie |
| 5 | **Source unique par artefact** : dédupliquer SKILL (génération ou liens symboliques depuis un dossier `skills/` canonique), fusionner 02/33, 03/17, 25/26, supprimer `Archives-MVP-GITHUB/` et le doublon `PROTOCOLES/` | P1 | M/L | Élimine les divergences silencieuses |
| 6 | **Dépendances déclarées et épinglées** : `pyproject.toml` racine (outillage dev : ruff, pyright) + `requirements`/module pour chaque module à code ; borner `mcp` ; nettoyer `SPARK-MCP-Gateways/test_inspect*` | P1 | M | Clone propre reproductible ; Pyright passe sous les 25 vraies erreurs |
| 7 | **Résorber la dette Ruff par cliquet** : justifier chaque ignore ou le retirer par vagues (BLE001 d'abord dans 53/60), interdire toute *nouvelle* occurrence via `--statistics` plafond en CI ; `logging` à la place de `print` dans démons/hooks ; timeouts subprocess systématiques | P2 | L | Qualité réelle au lieu de vert cosmétique |
| 8 | **Élargir tests & CI** : matrice Python 3.10/3.12 (+ job séparé 3.14 pour le module 55), tests de fumée pour 02/17/34/37, shellcheck, lien mort Markdown, cache + `concurrency`, `gate-r-reconcile` sur ledger **produit par le run courant**, rétention `evidence/` | P2 | M/L | Le filet couvre enfin le code à risque |
| 9 | **Hygiène Git** : `.gitattributes` (`* text=auto eol=lf`, binaires, `linguist-generated` pour `evidence/` et livrables), `.editorconfig`, Git LFS ou suppression des binaires régénérables, renommages (`23-Architecture-Entr`, fichier accentué), purger marqueurs/`list.txt` | P2 | S | Fins des diffs parasites et de l'historique obèse |
| 10 | **Produit & découvrabilité** : description + topics GitHub, templates issues/PR, `CHANGELOG.md` + première release taguée `v3.0.0` (ou retirer la mention), README recentré « installer en 5 minutes » pour les 3 modules cœur, désactiver le Wiki si inutilisé | P3 | S/M | Transforme la vitrine en projet adoptable |

---

## 7. Feuille de route proposée

### Horizon 1 — « Vérité » (1 journée, que des quick wins)

- [ ] Corriger README : 59 modules, versions Python unifiées, retirer/qualifier « 0 erreur Pyright » et « fully populated », renommer `MVP-GITHUB/` → `Tesla-Antigravity-CLI/`, rétablir l'étape 5.
- [ ] Réactiver Dependabot Alerts ; compléter `SECURITY.md` (canal GitHub PVR).
- [ ] Corriger le bug `$TESLA_ROOT` littéral (module 37) + timeout manquant.
- [ ] Supprimer : doublon `PROTOCOLES/`, `list.txt`, marqueurs `EXPORT/.keep*`, `SPARK-MCP-Gateways/test_inspect2..6.py` (ou les renommer hors `test_`).
- [ ] Ajouter `.gitattributes` + `.editorconfig` ; description et topics GitHub.

### Horizon 2 — « Structure » (1–2 semaines)

- [ ] Statuer chaque module (`core/skill/experimental/archived`) ; déplacer Cluedo, Archives, OUTPUTS datés et fichiers personnels hors du repo (dépôt privé / releases).
- [ ] Canonique unique : `skills/` pour les SKILL.md, fusion Alexandria (33 absorbe 02), fusion `update_session_history` (17 absorbe 03), fusion 25/26.
- [ ] `pyproject.toml` racine + dépendances par module ; Pyright en CI non bloquant avec plafond d'erreurs décroissant.
- [ ] Remplacer les `/home/lord-mahonheim` du code par `Path.home()` / variables d'environnement ; script de contrôle en CI (`grep` bloquant) pour empêcher la régression.

### Horizon 3 — « Industrialisation » (1–2 mois, par vagues)

- [ ] Matrice CI Python + shellcheck + liens morts ; `gate-r-reconcile` sur preuve fraîche ; politique de rétention `evidence/` (artefacts CI plutôt que fichiers commités).
- [ ] Dette Ruff : vagues par règle avec cliquet ; `logging` structuré pour démons/hooks ; timeouts subprocess audités par AST (`ast_quarantine` du module 60 peut servir de base !).
- [ ] Tests de fumée/intégration pour 02, 17, 34, 37 ; couverture mesurée sur 53/60 avec seuil.
- [ ] Premier `CHANGELOG` + release GitHub taguée ; tableau de bord auto-généré remplaçant `AGY-Project-MAIN-LIST.md` comme registre public (liens relatifs).

---

## 8. Conclusion

Ce dépôt n'a pas un problème de talent d'ingénierie — les modules 53 et 60 prouvent le contraire, avec un niveau de rigueur (fail-closed, preuve, divulgation des inconnues) rare dans un projet personnel. Il a un problème d'**accumulation sans tri** : 59 chantiers cohabitent sans statut, la documentation prolifère plus vite que le code vérifié, et la vitrine (README) a pris de l'avance sur la réalité mesurable.

Les axes ci-dessus ramènent le système à sa propre doctrine : *pas de preuve, pas de parité, pas de publication*. Appliquer l'horizon 1 suffit à rendre le dépôt honnête ; l'horizon 2 le rend navigable ; l'horizon 3 le rend durable. Le meilleur prochain chantier n'est donc pas un 61ᵉ module — c'est le tri des 59 existants.

---

### Annexe — Commandes de reproduction

```bash
python3 53-Vigilum-Codex-2.0-Executable-Governance/bin/test_runner.py   # 183 tests PASS
python3 60-WikiSkill-Ouroboros/scripts/self_test.py                      # 14/14 PASS
python3 -m compileall .                                                  # 0 erreur
ruff check .                                                             # vert (config repo)
ruff check . --select BLE001,F401,F811,F841,S110,S112,TRY002,B023,G201 --statistics  # 141 masquées
pyright --outputjson                                                     # 98 erreurs / 109 fichiers
gh repo view --json description,stargazerCount,primaryLanguage,languages
```
