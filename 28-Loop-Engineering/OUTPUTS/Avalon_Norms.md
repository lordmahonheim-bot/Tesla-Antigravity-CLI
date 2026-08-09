# Normes et Topologie d'Avalon (Tesla Avalon Second Living Brain)

Ce document établit les normes d'architecture du graphe et des métadonnées pour le Second Cerveau `Avalon`, suite à l'audit structurel (`Audit_Avalon_Vision.md`). Ces règles sont obligatoires pour garantir l'intégrité du système et le maillage neuronal RAG (Retrieval-Augmented Generation).

## 1. Template YAML Obligatoire (Frontmatter)

Tout fichier Markdown (notamment les fichiers orphelins) doit impérativement inclure le Frontmatter YAML suivant en tête de fichier. Ce schéma garantit une indexation correcte par les scripts d'Alexandria et par le graphe Obsidian.

```yaml
---
title: "Titre exact de la note"
aliases: ["Alias éventuel 1", "Acronyme"]
tags: ["#concept", "#agent", "#projet"]
type: "concept | projet | ressource | log | moc"
status: "actif | en_cours | archive | brouillon"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---
```

**Règles de Topologie et Wikilinks :**
- **Obligation de Liens :** Chaque fichier doit inclure au minimum un wikilink `[[Nom de la note MOC ou parente]]` pour éviter de rester orphelin.
- Le champ `type` servira à définir la coloration automatique du graphe dans `.obsidian/graph.json` selon la logique du Vigilum Codex.

## 2. Politique Stricte de Classement (01-Library vs 03-Resources)

Pour pallier la pollution de la racine et harmoniser l'organisation (SGC), la séparation entre l'action et la documentation doit être stricte.

### `01-Library` (Centre Névralgique Actif)
- **Définition :** Contient l'ensemble des projets en cours d'exécution, le design des agents actifs et les chantiers courants.
- **Cible :** Documentation technique d'implémentation, architectures en cours (ex: `Antigravity-Agent-Design`).
- **Caractéristique :** Fichiers avec un `status: "actif"` ou `"en_cours"`.

### `03-Resources` (Référentiel Passif et Connaissances Froides)
- **Définition :** Héberge les connaissances externes, les standards, les tutoriels et la documentation figée.
- **Cible :** Bibliothèques de prompts, notes de recherche (ex: `GitHub-Best-Practices`).
- **Caractéristique :** Ces dossiers servent de bibliothèque (Read-Only) de référence pour les agents, sans action directe sur la base de code active.

*Note de sécurité : Les exécutables (`.py`) et les bases de données binaires (`.db`) sont strictement proscrits de la racine de connaissances documentaires d'Obsidian et doivent être isolés, par exemple dans un dossier `03-Resources/Scripts` bien délimité ou hors du vault.*
