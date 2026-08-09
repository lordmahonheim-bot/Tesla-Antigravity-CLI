---
type: documentation
tags: [documentation/systeme, chantier/gouvernance, statut/valide]
date_creation: 2026-06-29
date_derniere_maj: 2026-06-30
version: 1.0
---

# 📋 SYSTÈME DE GESTION DE CHANTIERS — TESLA / BIFROST
**Doctrine :** Vigilum Codex  
**Opérateur :** Lord Mahonheim (Abdellah MOUHTAJ)  
**Agent responsable :** Tesla (sur Antigravity CLI)  
**Environnement :** MIDGARD (Linux, local)  
**Déploiement :** 2026-06-29

---

## 1. Raison d'Être

Ce système a été conçu pour répondre à un besoin simple : **tracer chaque projet de travail entre Mahonheim et Tesla, du premier souffle d'idée jusqu'à la cérémonie d'archivage.**

Avant ce système, les chantiers vivaient en fragments dispersés : des références dans `PROJECT_STATE.md`, des fichiers dans `OUTPUTS/`, des notes dans Avalon. Il n'y avait pas de point unique de vérité pour un chantier donné.

**Ce que ce système apporte :**
- Un **cahier de charges unique et exhaustif** par chantier.
- Une **traçabilité complète** du cycle de vie (ouverture → archivage).
- Une **gouvernance claire** : Mahonheim valide, Tesla exécute.
- Une **mémoire persistante** synchronisée avec Alexandria et Obsidian Avalon.

---

## 2. Architecture du Système

```
/Gestion-de-Chantiers/
│
├── README.md                                  ← Ce fichier (documentation du système)
├── INDEX.md                                   ← Tableau de bord des chantiers actifs
│
├── [NOM-DU-CHANTIER]_v1.0_YYYY-MM-DD.md      ← Cahier de charges d'un chantier actif
├── [NOM-DU-CHANTIER]_v2.0_YYYY-MM-DD.md      ← Version révisée si nécessaire
│
└── Archivage-de-Chantiers/
    ├── README.md                              ← Registre des chantiers clôturés
    └── [NOM-DU-CHANTIER]_v1.0_YYYY-MM-DD.md  ← Chantiers terminés (immuables)
```

> **Note Git :** Ce dossier entier est exclu du suivi Git (`.gitignore`). Les cahiers de charges sont des documents de gouvernance interne, non destinés aux dépôts publics.

---

## 3. Convention de Nommage

Chaque fichier chantier suit ce format strict :

```
[NOM-DU-CHANTIER]_v[VERSION]_YYYY-MM-DD.md
```

**Exemples :**
```
PLAN-ARMEMENT-PLURIDISCIPLINAIRE_v1.0_2026-06-28.md
PLAN-ARMEMENT-COGNITIF_v1.0_2026-06-29.md
HARDWARE-GUARD-DAEMON_v1.0_2026-07-01.md
```

**Règles :**
- Nom en MAJUSCULES avec tirets (pas d'espaces, pas d'underscores).
- Version `v1.0` à l'ouverture. Incrémentée (`v2.0`) si révision structurelle majeure.
- Date = date d'**ouverture** du chantier (pas de mise à jour).
- Extension `.md` obligatoire.

---

## 4. Cycle de Vie d'un Chantier

```
                 ┌─────────────────┐
                 │    IDÉE INITIALE │
                 │  (dans la tête  │
                 │  de Mahonheim)  │
                 └────────┬────────┘
                          │ "J'ouvre un chantier X"
                          ▼
                 ┌─────────────────┐
                 │   🟢 OUVERT     │  Tesla crée le fichier + met à jour INDEX.md
                 └────────┬────────┘
                          │ Première tâche lancée
                          ▼
                 ┌─────────────────┐
                 │   🔵 ACTIF      │  Tâches en cours d'exécution
                 └────────┬────────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐
    │  ⚪ SUSPENDU    │      │  🔴 BLOQUÉ      │
    │  (veille tempo- │      │  (dépendance    │
    │   raire)        │      │   non résolue)  │
    └────────┬────────┘      └────────┬────────┘
             │                         │
             └────────────┬────────────┘
                          │ Reprise
                          ▼
                 ┌─────────────────┐
                 │ 🟡 EN VALIDATION│  Tesla soumet, Mahonheim valide
                 └────────┬────────┘
                          │ Feu vert de Mahonheim
                          ▼
                 ┌─────────────────┐
                 │   ✅ TERMINÉ    │  Archivage dans Archivage-de-Chantiers/
                 └─────────────────┘
```

**Tableau des statuts :**

| Emoji | Statut | Déclencheur |
|---|---|---|
| 🟢 | Ouvert | Création du fichier chantier |
| 🔵 | Actif | Première tâche en cours d'exécution |
| ⚪ | Suspendu | Mise en veille temporaire (décision externe attendue) |
| 🔴 | Bloqué | Impossibilité technique ou dépendance non résolue |
| 🟡 | En validation | Tâches terminées, attente du feu vert de Mahonheim |
| ✅ | Terminé | Chantier clos et archivé |

---

## 5. Structure d'un Cahier de Charges

Chaque fichier chantier contient obligatoirement les **11 sections suivantes** :

| # | Section | Contenu |
|---|---|---|
| 1 | **Idée Initiale** | La genèse — de la pensée brute à la formalisation |
| 2 | **Description** | Périmètre, objectif, contexte, ce qui est hors-périmètre |
| 3 | **Objectif Cible** | Définition du succès (ce qu'on obtient à la fin) |
| 4 | **Hiérarchie** | Chantier parent / enfants liés |
| 5 | **Phases & Calendrier** | Tableau des phases avec livrable et statut par phase |
| 6 | **TODO List** | Liste de tâches cochables par phase |
| 7 | **Ressources & Fichiers Liés** | Tous les fichiers, scripts, skills, dépôts liés |
| 8 | **Journal de Bord** | Log chronologique des événements et décisions |
| 9 | **Risques & Blocages** | Tableau risques × niveau × mitigation |
| 10 | **Critères de Clôture** | Definition of Done — checklist de validation finale |
| 11 | **Signature & Horodatage** | Complété à l'archivage uniquement |

---

## 6. Hiérarchie Parent / Enfant

Un chantier peut être **racine** (sans parent) ou **enfant** d'un autre chantier.

**Exemple :**
```
PLAN-ARMEMENT-PLURIDISCIPLINAIRE (parent / racine)
    ├── HARDWARE-GUARD-DAEMON (enfant — Phase 1)
    ├── SELF-HEALING-PYRIGHT (enfant — Phase 2)
    └── TESLA-GITHUB-AUTOMATION (enfant — Phase 3)
```

**Règle d'archivage avec enfants non terminés :**
> ⚠️ Si un chantier parent est archivé alors que des enfants sont encore ouverts, Tesla émet un avertissement explicite. L'archivage n'est pas bloqué, mais la décision appartient à Mahonheim.

---

## 7. Protocoles d'Utilisation

### 7.1 Ouvrir un Chantier

**Déclencheur :** Mahonheim dit *"J'ouvre un chantier [NOM]"*

**Séquence Tesla :**
1. Poser 2-3 questions de cadrage rapides (périmètre, objectif, dépendances).
2. Créer le fichier `[NOM]_v1.0_YYYY-MM-DD.md` dans `Gestion-de-Chantiers/`.
3. Mettre à jour `INDEX.md` (ligne + statistiques).
4. Mettre à jour `memory/PROJECT_STATE.md` (résumé hybride + lien).
5. Indexer le fichier dans Alexandria (FTS5).

### 7.2 Mettre à Jour un Chantier

À chaque avancement significatif (tâche terminée, décision prise, blocage levé) :
1. Mettre à jour la TODO List (`[ ]` → `[x]`).
2. Ajouter une ligne au Journal de Bord (date + événement + décision).
3. Mettre à jour le statut dans le frontmatter YAML.
4. Re-indexer dans Alexandria.
5. Mettre à jour `INDEX.md` si le statut change.

### 7.3 Archiver un Chantier

**Déclencheur :** Mahonheim valide la clôture.

**Séquence Tesla :**
1. Vérifier les Critères de Clôture (DoD) — signaler les items non cochés.
2. ⚠️ Si des enfants sont non terminés : avertir Mahonheim (pas de blocage strict).
3. Compléter la **Section 11** (Signature + Horodatage de clôture + résultat).
4. Déplacer le fichier dans `Archivage-de-Chantiers/`.
5. Mettre à jour `INDEX.md` (retirer de l'actif, ajouter aux archives).
6. Mettre à jour `memory/PROJECT_STATE.md`.
7. Mettre à jour `Archivage-de-Chantiers/README.md`.
8. Re-indexer dans Alexandria.

---

## 8. Intégration dans l'Écosystème Bifrost

```
                        [ Mahonheim ]
                             │
                     "J'ouvre un chantier"
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Gestion-de-Chantiers/      │
              │   ├── INDEX.md               │ ◄── Point d'entrée Obsidian
              │   └── [CHANTIER]_v1.0.md    │
              └──────────────┬───────────────┘
                             │ Synchronisation
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
         ┌──────────────┐   ┌──────────────────┐
         │PROJECT_STATE │   │ Alexandria (FTS5) │
         │    .md       │   │ alexandria_brain  │
         │  (résumé)    │   │     .db          │
         └──────────────┘   └──────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  Avalon (Obsidian│
         │  02-Logbook/     │
         │  Journal/)       │
         └──────────────────┘
```

**Rôles de chaque composant :**

| Composant | Rôle |
|---|---|
| `Gestion-de-Chantiers/[CHANTIER].md` | Source de vérité — tout le détail du chantier |
| `Gestion-de-Chantiers/INDEX.md` | Tableau de bord — vue d'ensemble pilotable depuis Obsidian |
| `memory/PROJECT_STATE.md` | Checkpoint de session — résumé hybride + liens vers chantiers |
| `Avalon/02-Logbook/Journal/` | Journal de sessions — chronologie des décisions |
| `Alexandria (FTS5)` | Moteur de recherche — requêtes MATCH sur tous les chantiers |

---

## 9. Chantiers Actuellement Actifs

*(Voir [INDEX.md](INDEX.md) pour le tableau de bord complet et à jour.)*

| # | Chantier | Statut | Ouvert le |
|---|---|---|---|
| 001 | Plan d'Armement Pluridisciplinaire | 🟡 En validation | 2026-06-28 |
| 002 | Plan d'Armement Cognitif | 🟡 En validation | 2026-06-29 |

---

## 10. Règles de Gouvernance

1. **Un chantier = un fichier.** Pas de mélange de chantiers dans un même document.
2. **Mahonheim décide, Tesla exécute.** Aucune phase ne démarre sans feu vert explicite.
3. **Le Journal de Bord ne ment pas.** Tout événement y est tracé, y compris les échecs et les blocages.
4. **Archivage = immuabilité.** Un chantier archivé ne se modifie pas. En cas de reprise, ouvrir un nouveau chantier `v2.0`.
5. **Gitignore absolu.** Aucun cahier de charges ne doit être commité dans un dépôt public ou partagé.
6. **Indexation systématique.** Chaque création ou mise à jour majeure déclenche une ré-indexation Alexandria.

---

## 11. Glossaire

| Terme | Définition |
|---|---|
| **Chantier** | Unité de travail avec un périmètre défini, un début et une fin. Peut être grand (plan stratégique) ou petit (tâche technique). |
| **Cahier de Charges** | Le fichier `.md` qui documente exhaustivement un chantier. C'est la source de vérité. |
| **INDEX.md** | Tableau de bord des chantiers actifs. Mis à jour automatiquement par Tesla. |
| **DoD** | Definition of Done — critères binaires qui définissent quand un chantier est réellement terminé. |
| **Archivage** | Action de déplacer un chantier terminé dans `Archivage-de-Chantiers/`. Déclenché par Mahonheim. |
| **Feu vert** | Validation explicite de Lord Mahonheim permettant le lancement d'une phase ou la clôture d'un chantier. |

---

*Documentation rédigée par Tesla sur Antigravity CLI | Doctrine Vigilum Codex*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
