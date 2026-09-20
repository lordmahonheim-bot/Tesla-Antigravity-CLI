# Audit et corrections — Gemini / MIDGARD / Tesla / Antigravity

**Date : 19 septembre 2026**
**Décision : parcours terminal corrigé et testé hors ligne ; validation sur MIDGARD requise.**

## Résumé

Le dossier CODE_EDITOR contenait des propositions contradictoires : recours à
Chrome malgré le parcours headless, clés durables dans `.bashrc`, bridge qui
exécutait du code généré avant revue, commandes AGY non démontrées et réglages
mémoire prescrits sans mesures. Les mentions « certifié », « Fail-Safe » et
« sans risque de régression » ne constituaient pas des preuves reproductibles.

Le parcours de référence est maintenant :

**TERMINATOR → prompt relu → API Gemini → artefact privé → revue humaine →
changements ciblés et tests → éventuelle orchestration AGY manuelle.**

Le client Python ne lance aucun programme, ne parcourt pas le dépôt, n'ouvre
aucun navigateur et ne modifie aucun réglage système. SPARK reste un composant
séparé en lecture seule. Aucun Chrome n'a été utilisé pour cet audit.

## Périmètre et preuves disponibles

- Les **19 documents initiaux** de `EXPORT/To_RENA/CODE_EDITOR` ont été inventoriés
  et leurs instructions pertinentes examinées ; deux documents sont remplacés,
  les 17 autres explicitement marqués comme archives pour le parcours sans Chrome.
- Passerelle Python `58-Spark-MCP-Gateway`, documentation et dépendances corrigées.
- Consultation du contexte `54-Integration-Antigravity-Google-Agents-MIDGARD`
  et des outils locaux ; pas de modification de scripts privilégiés système.
- Références Google consultées par récupération HTTP de documentation, sans navigateur.
- Environnement de validation : sandbox Linux, Python **3.11.2**, environ 4 Go
  de RAM visibles ; **ce n'est pas MIDGARD**. TERMINATOR, AGY et RTK absents.
- Aucune clé Gemini disponible : aucun prompt envoyé à Gemini, aucune dépense
  d'API, aucune connexion à la passerelle SPARK de production.

## Constats et corrections

| Gravité | Constat initial | Correction / limite restante |
|---|---|---|
| Critique | Le prototype `NOEUD4_MasterCode_Bridge_Terminator` écrivait dans un `/tmp` fixe et exécutait directement la réponse via `antigravity run`. | Prototype retiré ; client effectif `tools/tesla_ai.py`, fichiers privés uniques `.md`, zéro exécution et zéro application automatique. |
| Haute | « Sandbox AGY » et syntaxe `agy run` / `antigravity run` non prouvées dans le dépôt. | Aucun connecteur d'exécution supposé. Vérification du binaire, aide/version et isolation réelle obligatoire sur MIDGARD. |
| Haute | Clé Gemini ajoutée en clair à `.bashrc`, héritée par tous les processus. | Saisie masquée dans un sous-shell IA seulement, `set +x`, suppression à la fin ; clé uniquement en en-tête HTTPS. Pas de secret stocké par le client. |
| Haute | Une configuration SPARK publique pouvait fonctionner avec un jeton vide. | Refus de démarrage par défaut sans jeton ; exception explicite strictement locale, interdite avec tunnel configuré ou bind distant. Proxies externes inconnus non détectables : exception à proscrire derrière eux. |
| Haute | Import `MCPServer` et `streamable_http_app(transport_security=...)` incompatibles avec le SDK 1.x testé. | `FastMCP`, sécurité configurée au constructeur, app sans argument ; dépendances directes fixées et handshake réellement testé. |
| Haute | `github_read_file` appelait `.get()` avant de reconnaître une liste de répertoire. | Test du type en premier ; test de régression, refus explicite des contenus binaires et formats non pris en charge. |
| Moyenne | Modèles anciens figés (`gemini-pro`, `gemini-1.5-pro`), ancien SDK, absence de preuve de disponibilité. | REST documenté, découverte paginée `models`, identifiant choisi explicitement ; aucun fallback silencieux vers un autre modèle. |
| Moyenne | Énoncé temporel « depuis fin 2026 » dans un document du 19 septembre ; politique des clés traitée comme acquise. | Ancienne étude archivée ; guide référencé à la migration annoncée par Google, type de clé à vérifier dans le projet réel. |
| Haute | Pas de consentement d'envoi distinct, de contrôle de taille ni de traitement clair des quotas/erreurs. | `--allow-cloud` requis ; prompt ≤ 64 Kio, réponse ≤ 2 Mio, timeout configurable, retries optionnels bornés 429/503, erreurs assainies. |
| Haute | Montage `/tmp` à chaud, modifications `fstab`, swappiness fixe présentés comme protections universelles. | Retirés du guide actif ; diagnostic en lecture seule, mesures mémoire/swap/I/O avant toute optimisation ZRAM. Aucun `sudo`, `mount` ou `sysctl` exécuté. |
| Moyenne | URLs GitHub construites depuis des chemins non validés ; erreurs réseau/contenus non bornés. | Validation et encodage des chemins, délai, plafond 2 Mio, refus de redirection et erreurs contrôlées. |
| Moyenne | Faible séparation entre service MCP distant, IA facturable et exécution locale. | Aucun outil Gemini/shell ajouté à SPARK. Clés séparées, génération locale autorisée au cas par cas, interface manuelle avec AGY. |
| Moyenne | Workflow Git imposant checkout/pull/changement de branche et promesses absolues. | Revue sur branche courante ; aucune mutation Git automatique ; archives signalées, résultats de test distincts des affirmations historiques. |

## Livrables

- [`tools/tesla_ai.py`](../../../tools/tesla_ai.py) : commandes `doctor`, `models`,
  `generate` ; bibliothèque standard Python 3.10+.
- [Guide opératoire TERMINATOR](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md) :
  authentification éphémère, revue, Git, contrôles MIDGARD et passage manuel à AGY.
- [Configuration trois panneaux](templates/terminator-headless.config) indépendante,
  scrollback borné, sans lancement automatique d'agent ni écrasement des préférences.
- [Passerelle SPARK corrigée](../../../58-Spark-MCP-Gateway/README.md), transport
  stateless, authentification stricte, trois outils en lecture seule.
- Tests Python et workflow CI dédié, permissions GitHub Actions en lecture seule.
- `.tesla-ai/` exclu de Git pour garder prompts et réponses hors versionnement.

## Vérification exécutée

Commandes depuis la racine du dépôt :

```bash
python3 -m unittest discover -s tests -p test_tesla_ai.py -v
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
python3 tools/tesla_ai.py doctor
git diff --check
```

**Résultats locaux : 28 tests réussis (17 client, 11 passerelle).**
`pip check` : aucune incohérence détectée. `git diff --check` : aucune erreur.

Couverture utile :

- consentement avant réseau ; diagnostic hors ligne ; clés absentes des URLs ;
- modèle/chemin injecté refusé ; pagination bornée ; parsing et tailles bornés ;
- réponses vides, tronquées, bloquées et appels d'outils refusés ;
- timeout/erreurs expurgées, 429 avec retry borné, `Retry-After` long non ignoré ;
- génération vers artefact 0600, dossier 0700, noms uniques, lien symbolique refusé ;
- prompt vide, trop long, non UTF-8 ou contenant la clé active rejeté avant réseau ;
- démarrage SPARK fail-closed, exception loopback limitée, hostname exact ;
- handshake MCP, liste d'outils et appel du statut en ASGI local ;
- 401 sans bon jeton, 421 hôte hostile, 403 origine hostile, 404 sur `/mcp/sse` ;
- erreurs GitHub, redirection, contenu trop grand, binaire et répertoire-vers-fichier.

Les requêtes GitHub/Gemini des tests sont **simulées** ; le handshake MCP est
réel dans le processus de test, pas à travers votre réseau de production.

Mesure indicative unique du **diagnostic seulement**, dans cette sandbox :
**0,063 s, pic RSS 19 504 Kio**, relevé via `time.monotonic()` et
`resource.getrusage(RUSAGE_CHILDREN)`. Ce n'est ni un benchmark de génération,
ni une mesure TERMINATOR/AGY/MIDGARD, ni une garantie de budget RAM total.
La réduction attendue provient surtout de l'absence de navigateur, modèle local,
indexation et tâches concurrentes dans ce client.

La CI ajoutée prévoit Python 3.10 et 3.12 ; elle n'a pas encore été exécutée sur
GitHub dans cette session. Dépendances transitives non verrouillées, tests à
rejouer après toute mise à jour.

## Risques restants / réception sur MIDGARD

- [ ] Lancer `doctor` sur MIDGARD et confirmer matériel, RAM disponible, stockage,
  swap/ZRAM, versions Python, TERMINATOR, éditeur et AGY.
- [ ] Ouvrir la configuration TERMINATOR ; confirmer trois panneaux et diffusion
  clavier désactivée. Aucune session graphique n'a été testée ici.
- [ ] Vérifier type de clé Gemini, autorisations, restrictions, région, quotas,
  facturation et conditions de traitement des données avec la documentation actuelle.
- [ ] Depuis le sous-shell IA, lister les modèles puis envoyer un prompt synthétique
  non confidentiel avec `--allow-cloud` ; confirmer que seul un artefact est créé.
- [ ] Fermer le sous-shell contenant la clé avant tests/exécution de code local.
- [ ] Identifier AGY, vérifier les commandes réellement disponibles et l'isolation,
  puis réaliser une tâche non destructive sous validation humaine.
- [ ] Si SPARK est nécessaire, configurer un jeton aléatoire, les droits GitHub
  en lecture seule et le hostname précis ; tester rejet sans jeton et appel du
  statut via le client réel. Ne pas déduire le succès de l'ancien rapport.
- [ ] Mesurer mémoire/latence/I/O sous charge représentative avant de régler ZRAM
  ou le swap ; conserver une procédure de retour arrière spécifique à la machine.

Un artefact reste du contenu non fiable ; un fichier non exécutable peut toujours
être exécuté explicitement avec un interpréteur. Le client ne détecte pas tous
les secrets du prompt, ne protège pas contre un autre processus du même compte
et ne constitue pas une sandbox. Le parent du dossier de sortie doit être sûr.
Une requête interrompue peut avoir été traitée/facturée par le fournisseur.

Le système complet Tesla/Alexandria/RTK et les autres passerelles (dont Calibre)
ne sont pas certifiés par cet audit. Le même import `MCPServer` apparaît dans
Calibre : sa migration nécessite une validation dédiée, hors correctif ici.
Aucun tunnel, configuration privée, keyring ni service MIDGARD n'a été modifié.

## Sources primaires

Consultées le 2026-09-19, sans Chrome :

- [Google — clés API, restrictions et migration](https://ai.google.dev/gemini-api/docs/api-key)
- [Google — découverte des modèles et capacités](https://ai.google.dev/api/models)
- [Google — contrat REST generateContent](https://ai.google.dev/api/generate-content)
- [MCP Python SDK officiel](https://github.com/modelcontextprotocol/python-sdk)
  et signatures du paquet `mcp==1.30.0` inspectées localement.

**Conclusion :** base technique corrigée, minimale et vérifiable ; pas de
certification de production tant que les contrôles MIDGARD/Google/AGY/SPARK
ci-dessus n'ont pas été exécutés dans l'environnement réel.
