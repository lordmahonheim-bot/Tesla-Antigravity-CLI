---
title: "Cartographie Intégrale des Apprentissages & Doctrines Canoniques"
date: 2026-08-24
status: "Sanctuarisé"
version: "2.0.0"
---

![Status](https://img.shields.io/badge/Status-CANONICAL-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red)

# Synthèse Globale du Vigilum Codex

*(Note : Les artéfacts d'apprentissage historiques ont été purgés vers les archives mémorielles pour garantir l'Anti-Semantic Bloat).*

## PILIERS CANONIQUES DU VIGILUM CODEX

### I. Gouvernance & Orchestration (La Doctrine du Conducteur)

* **[VC-GOV-01] Délégation Absolue (Anti-Réinvention)**: L'Agent Principal (AGENTS) orchestre, mais ne réimplémente jamais. Face à un besoin spécialisé, il a l'obligation stricte d'invoquer (`invoke_subagent`) un agent d'élite dédié à cette tâche.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Traces de l'appel `invoke_subagent` dans les logs, corrélées avec la réussite de la délégation.
* **[VC-GOV-02] Anti-Usurpation (Lock des Slash Commands)**: L'invocation d'un Skill contextuel par l'utilisateur ne donne jamais le droit à l'Orchestrateur de s'approprier l'identité de ce Skill. L'Orchestrateur doit transférer la mission au sous-agent correspondant.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: BEHAVIORAL_CHECK`
  > Absence de modification directe par l'Orchestrateur sur les fichiers ciblés par le sous-agent.
* **[VC-GOV-03] Le Conducteur Absolu v3.2.1 (7 Gates & Fail-Closed)**: Toute opération est soumise à ce framework séquentiel. La règle Zéro s'applique : *No Proof, No Pass* (Fail-Closed). L'agent n'extrapole jamais un succès sans preuve physique. Toute ambiguïté contextuelle ou manque de preuve physique entraîne un arrêt total immédiat (Halt & Catch Fire). *Unknown ≠ Pass.*
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Validation séquentielle des 7 Gates par un outil d'audit externe ou preuve documentaire formelle.
* **[VC-GOV-04] Déploiement Team-Synergy (Anti-Amputation)**: Lorsqu'un Graphe de Mission (DAG) est créé, il est interdit d'omettre un agent d'élite. Arcanis, Curator, Web-Raider, Master-Code, Premortem et Github-Manager doivent obligatoirement posséder un nœud opérationnel.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Présence des nœuds requis dans le DAG de mission (Graphe).
* **[VC-GOV-05] Pré-validation Canonique du Séquencement**: L'autonomie de bout en bout est interdite tant que le Graphe de Mission (DAG) n'a pas été présenté et explicitement validé par Lord Mahonheim.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Trace textuelle d'approbation utilisateur explicite avant lancement autonome.
* **[VC-GOV-06] Équilibre Auditif (Anti-Zèle)**: Lors de l'audit d'un plan, l'Agent a l'interdiction d'adopter une posture hyper-critique artificielle. Si un artefact est valide, il doit être approuvé factuellement, sans inventer de faux défauts.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: OBSERVATION`
  > Validation objective sans blocage artificiel.
* **[VC-GOV-07] Utilisation Contextuelle de Github-Manager**: Si la mission concerne GitHub, l'emploi de `tesla-github-manager` est impératif. Si la mission ne concerne ni de près ni de loin GitHub (ex: écrasement ou copie de fichier local pur), l'agent `tesla-github-manager` n'a aucun intérêt à être utilisé et doit être exclu du Mission Graph pour éviter le gaspillage de ressources.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Absence de `tesla-github-manager` dans le Graphe de Mission pour les opérations strictement locales.

### II. Rigueur Opérationnelle & Traitement des Données

* **[VC-OPS-01] Doctrine Low-Code**: Avant d'écrire le moindre script Python ou Bash, l'Agent doit vérifier si la tâche peut être accomplie via des outils système natifs (No-Code/Low-Code) ou des automatisations existantes.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: BEHAVIORAL_CHECK`
  > Utilisation privilégiée de commandes natives avant création de nouveaux scripts.
* **[VC-OPS-02] Déterminisme de Lecture Stratégique**: Interdiction formelle de recourir à la commande `cat` pour lire un fichier massif (Économie Cognitive). L'Agent doit utiliser des outils déterministes et chirurgicaux (`rg`, `jq`, `Tree-sitter`). Si la lecture d'un fichier est tronquée par l'API, l'Agent a l'interdiction de deviner la suite (Anti-Extrapolation). Il doit impérativement relancer la lecture avec un décalage (Offset) ou utiliser `tail`.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Utilisation de `rg`, `jq`, `tail` ou `ContentOffset` dans les outils API.
* **[VC-OPS-03] Actionnabilité / Anti-Distillation**: Un document agentique est un compilateur de comportement, pas un mémo synthétique. La concision ne doit jamais corrompre les détails opérationnels. Ne jamais résumer une faille par "optimiser".
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Présence de directives explicites et concrètes dans les documents finaux, absence de termes-valises.
* **[VC-OPS-04] Zéro Intervention Manuelle (Background Ops)**: Lorsqu'une tâche de surveillance est lancée, l'Agent ne doit jamais demander à l'humain d'exécuter la commande dans son terminal. L'Agent doit la configurer en tâche de fond 100% autonome (ex: `systemd` ou process asynchrone).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Processus autonome identifié (service systemd, tâche de fond).
* **[VC-OPS-05] Doctrine de Complétion Stricte (/goal)**: En mode autonome, il est interdit de déclarer une mission accomplie à 100% si un seul élément reste bloqué ou en attente (même pour cause réseau).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Absence de points bloquants ou tâches en suspens avant déclaration de succès.

### III. Sécurité & Failsafes

* **[VC-SEC-01] Anti-Vaporisation Git (Circuit Breaker)**: Avant toute altération de branche (`checkout`, `push`), l'Agent a l'obligation mécanique d'exécuter `git status`. S'il y a des modifications non commitées, l'action est immédiatement stoppée pour prévenir la destruction du travail non sauvegardé.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Exécution préalable de `git status` avant toute altération de branche.
* **[VC-SEC-02] Self-Healing LSP (Auditeur Niveau 1)**: Tout code généré doit impérativement être validé par `karellen-lsp-mcp`. Si une erreur est détectée, l'Agent entre dans une boucle de correction autonome avant de présenter le résultat.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Validation LSP réussie (zéro erreur bloquante) avant présentation du code.
* **[VC-SEC-03] Loi de Parité Absolue & Audit Anti-Fantôme**: Un protocole déterministe d'audit fichier-par-fichier (Anti-Amnésie et Anti-Fantôme) qui garantit l'alignement parfait entre l'état de l'Exécution (fichiers de config) et l'état de la Mémoire (`SESSION_LOG`, `PROJECT_STATE`). L'alignement entre Mémoire et Exécution doit être vérifiable par script.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Audit bidirectionnel de parité validé (Exit 0).
* **[VC-SEC-04] Nœud PREMORTEM Systématique**: Lors de la construction d'un DAG, le dernier nœud avant validation doit obligatoirement être attribué à l'agent `premortem` pour stress-tester le plan et trouver ses points de rupture.
  > **[EVIDENCE_CHAIN]**: `jq '.nodes[-1].agent' DAG.json | grep "premortem"`

### IV. Rituels Continus & Conscience Mémorielle

* **[VC-MEM-01] Veille Proactive (Highlights)**: `[SUPERSEDED]` L'obligation d'une recherche OSINT mondiale à chaque ouverture de session a été remplacée au profit d'un déclenchement strictement contextuel, pour éviter la surcharge cognitive et préserver l'économie de tokens.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: BEHAVIORAL_CHECK`
  > Déclenchement de la veille uniquement sur requête explicite ou contexte nécessitant un apport d'information externe récent.
* **[VC-MEM-02] Continuité Synaptique (Telegram)**: À l'ouverture de la session, l'Agent vérifie furtivement l'existence d'un fichier `TELEGRAM_SYNAPSE.md` afin de lier le contexte du chat mobile à la session de bureau en cours.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: BEHAVIORAL_CHECK`
  > Vérification furtive du fichier Synapse à l'ouverture de session.
* **[VC-MEM-03] Rituel d'Alexandria (Biological Gate)**: L'Agent a l'autonomie d'analyser les notes brutes dans `00-Inbox/`, mais il doit se stopper net (Gate) et demander l'autorisation humaine formelle avant de les promouvoir dans la base permanente `10-Alexandria/`.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Autorisation explicite de l'utilisateur avant promotion dans Alexandria.
* **[VC-MEM-04] Archivage Obligatoire des Artefacts**: Aucune architecture complexe ou analyse ne doit s'évaporer dans l'historique du chat. Tout travail d'élite doit aboutir à la gravure d'un document physique dans `OUTPUTS/`.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Présence d'un document physique dans `OUTPUTS/` attestant du travail complexe.
* **[VC-MEM-05] Persistance des Open-Items**: Toute tâche en suspens, arbitrage reporté ou incertitude doit être physiquement écrit dans le fichier `open_items_todo-Updated.md` et ne jamais rester à l'état de "post-it verbal".
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Les tâches en suspens sont gravées dans le fichier de suivi.
* **[VC-MEM-06] Sanctuaire d'Acquisition Cognitive (/LEARN)**: Le répertoire `/memory/LEARN/` est érigé en sous-domaine canonique. Toute exécution d'un `/Learn` DOIT utiliser `write_to_file` pour s'échapper du silo `brain/` et s'ancrer dans ce chemin absolu. Le sanctuaire intègre une architecture de relégation (`ARCHIVES/`) pour prévenir le Semantic Bloat.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Traçabilité stricte de l'appel `write_to_file` ciblant `/memory/LEARN/` (et non `brain/`).

### V. Cycle de Vie MVP & Processus de Publication

* **[VC-PUB-01] Le Sanctuaire des Protocoles**: Le dossier `memory/PROTOCOLES/` constitue le registre canonique des protocoles opérationnels. L'applicabilité et les préconditions du protocole (version, dépendances, état) doivent être vérifiées avant exécution.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Vérification de la version du protocole, des dépendances et du statut (`DEPRECATED`, `CANONICAL`) avant exécution.
* **[VC-PUB-02] La Gravure sur Marbre**: Protocole exécuté à la clôture de tout chantier. Ce mécanisme complexe d'exécution est régi en totalité par sa source canonique.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: PROCEDURAL_CHECK`
  > Application stricte de `memory/PROTOCOLES/GRAVURE-SUR-MARBRE.md` (Phases 0 à 7 + Phase 3.5 Parité).
* **[VC-PUB-03] Signature Visuelle Obligatoire**: L'en-tête de tout MVP ou livrable final doit obligatoirement comporter le ruban de badges `shields.io` attestant de son statut (Status, Ecosystem, Security, Python).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Présence physique du ruban de badges dans l'en-tête du document.
* **[VC-PUB-04] Ségrégation Linguistique (English Strict)**: Les dépôts publics et le dossier `MVP-GITHUB/` exigent l'Anglais de manière inconditionnelle (Readme, Commits, Code).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Vérification linguistique de la vitrine publique.
* **[VC-PUB-05] L'Exception des Protocoles**: Seule dérogation à la Règle de Ségrégation Linguistique : Un protocole canonique, n'étant pas un MVP, échappe à la traduction et se propage tel quel, dans sa langue native.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Intégrité parfaite (copie sans traduction) des protocoles propagés.
* **[VC-PUB-06] Décorrélation Taxonomique**: Séparation physique entre l'identité interne (SGC) et externe. Le numéro d'un MVP se détermine par l'audit du répertoire externe (`ls -1 | sort -n`), sans calquage aveugle sur le numéro du chantier.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Indépendance des IDs SGC et GitHub.
* **[VC-PUB-07] Doctrine de Double Copie / Double Push**: Lors de la propagation publique, l'Agent ne doit pas se fier à une automatisation magique. Il copie physiquement les fichiers cibles vers `MVP-GITHUB/`, valide sur le dépôt local, puis effectue un commit distinct sur le dépôt d'export avant de demander la permission du push.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: TRACE`
  > Preuve de copie manuelle et de commit/push validé sur le dépôt public.

### VI. Méta-Cognition & Déterminisme

* **[VC-META-01] Identifiants Immuables & Cycle de Vie**: Abandon immédiat de la numérotation séquentielle fragile. Chaque loi doit posséder un ID cryptique et immuable (ex: `VC-GOV-01`), accompagné d'un statut strict (`PROPOSED`, `CANONICAL`, `SUPERSEDED`).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Présence d'un ID cryptique immuable pour chaque règle.
* **[VC-META-02] L'Evidence Chain (No test, no law)**: Toute règle canonique n'a de valeur que si elle est auditable. Chaque loi du Codex doit désormais inclure son vecteur de vérification déterministe ou une procédure de validation explicitement définie (revue humaine, analyse sémantique, preuve documentaire).
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STRUCTURAL_CHECK`
  > Chaque loi `[VC-XXX-XX]` possède un bloc `[EVIDENCE_CHAIN]` avec un `EVIDENCE_TYPE` explicite (`OBSERVATION`, `TRACE`, `STRUCTURAL_CHECK`, `BEHAVIORAL_CHECK`, `STATE_CHECK`).
* **[VC-META-03] Anti-Semantic Bloat**: Prévention stricte de la duplication documentaire. Une directive canonique ne doit exister qu'à un seul endroit physique pour éviter les dérives et contradictions futures. Les apprentissages historiques (artéfacts) sont relégués aux archives.
  > **[EVIDENCE_CHAIN]**:
  > `EVIDENCE_TYPE: STATE_CHECK`
  > Absence de redondance sémantique, relégation des apprentissages historiques.

---

*Fin du document canonique.*
