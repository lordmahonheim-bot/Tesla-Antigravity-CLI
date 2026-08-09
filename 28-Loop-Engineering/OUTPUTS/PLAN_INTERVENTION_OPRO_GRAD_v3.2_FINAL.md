# PLAN D'INTERVENTION DÉFINITIF : OPRO-GRAD v3.2 (AIP-5)
**Statut** : **APPROUVÉ POUR EXÉCUTION**  
**Version** : 3.2 (Raffinage Ultime Arcanis – 2026-07-24)  
**Auteur** : Tesla (Orchestrateur Suprême + Arcanis Audit)  
**Parent** : Chantier 32 – SELF-IMPROVING-AI (SIA-TESLA-H) [Phase 6]  
**Objectif** : Atteindre l'Autonomie d'Ingénierie Permanente de Niveau 5 (AIP-5) en transformant le système en compilateur agentique, avec une paranoïa sécuritaire absolue (Vigilum Codex).

---

## 1. VISION ÉPISTÉMOLOGIQUE & COMPOSANTS
Le système OPRO-Grad repose sur trois piliers complémentaires (et non séquentiels) :
1. **TextGrad (Sonde Locale) :** Génère un "Gradient Textuel" pour pointer la racine sémantique exacte d'une erreur locale.
2. **OPRO (Agrégateur Global) :** Utilise l'historique complet (Rejected-Edit Buffer) pour proposer des mutations globales du prompt.
3. **DSPy (Compilateur Arena) :** Structure l'évaluation mathématique des mutations proposées.

---

## 2. DIAGRAMME DU FLUX D'AUTO-ÉVOLUTION (OPRO-GRAD)

```mermaid
flowchart TD
    A[Détection: Erreur franche OU Dérive KPI silencieuse] --> B[Stade 1: TextGrad RCA<br/>tesla-premortem]
    B --> C[Gradient Textuel<br/>+ Rejected-Edit Buffer]
    C --> D[Stade 2: OPRO Optimizer<br/>tesla-opro-optimizer]
    D --> E[Batch 3 Patchs<br/>LR Textuel ≠ Token Budget]
    E --> F[Stade 3: DSPy Arena<br/>git worktree éphémère]
    F --> G[Fitness = f(Résolution, Tokens, Temps, Régression Latérale)]
    G --> H{Score > Seuil & Régression = 0 ?}
    H -->|NON| I[Ajout au Rejected-Edit Buffer]
    H -->|OUI| J[Stade 4: Gate Hiérarchisée]
    J -->|MINOR| K[Auto-Merge + Semantic GC]
    J -->|MAJOR / CRITICAL| L[Human-In-The-Loop: Lord Mahonheim]
    K --> M[CANONICAL SKILL.md]
    L --> M
```

---

## 3. SÉCURITÉ ABSOLUE : LE KILL-SWITCH GLOBAL
L'auto-évolution non bridée mène au drain de tokens. L'introduction de la **Règle 15** est actée : *Aucun agent ne peut modifier son propre circuit-breaker.*
Le Kill-Switch est matériel et à 3 niveaux :
1. **Rate Limit Local :** Max 5 déclenchements OPRO par heure.
2. **Token Breaker (Budget Global) :** Hard-cap de 500 000 tokens journaliers dédiés à OPRO. En cas de dépassement, pause et notification.
3. **Kill-Switch Physique :** Présence du fichier `/etc/tesla/HALT_OPRO` coupe tout (vérification toutes les 10s).

---

## 4. LE WORKFLOW (LES 5 STADES)

### Stade 0 : Détection & Télémétrie
* **Déclencheurs :** Erreurs franches (LSP, tests) **OU** dérive des KPIs (Fitness moyen EWMA en baisse de -15% sur 20 runs).

### Stade 1 : Capture Sémantique (TextGrad RCA)
* `tesla-premortem` génère un `textual_gradient.json` identifiant formellement l'étape fautive.
**Exemple de `textual_gradient.json` :**
```json
{
  "error_id": "LSP-042-2026-07-24",
  "failing_step": "Section 7.3 du SKILL.md",
  "gradient": "La règle de typage TypedDict est omise. Cela provoque l'ignorance de la contrainte 12.2.",
  "affected_modules": ["tesla-master-code", "validation"],
  "severity": "MEDIUM"
}
```

### Stade 2 : Optimiseur OPRO (`tesla-opro-optimizer`)
* **Paramètres désolidarisés :** 
  * *Learning Rate Textuel* (profondeur de modification, ex: 1 ligne vs section entière).
  * *Token Budget* (contrainte dure L1 anti-bloat).
* **Expiration du Buffer :** TTL de 90 jours ou 500 entrées maximum sur le *Rejected-Edit Buffer*.

### Stade 3 : Compilation Arena & Fitness
* Sandbox via `git worktree` (90% économie disque).
* **Fonction de Coût Mathématique Paramétrée :**
  `Fitness = 0.45·(Résolution) - 0.25·(Tokens) - 0.10·(Temps) - 10.0·(Régression Latérale)`
* *Contrainte dure :* Si la régression latérale > 0, le patch est détruit (poids massif de 10.0).

### Stade 4 : Validation Gate (Restauration Règle 14)
* **TRIVIAL/MINOR :** Auto-merge.
* **MAJOR/CRITICAL :** Validation HITL requise.

### Stade 5 : Consolidation & Semantic GC
* Compression pour forcer le `SKILL.md` à rester sous 150 lignes. Enregistrement dans `LESSONS_REGISTRY.md`.

---

## 5. ROADMAP D'IMPLÉMENTATION (ACTIONNABILE)

### Phase 6.1 – MVP Lean (Semaine 1, Effort estimé: 3j/homme)
*Stack frugale : mmdc, LanceDB, Tree-sitter Markdown (Zéro Playwright pour le moment).*
- [x] Création du script `mermaid_validator.sh` (Déjà fait en Nœud 2).
- [ ] Écriture des schémas JSON : `fitness_score.schema.json`, `kill_switch_state.schema.json`, `textual_gradient.schema.json` (Effort: 0.5j).
- [ ] Refonte de `tesla-writing-skills` en `tesla-opro-optimizer` avec séparation LR Textuel / Token Budget (Effort: 1.5j).
- [ ] Câblage du Kill-Switch à 3 niveaux (Effort: 1j).

### Phase 6.2 – Industrialisation de l'Arena (Semaine 2, Effort estimé: 4j/homme)
- [ ] Implémentation du `git worktree` runner pour l'Arena éphémère.
- [ ] Initialisation de LanceDB pour le *Rejected-Edit Buffer* avec politique TTL.
- [ ] Démon systemd `opro-grad-watcher.service`.

### Phase 6.3 – Déploiement Complet (Semaine 3)
- [ ] Mesure sur 10 tâches pilotes.
- [ ] Intégration de DSPy local (si justifié pour optimiser les signatures).

---

## 6. MÉTRIQUES, KPIs & RISQUES (Baseline Phase 4)

| KPI | Baseline Actuelle | Objectif OPRO-GRAD v3.2 | Outil de mesure |
|---|---|---|---|
| Erreurs LSP | -56% | -70% | `loop_trace.jsonl` |
| Token Overhead | +12% | < +8% | Arena Reports |
| Taux Acceptation Gate | 75% | ≥ 85% | Gate Logs |
| Taille SKILL.md | ≤ 142 lignes | ≤ 140 lignes | Tree-Sitter GC |

**Matrice des Risques Étendue (AMDEC) :**
| Risque | Mitigation | RPN |
|---|---|---|
| Drain Token Infini (Boucle) | Kill-Switch Global (500k/jour) | Faible (3) |
| Régression d'un autre agent | Paramètre `δ` massif (10.0) dans le Fitness | Faible (4) |
| Cimetière Sémantique | TTL du Buffer (90j / 500 max) | Très Faible (2) |
| Complexité cognitive accrue | Semantic GC obligatoire + Limite 150 lignes | Faible (4) |
| Dépendance au démon | Démarrage conditionnel + Fichier fallback | Moyen (6) |

---

## 7. LIVRABLES ATTENDUS
1. `schemas/textual_gradient.schema.json`
2. `schemas/fitness_score.schema.json`
3. `schemas/kill_switch_state.schema.json`
4. `tesla-opro-optimizer/SKILL.md` (v1 refondue)
5. `scripts/opro_kill_switch_monitor.sh`

---

## 8. MAPPING AUX CHANTIERS
* **Chantier 32 (SIA-TESLA-H) :** Parent direct (Phase 6).
* **Chantier 44 (SkillOpt) :** Refonte en `tesla-opro-optimizer`.
* **Chantier 28 (Loop Engineering) :** Base d'évaluation Arena.

---

## ANNEXE : RÉFÉRENCES SCIENTIFIQUES
* **OPRO :** Yang et al., *Large Language Models as Optimizers* (arXiv:2309.03409).
* **TextGrad :** Yuksekgonul et al., *TextGrad: Automatic "Differentiation" via Text* (arXiv:2406.07496).
* **DSPy :** Khattab et al., *DSPy: Compiling Declarative Language Model Calls* (Stanford NLP).
* **SkillOpt :** Microsoft Research (arXiv:2605.23904).
