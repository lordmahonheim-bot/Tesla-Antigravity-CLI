# Plan d'Implémentation et de Déploiement : Boucle Shadow SkillOpt TDD

## [Goal Description]
L'objectif est d'intégrer formellement la méthodologie de pointe **SkillOpt** (optimisation exécutive des compétences des agents en espace textuel) au sein de la méta-compétence `tesla-writing-skills`. Actuellement, la création de compétences repose sur un cycle TDD manuel (RED/GREEN/REFACTOR). La boucle **Shadow SkillOpt TDD** algorithmatisera ce processus en introduisant une séparation stricte des rôles (Target vs Optimizer), des mises à jour bornées (Bounded Updates), une porte de validation intransigeante (Selection Gate), un registre des échecs (Rejected-Edit Buffer) et une mise à jour stratégique à long terme (Slow/Meta Update). Cela garantit un apprentissage stable et cumulatif des compétences, sans dérive ni "sur-distillation".

## User Review Required
> [!IMPORTANT]
> **Validation du Paradigme d'Édition Atomique** : L'approche SkillOpt interdit la réécriture complète d'un `SKILL.md` par l'agent Optimizer pour préserver la stabilité. Seules les opérations `append`, `insert_after`, `replace`, et `delete` sont autorisées avec un "budget" d'éditions strict. Êtes-vous d'accord pour imposer ce budget rigide (ex: max 4 éditions par cycle) ?

> [!WARNING]
> **Section Protégée (Slow Update)** : Le plan inclut l'ajout de balises `<!-- SLOW_UPDATE_START -->` et `<!-- SLOW_UPDATE_END -->` dans les compétences générées. Cette section sera sacrée et immuable par la boucle rapide. Validez-vous ce formatage HTML dans le Markdown ?

## Open Questions
1. Faut-il définir une arborescence standard pour le dossier `.shadow/` (ex: `.shadow/candidate_skill.md`, `.shadow/rejected_edits.json`) directement dans `tesla-writing-skills` ?
2. Le "budget" d'édition textuelle (Textual Learning Rate) doit-il être codé en dur (ex: 4 edits max) ou laissé à l'appréciation du *Target Agent* ?

---

## Proposed Changes

### `tesla-writing-skills/SKILL.md`
Nous allons refondre le document pour transformer le TDD manuel en un pipeline de machine learning textuel (SkillOpt).

#### [MODIFY] `SKILL.md`

1. **Refonte de la section "Quick Reference"** :
   Intégration du vocabulaire SkillOpt.
   ```diff
   - - **RED** : Écrire un test qui échoue pour exposer la défaillance.
   - - **GREEN** : Implémenter la solution minimale requise pour faire passer le test.
   - - **REFACTOR** : Boucher les rationalisations du LLM et optimiser.
   + - **Rollout (Train)** : Lancer le Target Agent sur des tâches pour collecter les échecs.
   + - **Minibatch Reflection (Optimizer)** : Analyser les échecs et proposer un budget borné d'éditions (Patch).
   + - **Validation Gate (Test)** : Déployer le patch dans `.shadow/` et le tester sur un jeu de validation. Acceptation stricte si amélioration.
   + - **Rejected Buffer** : Enregistrer les patchs refusés comme feedback négatif.
   ```

2. **Nouvelle Section : La Boucle Shadow SkillOpt TDD** (Remplace "Cartographie TDD pour compétences") :
   ```markdown
   ## La Boucle Shadow SkillOpt TDD (Algorithme)

   L'optimisation des compétences ne s'appuie plus sur des réécritures complètes aveugles. Elle suit une boucle d'optimisation textuelle stricte :

   1. **Séparation des Rôles** : Le *Target Agent* exécute la tâche avec la compétence actuelle. L'*Optimizer Agent* (souvent un agent d'élite ou vous-même) analyse les résultats hors-ligne.
   2. **Preuve par Déploiement (Rollout)** : Exécutez la compétence sur un jeu de tâches d'entraînement. Regroupez les succès et les échecs.
   3. **Mises à Jour Textuelles Bornées (Bounded Updates)** : L'Optimizer ne réécrit **JAMAIS** le fichier entier. Il propose un nombre strict d'éditions atomiques (`append`, `insert_after`, `replace`, `delete`). Le budget d'édition fait office de "Learning Rate" textuel.
   4. **Porte de Validation (Selection Gate)** : La compétence modifiée est générée dans le dossier `.shadow/`. Elle est testée sur un jeu de validation *différent*. L'édition est acceptée **UNIQUEMENT** si le score s'améliore strictement.
   5. **Buffer de Rejets (Rejected-Edit Buffer)** : Les éditions qui échouent la porte de validation sont consignées. Elles servent de feedback négatif pour les prochaines itérations de l'Optimizer afin de ne pas répéter les mêmes erreurs.
   6. **Mise à Jour Stratégique (Slow/Meta Update)** : Après plusieurs cycles, une méta-analyse est effectuée. Les conclusions stratégiques à long terme sont écrites à la fin de la compétence entre les balises `<!-- SLOW_UPDATE_START -->` et `<!-- SLOW_UPDATE_END -->`. **Cette section est en lecture seule pour la boucle rapide.**
   ```

3. **Mise à jour de la "Checklist de création"** :
   ```diff
   - **RED — Test qui échoue :**
   - - [ ] Scénarios de pression (3+ pressions combinées pour skills de discipline)
   + **1. Rollout & Reflection (Train) :**
   + - [ ] Exécuter le Target Agent sur des scénarios de pression.
   + - [ ] Extraire les patterns de défaillance récurrents.
   
   - **GREEN — Compétence minimale :**
   + **2. Bounded Edits & Shadowing (Patch) :**
   + - [ ] Proposer des éditions atomiques (max 4) ciblant la défaillance.
   + - [ ] Générer la compétence candidate dans `.shadow/`.
   
   - **REFACTOR — Boucher les failles :**
   + **3. Validation Gate & Buffer (Test) :**
   + - [ ] Tester le candidat sur un jeu de tâches de validation (indépendant).
   + - [ ] Succès = Déploiement. Échec = Ajout au Rejected-Edit Buffer et annulation.
   
   + **4. Slow Update (Optionnel) :**
   + - [ ] Mettre à jour la balise `<!-- SLOW_UPDATE_START -->` avec les stratégies de long terme.
   ```

---

## Verification Plan

### Automated Tests
1. Vérification syntaxique du Markdown mis à jour avec `lsp_diagnostics` (si applicable).
2. Simulation d'un cycle complet avec `tesla-github-manager` pour s'assurer qu'il comprend les balises `SLOW_UPDATE` et le format d'édition atomique.

### Manual Verification
1. Lord Mahonheim vérifiera la clarté et l'actionnabilité (Règle 14) de la nouvelle section "Boucle Shadow SkillOpt TDD" au sein de `SKILL.md`.
2. Lord Mahonheim validera que les instructions empêchent effectivement les LLMs de réécrire l'intégralité d'un fichier (sur-distillation) au profit de modifications ciblées.
