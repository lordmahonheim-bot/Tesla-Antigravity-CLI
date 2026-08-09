# Plan d'Insertion Architectural : Paradigme "Book-to-Skill" dans Superpowers


**Date :** 2026-07-23
**Auteurs :** Orchestrateur Tesla, Master-Code, Curator-Prime, Premortem.

---

## 1. Justification Architecturale
Les agents utilisent des outils de lecture (comme `view_file` ou `context7`) dont la capacité de restitution est physiquement plafonnée (ex: 46KB / 800 lignes maximum par appel). 
Toute compétence monolithique dépassant cette limite subit une troncature, déclenchant invariablement le **biais de complaisance** du LLM (qui hallucine la suite au lieu de relancer un appel outil). 
L'injection du paradigme **"Book-to-Skill"** transforme la méta-compétence `superpowers:writing-skills` pour qu'elle apprenne aux agents à produire un "livre" structuré (Lazy Loading) plutôt qu'un texte monobloc.

---

## 2. Nouvelles Règles à Insérer (Blindées via Doctrine d'Actionnabilité)

Les blocs suivants doivent être ajoutés à `superpowers:writing-skills` :

### A. La Règle de Fragmentation (< 800 lignes)
> [!IMPORTANT]
> **Règle des 800 Lignes (Plafond Dur)**
> 800 lignes est un **plafond dur** lié aux limites de l'outil `view_file` (à vérifier selon l'environnement Antigravity CLI), mais l'objectif d'une compétence reste la concision (< 200–500 mots). Si le plafond est atteint, la compétence DOIT être fragmentée en "chapitres" autonomes (ex: `chapter_01_core.md`, `chapter_02_security.md`).

### B. Le Système de Routage (`SKILL.md` & `glossary.md`)
> [!NOTE]
> **L'Architecture de Routage (SKILL.md et glossary.md)**
> Lors de la création d'une compétence multi-fichiers :
> 1. Le fichier `SKILL.md` devient un **Routeur d'intentions**. Il **conserve la logique cœur** ; seule la référence lourde est externalisée. Il contient l'identité de la compétence et un Sommaire dirigeant l'agent vers les bons chapitres.
> 2. Un fichier `glossary.md` **DOIT** être créé comme index de routage absolu pour chaque concept clé.

### C. Les "Overlap Pointers" Actifs (Anti-Paresse LLM)
> [!TIP]
> **Overlap Pointers (Pointeurs de Chevauchement)**
> Chaque fin de chapitre fragmenté DOIT inclure un "Overlap Pointer" clair et **impératif**.
> *Format exigé :* `[SUITE DANS : ./chapters/chapter_02.md - ACTION REQUISE : Utilisez immédiatement l'outil view_file pour lire ce fichier. Objectif : Validation Sécurité]`

### D. Table des Rationalisations Spécifique "Lazy Loading"
En complément direct de la section "Blindage contre la rationalisation (Bulletproofing)", pour contrer le refus de lecture des agents sous pression, ajouter cette sous-table :

| Excuse de l'Agent | Réalité (Blindage) |
| --- | --- |
| "Le sommaire me donne assez de contexte." | Hallucination garantie. Utilisez `view_file` sur le chapitre cible. Aucune exception. |
| "Je connais déjà cette compétence." | Les compétences sont mises à jour. Lisez le chapitre ou échouez. |
| "Appeler view_file prend trop de temps." | Agir à l'aveugle corrompt la mission. Lisez le fichier cible. |

---

## 3. Séquencement Technique d'Édition

Voici les étapes strictes pour appliquer cette mise à jour au fichier `/home/lord-mahonheim/bifrost/tesla/.agents/skills/superpowers-writing-skills/SKILL.md` :

### Étape 1 : Mise à jour du Frontmatter et de l'Overview
- **Action** : Éditer la section `# Vue d'ensemble` pour introduire le concept d'architecture "Livre" (Lazy Loading).

### Étape 2 : Insertion de l'Arborescence
- **Action** : Dans `## Structure de répertoire`, **conserver l'idée d'« espace de noms plat » (pour la découverte)** et **ajouter en complément** l'arborescence de l'organisation interne :
  ```text
  /my-skill/
    ├── SKILL.md (Routeur)
    ├── glossary.md (Index absolu)
    └── chapters/ (Fichiers < 800 lignes)
  ```

### Étape 3 : Ajout des Règles Techniques (Blocs A, B, C, D)
- **Action** : Insérer les blocs de règles listés dans la Partie 2 dans le corps du texte.

### Étape 4 : Enrichissement des Anti-Patterns (APPEND-ONLY)
- **Action** : Ajouter 3 nouvelles erreurs courantes à la fin du document :
  - ❌ **Fichier Monolithique** : > 800 lignes (provoque troncature et hallucination).
  - ❌ **Routage Aveugle** : Pas de `glossary.md` ou absence de liens relatifs valides vers les chapitres.
  - ❌ **Pointeur Passif** : Lien vers la suite sans l'injonction d'utiliser `view_file`.
- ⚠️ **CONTRAINTE CRITIQUE DE CONFORMITÉ :** La modification de cette section doit se faire en mode **ENRICHISSEMENT (Append-Only)**. Aucune règle existante (notamment la protection "Exécution Atomique SQL" et les rationalisations TDD d'origine) ne doit être supprimée ou écrasée.
