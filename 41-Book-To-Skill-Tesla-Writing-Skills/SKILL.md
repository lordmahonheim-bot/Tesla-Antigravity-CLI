---
name: tesla-writing-skills
injection_type: shadow-targeted
target_subagent: self
skillopt_version: 1.0.0
skillopt_schedule: cosine
skillopt_default_lr: 4
skillopt_floor: 2
skillopt_batch_size: 40
skillopt_reflection_minibatch: 8
description: "À utiliser lorsque l'agent doit concevoir, rédiger, tester (TDD), injecter par shadow-targeting ou vérifier une compétence avant son déploiement furtif. Intègre SkillOpt (Bounded Updates, Validation Gate, Rejected-Edit Buffer, Slow Update) et Book-to-Skill (Plafond 800 lignes, Routeur)."
---

# Tesla-Writing-Skills : Stratégie Exécutive pour Compétences Auto-Évolutives

> 🔒 **LA LOI DE FER (IRON LAW)**
> **NO SKILL UPDATE WITHOUT A VALIDATED ROLLOUT FIRST.**
> Il est strictement interdit de créer ou modifier une compétence sans un test de validation préalable (TDD).

> 🔒 **DOCTRINE HIBRIDE — Vigilum Codex.** 
> Ce document est la fusion absolue de **Tesla-Writing-Skills** (TDD appliqué à la documentation), du protocole **Shadow-Targeting** (injection furtive dans les subagents Antigravity CLI), de l'architecture **Book-to-Skill** (lazy loading) et de **SkillOpt** (optimisation textuelle systématique et bornée). Il traite le document de compétence comme l'état externe entraînable d'un agent figé.

---

## 1. Vue d'ensemble

**Écrire des compétences, C'EST du Test-Driven Development.** SkillOpt prolonge cette philosophie en traitant la compétence elle-même comme un **état externe optimisable** — et non comme un document statique. Au lieu d'une réécriture inconditionnelle, nous appliquons une boucle d'optimisation textuelle stricte analogue à l'entraînement des poids d'un modèle :

| Analogie Deep-Learning | Forme Opérationnelle SkillOpt |
|---|---|
| **Espace des poids** | Document de compétence (`best_skill.md`) |
| **Données d'entraînement** | Rollout batch depuis `D_tr` |
| **Gradient / Optimizer** | Modèle Optimizer générant des éditions structurées |
| **Taille du pas (Step size)** | Budget d'édition textuelle `L_t` (Learning Rate) |
| **Validation** | Held-out selection gate `D_sel` (Amélioration stricte exigée) |
| **Feedback Négatif** | Rejected-edit buffer (`B_rejected`) |
| **Momentum / Meta-learning** | Epoch-wise slow/meta update (`<!-- SLOW_UPDATE_START -->`) |
| **Artefact de déploiement** | Document compact ou routé (Book-to-Skill) |

**Couche Shadow-Targeting :** La compétence optimisée est déployée par **injection furtive** dans un subagent natif d'Antigravity CLI (`target_subagent: self`). Cette injection requiert un circuit de rollback atomique obligatoire (désactivation sémantique → quarantaine physique → SQL atomique → re-sync).

---

## 2. Architecture de Routage : Book-to-Skill

Les outils de lecture de l'agent ont des limites de restitution (ex: 800 lignes par appel). Les compétences doivent donc adopter un paradigme de "Livre" divisé en chapitres et routé dynamiquement.

**Structure exigée pour les compétences > 800 lignes :**
```text
/my-skill/
  ├── SKILL.md (Routeur d'intentions)
  ├── glossary.md (Index absolu de routage)
  └── chapters/ (Fichiers < 800 lignes)
```

> [!IMPORTANT]
> **Règle des 800 Lignes (Plafond Dur)**
> Une compétence ou un chapitre ne DOIT JAMAIS excéder 800 lignes. Si dépassé, scindez en chapitres autonomes.

> [!TIP]
> **Overlap Pointers (Pointeurs de Chevauchement)**
> Chaque chapitre DOIT inclure un "Overlap Pointer" impératif à la fin.
> *Format exigé :* `[SUITE DANS : ./chapters/chapter_02.md - ACTION REQUISE : Utilisez view_file pour lire ce fichier. Objectif : XYZ]`

---

## 3. SkillOpt : L'Optimizer Textuel (Méthode)

### 3.1 Forward Pass : Preuve par Déploiement (Rollout)
À chaque étape d'optimisation, l'agent cible exécute un lot (batch) de tâches d'entraînement (`D_tr`) avec la compétence actuelle.
L'adaptateur enregistre : les métadonnées, messages, appels d'outils, et le résumé d'exécution compact (`subagent_trace_summary.txt`).

### 3.2 Backward Pass : Minibatch Reflection
Le modèle Optimizer (un agent d'élite) convertit les trajectoires en éditions structurées. Il sépare les échecs des succès et propose des patchs :
- `APPEND` : Ajouter une nouvelle règle procédurale.
- `INSERT` : Insérer dans une section spécifique.
- `REPLACE` : Modifier une instruction existante.
- `DELETE` : Supprimer une règle obsolète.

### 3.3 Mises à Jour Textuelles Bornées (Bounded Updates)
L'Optimizer ne réécrit **JAMAIS** le fichier entier. Il est contraint par un budget d'édition `L_t` (ex: max 4 éditions). Cela préserve la continuité et empêche l'effacement de règles utiles acquises précédemment.
- **Schedule par défaut :** `cosine` (commence large, décroît vers des consolidations mineures).

### 3.4 Porte de Validation (Selection Gate) et Buffer de Rejets
Chaque compétence candidate est évaluée sur un jeu de validation (`D_sel`).
- **Acceptation stricte :** Le score candidat DOIT être strictement supérieur au score actuel. Les égalités sont rejetées.
- **Rejected-Edit Buffer (`B_rejected`) :** Les éditions refusées sont consignées. Lors des prochaines itérations, l'Optimizer lit ce buffer pour ne pas répéter les mêmes erreurs (Feedback Négatif).

### 3.5 Epoch-Wise Slow / Meta Update
À la fin d'une époque (plusieurs itérations), une méta-analyse compare les performances globales. L'Optimizer rédige des directives stratégiques à long terme injectées dans une zone protégée de la compétence :
`<!-- SLOW_UPDATE_START -->` et `<!-- SLOW_UPDATE_END -->`.
Cette zone est intouchable par les itérations rapides.

---

## 4. Shadow-Targeting Renforcé

Toute injection dans un subagent natif (ex: `tesla-github-manager`) est un acte critique.

**Procédure de Retrait / Rollback (Obligatoire) :**
1. **Désactivation Sémantique :** Retirer la référence du `.agents/[SUBAGENT].md`.
2. **Quarantaine Physique :** Déplacer le dossier de la compétence.
3. **Mise à Jour SQL Atomique :**
   ```sql
   BEGIN TRANSACTION;
   UPDATE subagents_skills SET statut = 'inactive', notes = 'Rollback SkillOpt' 
   WHERE skill_name = '[NOM]' AND session_id = '[ID]';
   COMMIT;
   ```
4. **Re-synchronisation :** Lancer `update_session_history.py`.

---

## 5. Intégration TDD-SkillOpt (RED-GREEN-REFACTOR)

Le cycle de création TDD classique est maintenant propulsé par SkillOpt.

| Étape TDD | Forme Opérationnelle SkillOpt |
|---|---|
| **RED** | Lancer le *Rollout* sur `D_tr` sans la compétence. Documenter les échecs et rationalisations de base. |
| **GREEN** | Générer une mise à jour bornée (`L_t` = 4). Appliquer `APPEND/REPLACE/DELETE`. Produire `s_candidate` dans `.shadow/`. |
| **GATE (Test)**| Évaluer `s_candidate` sur `D_sel`. Accepter uniquement si le score s'améliore strictement. |
| **REFACTOR** | Identifier les nouvelles rationalisations. Ajouter des *Red Flags* et verrouiller via des éditions bornées. Re-tester. |
| **SLOW UPDATE**| À la fin du cycle, mettre à jour la balise `<!-- SLOW_UPDATE_START -->` avec le *Meta-Learning*. |

---

## 6. Lutter contre la Rationalisation (Blindage)

Associez la forme de la guidance au type de défaillance. Si l'agent saute une règle sous pression, une guidance molle ("préférez faire X") échouera.

**Table des Rationalisations Typiques :**

| Excuse de l'Agent | Contre-Mesure SkillOpt |
|---|---|
| "Le sommaire suffit." | Faux. Exiger `view_file` sur les chapitres (Overlap Pointer). |
| "Je vais tout réécrire d'un coup." | Interdit. Utiliser le budget d'édition textuelle `L_t`. |
| "Le score est égal, je valide." | Rejet. La porte de validation exige une amélioration stricte. |
| "C'est juste une modif." | Toute modification passe par le Rollout et le Validation Gate. |

---

## 7. Checklist de Création et de Déploiement

> 🔒 **OBLIGATOIRE POUR CHAQUE COMPÉTENCE.**

**1. RED (Preuve par Rollout) :**
- [ ] Exécuter le Target Agent sur `D_tr` SANS la compétence.
- [ ] Documenter les échecs et les rationalisations de l'agent.

**2. GREEN (Édition Bornée / Patch) :**
- [ ] `description` cible les symptômes (quand utiliser), pas le workflow.
- [ ] L'Optimizer propose max 4 éditions (Learning Rate respecté).
- [ ] Si > 800 lignes : Découper en chapitres (Book-to-Skill) avec `glossary.md`.

**3. GATE & REFACTOR (Validation) :**
- [ ] Tester `s_candidate` sur `D_sel`.
- [ ] Si échec : enregistrer dans `B_rejected` et annuler.
- [ ] Si succès : boucher les nouvelles failles identifiées.

**4. DÉPLOIEMENT (Shadow-Targeting) :**
- [ ] Mettre à jour `alexandria_brain.db` avec `injection_method = 'shadow-targeting'` et transaction SQL atomique prête pour le rollback.
- [ ] Re-synchroniser avec `update_session_history.py`.
