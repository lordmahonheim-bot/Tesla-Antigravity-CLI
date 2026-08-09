---
type: reference
tags: [curation/certified, curator/prime, status/valid]
coterie: tesla
date: 2026-07-23
author: tesla-curator-prime
confidence_score: 95%
sources: []
---

# CERTIFIED REPORT: ARCHITECTURE & STRUCTURATION DU VAULT OBSIDIAN "AVALON"

## 1. Diagnostic Summary
Le présent rapport définit l'architecture de la base de connaissances "Avalon", un Second Cerveau sous Obsidian optimisé pour l'ère de l'Intelligence Artificielle. Conçu pour le système de Lord Mahonheim, ce référentiel intègre les paradigmes de Tiago Forte (AI Second Brain / BASB) et de Ali Pilevar (LLM Wiki / MCP), mariés à la flexibilité d'Obsidian. L'objectif est d'atteindre un équilibre entre l'organisation structurelle (PARA), l'émergence des idées (Zettelkasten / MOC) et l'automatisation agentique (Antigravity).

## 2. Verified Facts & Evidence Pack
- **Souveraineté (Local-First)** : Obsidian fonctionne en local sur des fichiers `.md`, garantissant la pérennité et la protection des données face à la volatilité des formats cloud propriétaires.
- **Délégation à l'IA (Modèle CODE)** : Selon T. Forte, la phase de "Distillation" est hautement automatisable par l'IA (résumés, connexions), mais la "Capture" reste un acte subjectif humain.
- **Orchestration Agentique** : A. Pilevar démontre qu'un agent (Claude Code / Antigravity) opérant à la racine d'un coffre peut lire, structurer et synthétiser l'information, guidé par un fichier persistant (`CLAUDE.md` ou équivalent).
- **Protocole MCP** : Permet de brancher le Second Cerveau à des flux externes, mais induit des risques d'injections si laissé en écriture totale (nécessité de brider les accès externes en lecture seule).

## 3. Comparative Reasoning & Hypotheses
- **Dossiers vs Liens** : Bien que la méthode PARA offre une taxonomie rassurante, une structure trop imbriquée devient rigide. Le réseau de liens bidirectionnels (MOC) est préféré pour la connectique conceptuelle (Bottom-Up).
- **Zettelkasten vs PARA** : L'idéal est une structure hybride. PARA classe l'information par *actionnabilité*, tandis que Zettelkasten et MOC traitent de l'*idéation*. Nous regroupons donc la classification temporelle (Projets/Domaines) avec un espace plat dédié aux atomes cognitifs (Zettelkasten/MOC).

## 4. Contradictions & System Limits
- **Risque de "Paresse Cognitive"** : Si l'agent IA effectue toute la synthèse (Distill) sans intervention de Lord Mahonheim, le cerveau biologique ne mémorise plus rien.
- **Corruptions YAML** : L'agent IA qui modifie les fichiers peut corrompre le frontmatter (YAML) en cas de mauvaise interprétation. Une validation stricte de l'écriture s'impose.
- **Surcharge du Graphe** : Au-delà de 10 000 notes, la Graph View d'Obsidian ralentit. Une gestion rigoureuse des *Attachments* et une syntaxe *Atomic Notes* sont obligatoires.

## 5. Architectural Recommendations

### 5.1 Proposition de la Nouvelle Arborescence de Dossiers
Une structure hybride optimisée, réduisant les silos tout en garantissant un cadre solide pour l'IA :

```text
Avalon-Vault/
  ├── 00-Inbox/            # Entonnoir d'entrée (Capture rapide humaine et bots)
  ├── 01-Projects/         # Tâches et objectifs avec date de fin (PARA)
  ├── 02-Areas/            # Domaines de responsabilités continus (PARA)
  ├── 03-Resources/        # Notes de lecture, curation, documentation brute
  ├── 04-Archives/         # Projets clos, ressources obsolètes (réduit le token-count RAG)
  ├── 10-Zettelkasten/     # Notes Permanentes atomiques (1 note = 1 idée)
  ├── 20-MOCs/             # Maps of Content (Index émergents et dynamiques)
  ├── 90-Attachments/      # Média centralisé (Images, PDF, Audio)
  ├── 99-System/           # Templates, Scripts Dataview
  └── ANTIGRAVITY.md       # Fichier Master Prompt / Gouvernance pour l'agent (ex-CLAUDE.md)
```

### 5.2 Schéma des Métadonnées (Propriétés YAML) Obligatoires
Pour garantir l'interopérabilité avec Dataview et la compréhension parfaite de l'agent Antigravity, chaque note doit inclure un frontmatter YAML standardisé :

```yaml
---
aliases: []
tags: []
type: [inbox | project | area | resource | permanent-note | moc]
status: [draft | wip | review | done | archived]
created: YYYY-MM-DD
modified: YYYY-MM-DD
source: "" # URL ou référence (si applicable)
---
```

### 5.3 Gouvernance des Liens (MOC et Tags)
- **Liens Internes (Wikilinks)** : Privilégier systématiquement la syntaxe `[[Concept]]` pour relier des thèmes, idées, et individus.
- **Maps of Content (MOC)** : Les MOC remplacent les sous-dossiers. Dès qu'un thème accumule trop de notes orphelines, une MOC est créée pour indexer ces notes via des liens bidirectionnels.
- **Gestion des Tags** : Les tags `#` ne doivent **jamais** désigner des concepts (ex: pas de `#intelligence-artificielle`). Ils sont strictement réservés pour l'état et la nature du fichier (ex: `#status/wip`, `#type/moc`, `#zone/perso`). Limité à 2 ou 3 tags par note.

### 5.4 Règles d'Hygiène et Ponts d'Interfaçage avec Antigravity
1. **Le Master Prompt (`ANTIGRAVITY.md`)** : Placé à la racine, c'est l'ADN du coffre. Antigravity le lit à chaque initialisation pour assimiler le format, la "Brand Voice" de Lord Mahonheim, et les règles d'insertion.
2. **Atomicité des Scripts de l'Agent** : L'agent a l'interdiction de remplacer l'intégralité du coffre. Ses écritures (`/wikify`, `/alfred`) doivent cibler l'édition chirurgicale de fichiers spécifiques pour éviter la perte de données (Self-Healing).
3. **Revue Hebdomadaire Obligatoire** : Antigravity peut proposer des tags, synthétiser des réunions et trier le `00-Inbox/`, mais Lord Mahonheim doit valider humainement la promotion d'une note temporaire vers le dossier `10-Zettelkasten/`.
4. **Interfaçage MCP Bridé** : L'ingestion de flux externes (Gmail, Telegram, Slack) via les serveurs MCP se fait strictement en *Lecture Seule*. L'agent Antigravity lit la source, et c'est lui qui écrit la note dans le Vault Avalon, écartant ainsi tout risque d'injection directe depuis l'extérieur.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
