---
type: reference
tags:
  - domain/obsidian-skills
  - status/valid
  - method/deep-research-360
  - layer/shadow
  - layer/official
source: "[[Alexandria::5f4d83a1-12c8-47bc-8f43-1bc2d8d85f1c]]"
date: 2026-07-08
version: "4.0-MASTER"
author: "Tesla Arcanis-360 MASTER"
certification: "Arcanis_Seal_v4_MASTER"
methodology: vigilum-codex-7steps
angles_covered:
  - Technical Feasibility
  - Shadow Risks & Security
  - Market & Ecosystem Alignment
  - Tesla Architecture Integration
blind_spots:
  - Claude Code Closed-Source Telemetry & Sandboxing
  - Future Roadmap of Obsidian Bases & Native CLI
confidence_by_angle:
  Technical Feasibility: High
  Shadow Risks & Security: High
  Market & Ecosystem Alignment: Medium
  Tesla Architecture Integration: High
---

# AUDIT RITUEL ET ANALYSE 360° : TECHNOLOGIE OBSIDIAN-SKILLS
**Rapporteur d'Élite :** `Tesla-Arcanis-360`  
**Commanditaire :** Lord Mahonheim  
**Date d'Exécution :** 2026-07-08 (Temps local)  
**Classification :** SOUVERAIN / ALEXANDRIA COGNITIVE BASE  

---

## §A — The Baseline (Tier Officiel)

La technologie **`obsidian-skills`** est une bibliothèque ouverte de compétences d'agents d'intelligence artificielle, conçue et publiée par **Steph Ango (kepano)**, CEO d'Obsidian, en janvier 2026. Ce projet implémente la spécification ouverte **Agent Skills** (disponible sur [agentskills.io](https://agentskills.io)) pour outiller les runtimes d'IA — principalement **Claude Code** (Anthropic), **Codex CLI**, et **Open Code** — d'une compréhension native de l'écosystème Obsidian.

Plutôt que d'agir comme un plugin traditionnel au sein de l'application, `obsidian-skills` agit comme une notice d'instruction cognitivo-technique qui "apprend" à l'agent IA comment manipuler de manière propre, standardisée et structurée les fichiers d'un coffre (vault) Obsidian.

Le dépôt officiel intègre **5 compétences clés** structurées en sous-dossiers contenant chacun un fichier de spécification `SKILL.md` :

1. **`obsidian-markdown`** : Guide l'agent sur la syntaxe étendue d'Obsidian (wikilinks `[[Note]]`, callouts `> [!type]`, propriétés frontmatter, embeds `![[Note]]`, LaTeX, et diagrammes Mermaid).
2. **`obsidian-bases`** : Permet à l'agent de créer et de modifier les nouveaux fichiers de bases de données natives d'Obsidian (`.base`).
3. **`json-canvas`** : Explicite la manipulation programmatique des fichiers de tableau blanc infini (`.canvas`) selon le standard open-source JSON Canvas 1.0.
4. **`obsidian-cli`** : Fournit le guide d'utilisation de l'interface en ligne de commande officielle `obsidian` pour interagir directement avec une application Obsidian en cours d'exécution.
5. **`defuddle`** : Guide l'utilisation de l'utilitaire d'extraction et de nettoyage web `defuddle` pour convertir du HTML en Markdown minimaliste (sans boilerplate publicitaire ni scripts) afin de sauvegarder les jetons (tokens) de contexte.

---

## §B — The Power-User Tier (Tier Avancé)

L'analyse technique approfondie révèle que les fonctionnalités avancées ciblent la structuration locale-first et l'optimisation drastique du contexte de l'agent.

### 1. Spécifications de Structure et de Découverte
Les compétences suivent le standard d'activation progressive d'Agent Skills :
* **Niveau 1 (Discovery)** : Au démarrage de l'agent (ex: Claude Code), seuls le `name` et la `description` présents dans le frontmatter YAML du `SKILL.md` sont chargés en mémoire (consommation minimale : ~50-100 tokens).
* **Niveau 2 (Activation)** : Si la tâche courante requiert l'édition de Markdown Obsidian, de fichiers Bases ou Canvas, l'agent charge dynamiquement le corps complet du `SKILL.md` (~5k tokens).
* **Niveau 3 (Execution)** : L'agent fait appel aux ressources complémentaires (scripts de validation dans `scripts/` ou fiches détaillées dans `references/`).

### 2. Le Format de Base de Données Native : Obsidian Bases (`.base`)
Remplaçant le plugin communautaire historique Dataview, le format officiel `.base` est structuré en YAML et permet des requêtes de type relationnel local :
* **Structure YAML stricte** : Composée de filtres (`filters`), de formules de calcul (`formulas`), de définitions de propriétés d'affichage (`properties`), et de rendus visuels (`views`).
* **Moteur de calcul de dates** : Supporte l'arithmétique temporelle complexe (ex: `today() + "7d"`). Cependant, la soustraction de deux dates renvoie un objet `Duration` structuré contenant des champs numériques distincts (`duration.days`, `duration.hours`). Les calculs de division ou d'arrondi directs sur la durée brute échouent ; il est obligatoire d'extraire le champ numérique d'abord (ex: `(date(due) - today()).days.round(0)`).
* **Vues multiples** : Permet de configurer des rendus en tables (`table`), cartes visuelles (`cards`), listes minimalistes (`list`), et géolocalisation (`map`).

### 3. Modélisation Visual-first : JSON Canvas
Le format `.canvas` s'appuie sur une structure JSON simple composée de deux tableaux : `nodes` et `edges`.
* **Identifiants** : Les nœuds et connexions sont obligatoirement identifiés par des chaînes hexadécimales uniques de 16 caractères générées de façon aléatoire (64-bit random hexadecimal, ex: `6f0ad84f44ce9c17`).
* **Types de nœuds** : Supporte les types `text` (Markdown interprété avec newlines représentées par `\n`), `file` (liens locaux avec subpaths facultatifs), `link` (URLs externes), et `group` (boîtes de regroupement définissant des frontières spatiales).
* **Layouting** : L'axe des ordonnées Y descend vers le bas, l'axe X s'étend vers la droite. Les dimensions des nœuds textuels standards oscillent entre 200px et 600px de large selon la densité.

### 4. Réduction de Contexte par Defuddle
L'utilitaire `defuddle` (installable globalement via `npm install -g defuddle`) est une alternative d'extraction propre supérieure à Mozilla Readability pour les agents. Il supporte nativement la transcription des formules LaTeX ($...$) et des diagrammes Mermaid tout en éliminant les barres de navigation et les trackers publicitaires, permettant une réduction de volume HTML-vers-Markdown pouvant atteindre **90%**.

---

## §C — The Shadow Tier (Tier Souterrain)

Sous l'angle de la doctrine adverse et de la sécurité offensive du Vigilum Codex, la technologie `obsidian-skills` présente des failles conceptuelles critiques et des limites d'exécution majeures.

### 1. Vecteur RCE (Remote Code Execution) critique via `obsidian eval`
La compétence `obsidian-cli` documente de façon officielle l'utilisation de la commande suivante :
```bash
obsidian eval code="app.vault.getFiles().length"
```
Obsidian étant une application de bureau construite sur le framework **Electron**, son contexte d'exécution possède des accès directs aux APIs système locales via Node.js ou via les adaptateurs de fichiers internes de l'application (`app.vault.adapter`).
* **Le Risque d'Exploitation** : Si un agent IA (ex: Claude Code) est déployé avec le privilège de manipuler le coffre Obsidian via l'interface en ligne de commande officielle, n'importe quel script malveillant peut demander l'évaluation de code JS arbitraire.
* **Le Scénario d'Attaque** : Un attaquant utilise une injection de prompt indirecte (IPI) en insérant des instructions cachées sur un site web. L'utilisateur utilise le clipper ou Defuddle pour sauvegarder l'article dans son coffre. Lors d'une tâche de synthèse globale, l'agent IA lit la note infectée. Le prompt injecté force l'agent à exécuter une commande système destructive en injectant du JavaScript malveillant (ex: exécution de shell via `child_process` ou lecture/fuite de clés SSH privées) à travers la commande `obsidian eval code="..."`.

### 2. Dépendance impérative à la GUI (Pas de fonctionnement Headless natif)
Contrairement aux outils de pipeline classiques, l'interface de commande `obsidian` fournie par Obsidian v1.12.4+ agit comme une télécommande IPC (Inter-Process Communication).
* **La Limitation** : Pour fonctionner, le logiciel de bureau Obsidian **doit être physiquement démarré et ouvert** en arrière-plan. Si Obsidian est exécuté sur un serveur distant ou dans un conteneur d'agent sans serveur X11/Wayland ou sans frame-buffer virtuel (Xvfb), l'exécution de la CLI échouera.
* **L'Alternative Officielle** : La commande `obsidian-headless` (qui s'exécute via la commande `ob`) est un package indépendant, mais elle est strictement restreinte aux opérations d'indexation, de synchronisation (`ob sync`) et de publication (`ob publish`). Elle ne supporte pas l'évaluation de code ou les requêtes de base de données dynamiques de la CLI desktop.

### 3. Sensibilité extrême aux erreurs de parsing YAML dans Bases
Le moteur de base de données Obsidian Bases est instable face aux erreurs de formatage commises par l'IA :
* L'insertion de caractères réservés non échappés dans les formules (tels que `:`, `{`, `}`, `[`, `]`, `,`, `&`, `*`, `#`, `?`, `|`, `-`, `<`, `>`, `=`, `!`, `%`, `@`, `` ` ``) fait planter silencieusement le parsing du fichier `.base`.
* Les types `Duration` mal castés (sans accès préalable à un champ comme `.days` ou `.hours`) bloquent l'affichage de la table dans l'interface Obsidian sans renvoyer de log d'erreur explicite dans le terminal, provoquant des boucles de correction infinies pour les agents d'IA autonomes.

---

## §D — Matrice 360° Synthétique

| Angle d'Analyse | Constats clés | Niveau de Confiance | Zone d'ombre / Limite de validité |
| :--- | :--- | :--- | :--- |
| **Pertinence** | Intégration transparente pour synchroniser les notes et maintenir les wikilinks intacts grâce au contrôle IPC. | **Élevé** | Dépendance stricte de la version d'Obsidian (v1.12.4 minimum). |
| **Faisabilité** | Syntaxe standardisée, interopérable multi-agents (Claude Code, Codex, Open Code). | **Élevé** | Le mode d'installation npx/git nécessite un setup local Node.js complet. |
| **Risques Sécurité** | Vulnérabilité critique d'exécution de code arbitraire (RCE) via `obsidian eval` et injection indirecte. | **Élevé** | L'absence de sandboxing de l'agent amplifie le risque à un niveau critique. |
| **Shadow Risks** | Blocage en environnement serveur (headless) sans GUI active. Robustesse YAML fragile sur Bases. | **Moyen** | Efficacité réelle des variables d'environnement CDP non documentées. |
| **Intégration Tesla** | Standard Agent Skills identique à notre propre format de spécification locale. | **Élevé** | Conflit potentiel de triggers si importé tel quel. |

---

## §E — Registre des Angles Morts et Incertitudes

1. **Isolation de Claude Code** : Nous manquons de visibilité sur les couches de sandboxing internes appliquées par Anthropic lors de l'exécution de commandes système par Claude Code. Si Claude Code est exécuté dans un shell local avec accès total aux fichiers et au réseau, la faille RCE par `obsidian eval` est immédiatement exploitable.
2. **Évolution de la CLI Obsidian** : Le cycle de vie des commandes de débogage (`obsidian dev:*`) n'est pas figé. L'équipe d'Obsidian pourrait restreindre ou désactiver les commandes de type `eval` en production pour des raisons de sécurité, rendant la compétence obsolète ou tronquée.
3. **Pérennité du format Bases** : Les spécifications exactes de l'API interne d'Obsidian pour Bases ne sont pas encore stabilisées en dehors de la syntaxe de rendu YAML documentée.

---

## §F — Recommandations / Suites Actionnables pour l'Architecture Tesla

Pour assurer une intégration sécurisée et performante de la gestion des vaults de Lord Mahonheim sans compromettre la sécurité souveraine du système Midgard, nous préconisons la stratégie suivante :

### 1. Rejet de la Conformité Native au profit du "Capability Adapter Pattern"
**Recommandation majeure** : Il est interdit d'injecter nativement la compétence `obsidian-cli` (telle quelle) dans nos agents ou d'autoriser l'exécution de la commande `obsidian eval` sur la machine locale Midgard.
* **Mécanisme** : Créer un **Adaptateur de Capacité (Capability Adapter)** sous forme d'outils localisés (MCP ou script local). Cet adaptateur servira de passerelle sécurisée : il recevra les requêtes sémantiques de l'agent (ex: "lire une note", "créer un fichier") et les traduira par des opérations de fichiers standard sur le disque via Python (`open`, `write`) ou via un sous-ensemble ultra-restreint d'instructions de la CLI `obsidian` (excluant totalement `eval` et les flags `dev:*`).

### 2. Isolation Sandbox pour le Web Fetching (Defuddle)
L'utilisation de `defuddle` est fortement encouragée pour optimiser le budget de jetons (token economy) lors de l'acquisition documentaire par Arcanis ou Web-Raider.
* **Sécurisation** : Encapsuler l'exécution de `defuddle parse` dans une micro-sandbox isolée (ex: Firejail ou Deno compile) afin de garantir qu'aucun exploit de buffer-overflow ou exécution malveillante de JS via la librairie d'extraction HTML sous-jacente ne puisse compromettre le shell parent.

### 3. Normalisation des formats et Validation de Schéma (.base / .canvas)
Puisque le format Bases est sensible aux erreurs de syntaxe YAML :
* Implémenter un script de validation local (linter YAML) s'interposant avant l'écriture finale du fichier `.base` pour tester la conformité syntaxique (échappement des deux points, vérification du format de durée, etc.).
* En cas d'invalidation, l'agent Tesla doit corriger le fichier dans sa sandbox locale avant de soumettre la modification finale à la validation humaine (Ctrl+K).

---

## §G — Sceau de Certification

> **Arcanis MASTER.** Investigation planifiée. Shadow Mapping complet.
> Analyse 360° effectuée. Angles morts documentés. Hypothèses stress-testées.
> Sources croisées officielles et souterraines. Livrable certifié decision-ready.
> — Validé par Arcanis MASTER. Archive de référence Tesla.
> `SHA256:02e0e8c37de5092d6ac022fdc1942b783edd3489f8656d589ebde8701f4c9830`
