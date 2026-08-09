# Spécifications d'Architecture du Graphe Obsidian (TASLB)

Ce document canonique définit les standards de modélisation pour la transposition de la mémoire IA (TASLB) en un réseau relationnel natif dans Obsidian. Ces spécifications guideront le développement du script `session_to_graph.py`.

---

## 1. Règles de Nommage & Format des Métadonnées (YAML Frontmatter)

Chaque nœud du graphe correspond à un fichier Markdown (`.md`). Pour garantir l'interopérabilité avec les agents, le moteur FTS5 et la vue Graphe, chaque fichier doit respecter un en-tête YAML strict.

### 1.1. Règles de Nommage
- **Format du nom de fichier** : `[Type]_[Nom_Entite].md` (ex: `Agent_Tesla-Curator-Prime.md`, `Projet_Chantier-021.md`, `Log_2026-07-22.md`).
- **Casse et caractères** : PascalCase pour les entités, espaces remplacés par des tirets (`-`) ou underscores (`_`). Pas de caractères spéciaux ou accents dans le nom de fichier.

### 1.2. Structure du YAML Frontmatter
```yaml
---
id: "UUID-v4"
title: "Titre lisible de l'entité"
type: "Agent | Projet | Concept | Log"
tags:
  - "#agent"
  - "#statut/actif"
aliases:
  - "Tesla Curator Prime"
  - "Curator"
created: "YYYY-MM-DDTHH:MM:SSZ"
updated: "YYYY-MM-DDTHH:MM:SSZ"
connections:
  - "[[Node_A]]"
  - "[[Node_B]]"
---
```
*Note : Le bloc `connections` permet au RAG d'extraire rapidement les voisins (Depth=1) sans parser tout le corps du texte.*

---

## 2. Spécification Technique de la Colorimétrie (`.obsidian/graph.json`)

Pour une lecture cognitive immédiate de l'écosystème, la vue Graphe doit être automatiquement colorisée selon la doctrine du **Vigilum Codex**.

Le fichier `.obsidian/graph.json` du vault devra inclure (ou être mis à jour par un script de provisionning) les groupes de couleurs suivants dans son tableau `colorGroups` :

| Filtre (Query) | Logique / Sémantique | Code Couleur (Hex) | Rendu Visuel |
|---|---|---|---|
| `tag:#agent OR tag:#systeme` | Intelligence Agentique, la logique pure. | `#00E5FF` | 🔵 Cyan Électrique |
| `tag:#strategie OR tag:#veille` | Vision long terme, exploration, architecture. | `#9D00FF` | 🟣 Violet Profond |
| `tag:#statut/actif` | Le creuset de l'ingénierie, chantiers en cours. | `#FFB300` | 🟡 Or / Ambre |
| `tag:#statut/clos OR tag:#mvp` | Les trophées, MVP livrés, voie sécurisée. | `#00FF66` | 🟢 Vert Néon / Émeraude |
| `tag:#premortem OR tag:#bloque` | Ligne rouge, résilience, audits de sécurité. | `#FF003C` | 🔴 Rouge Cramoisi |

**Format cible attendu dans `graph.json` (exemple JSON) :**
```json
"colorGroups": [
  {
    "query": "tag:#agent OR tag:#systeme",
    "color": { "a": 1, "rgb": 58879 } 
  }
]
```

---

## 3. Spécifications pour le Pipeline `session_to_graph.py`

Le script `session_to_graph.py` est chargé de transformer les sessions (logs, conversations) en entités du graphe (nœuds et liens). 

### 3.1. Règles d'Ingestion
1. **Extraction d'Entités** : Utilisation de l'API Gemini pour parser `SESSION_TRANSCRIPTS.md` et identifier les entités principales (Projets, Agents, Concepts).
2. **Création/Mise à jour (Upsert)** :
   - Si le fichier de l'entité n'existe pas, le script le crée avec le template YAML Frontmatter approprié.
   - Si le fichier existe, le script fusionne les nouvelles informations et met à jour le champ `updated`.
3. **Génération de Wikilinks** : 
   - Toute mention d'une autre entité dans le corps du texte doit être encapsulée dans un lien natif Obsidian `[[Nom_Entite]]`.
   - Le script doit utiliser les `aliases` existants pour lier correctement des variations de noms (ex: "Curator" -> `[[Agent_Tesla-Curator-Prime|Curator]]`).
4. **Logs Quotidiens (Build in Public)** :
   - Chaque exécution clôturant une journée crée un nœud `Daily_Log_YYYY-MM-DD.md`.
   - Ce log contient des wikilinks vers tous les chantiers/agents ayant été actifs ce jour-là, centralisant la vue temporelle dans le graphe.

### 3.2. Garde-fous (Prévention du Semantic Bloat)
- **Densité des liens** : Le script ne doit lier que les entités contextuellement pertinentes (pas de liaison systématique de mots communs).
- **Orphelinat de Graphe** : Toute nouvelle entité doit être liée au minimum à un `Daily_Log` ou un `Projet` parent pour ne pas flotter hors du réseau principal.
