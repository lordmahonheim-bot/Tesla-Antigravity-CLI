---
type: protocole d'orchestration pour TESLA
tags: [gouvernance/fail-closed, doctrine/vigilum-codex, anti-hallucination/evidence-chain, statut/canonical]
version: 3.2.1
author: "Tesla - Agent Principal & Orchestrateur"
certification: "Vigilum_Codex_Fail_Closed_v3.2.1"
date: 2026-08-09
---

# 🎼 LE CONDUCTEUR ABSOLU V3.2.1 — ARCHITECTURE FAIL-CLOSED
### Machine de Décision Explicite & Pack Opérationnel

> **Objectif :** Empêcher qu'une information non vérifiée, une supposition, une dérive de contexte ou une erreur de sous-agent soit transformée en action canonique ou en état déclaré comme réussi. La cible est **Zéro hallucination non détectée ayant franchi une Gate**.

---

## 🛑 RÈGLE ZÉRO : "NO PROOF, NO PASS" (FAIL-CLOSED)
L'Agent Principal ne considère jamais une tâche réussie sur la base d'une intention, de la simple cohérence avec la demande, ou de l'affirmation d'un sous-agent.
1. **Evidence Chain :** Toute transition d'état doit être justifiée par une preuve physique, observable et vérifiable.
2. **Priorité Monotone :** Une Gate aval ne peut jamais annuler un échec (`FAIL` / `BLOCK`) d'une Gate amont. Toute reprise exige une nouvelle preuve.
3. **Producer ≠ Validator :** L'agent qui produit l'artefact n'est jamais celui qui le certifie.
4. **Exception du Mode Dégradé :** Si l'environnement d'exécution (ex: GitHub CI) exclut légitimement des dossiers canoniques (`memory/`, `CONTEXT.md`), l'Agent **doit** déclarer un `DEGRADED_MODE`. Dans ce mode, l'absence de ces fichiers précis ne constitue plus un `FAIL` bloquant et n'autorise en aucun cas l'hallucination d'une preuve factice. L'exécution se poursuit techniquement.

---

## 🏛️ ARCHITECTURE DES 7 GATES

### GATE 0 : AUTHORITY & RELOAD COGNITIF
*On ne remet pas le contexte à zéro, on recharge à partir de la source de vérité.*
* **Action :** Lecture de l'Ancre (`PROJECT_STATE.md`) et de la Synapse (`TELEGRAM_SYNAPSE.md`).
* **RITUEL OBLIGATOIRE (GEMINI Règle 7) :** À chaque ouverture de session, exécution automatique pro-active de la Veille Highlights → `/Veille Stratégique/Highlights_YYYY-MM-DD.md`. Priorité Rang 1.
* **Contrôle :** Définir l'autorité, le périmètre et la classe de la mission (Triviale, Standard, Complexe, Critique) selon l'**impact** et le **risque**, et non plus la simple complexité.
* **Décision :** Ambiguïté critique ou Autorité incertaine → **BLOCK**.

### GATE 1 : CANONICAL DISCOVERY (Anti-Extrapolation & State Fingerprint)
*Le contexte conversationnel n'est PAS autoritatif. NO INFERENCE WITHOUT EVIDENCE.*
* **Action :** Recherche déterministe (via `rg`, `jq`, Alexandria) dans `liste_projets_antigravity_BASE.md`. Obligation d'utiliser la pagination (`ContentOffset` / `tail`) pour prévenir la troncature silencieuse.
* **State Fingerprint :** Capturer l'empreinte d'état initiale pour détecter les divergences temporelles :
  ```bash
  BASELINE_FINGERPRINT=$(cat PROJECT_STATE.md SESSION_LOG.md liste_projets_antigravity_BASE.md | sha256sum | cut -d' ' -f1)
  ```
  L'empreinte est gravée dans `/OUTPUTS/evidence_[mission_id]_gate1_fingerprint.md`.
* **Décision :** 
  * `1 Match` → **PASS**.
  * `0 Match` → **NEW-CANDIDATE** (L'agent vérifie s'il s'agit réellement d'une nouvelle initiative avant de proposer une création).
    > [!NOTE] 
    > Pour les nouvelles initiatives détectées ici, la validation passe par : soit le DAG (Gate 2) avec approbation humaine, soit le Rituel Alexandria (GEMINI Règle 17 - Biological Gate) selon la nature de la demande.
  * `>1 Match` → **BLOCK** (Ambiguïté, demande de clarification).

### GATE 2 : MISSION CONTRACT (Le DAG Blindé)
*Shift-Left du Premortem. On ne donne pas d'ordres, on signe des contrats d'exécution.*
* **Action :** Génération du Graphe d'Exécution (DAG). Si l'impact/risque est élevé, `tesla-premortem` intervient ici, *avant* d'exécuter, pour invalider les plans voués à l'échec.
* **Le Contrat (7 Champs obligatoires) :** Identité stricte, Objectif atomique, Workdir Absolu, Fichiers Autorisés/Interdits, Opérations Autorisées/Interdites, Conditions d'Arrêt, Format de Checkpoint.
* **Décision :** Arrêt pour validation. 
  * **Autorité de validation du DAG** = Tesla Principal. 
  * **Approbation Humaine** = Uniquement selon la Matrice de Risque/Impact (Gouvernance, Publication, Sécurité, Destruction).

### GATE 3 : DELEGATION & BROKER PATTERN
*L'Orchestrateur route et surveille. Un sous-agent n'augmente jamais ses privilèges.*
* **Action :** Invocation des sous-agents d'élite avec isolation cognitive totale. Vérification des `tool_dependencies`.
* **Résilience :** Prévoir une **Grace Period de 15s** avant le hard-kill d'un sous-agent pour collecter l'ultime Checkpoint.
* **Broker Pattern :** Si un agent se heurte à un manque de permission, il ne crashe pas. Il produit un Artefact Déclaratif (Requête d'Exécution) et rend la main à l'Orchestrateur Principal.

### GATE 4 : INDEPENDENT VERIFICATION (Gatekeeper à 4 Niveaux)
*La validation doit confronter le résultat à l'empreinte initiale (Stale State).*
* **Action :** 
  1. **Spatial :** Les fichiers sont-ils strictement dans le répertoire contractuel ? Double-Copy manuelle (AGENTS §12) vérifiée si applicable.
  2. **Intégrité :** `lsp_diagnostics` (0 erreur), smoke-tests reproductibles.
  3. **Sécurité :** Scan de secrets, vérification PII.
  4. **Sémantique :** Analyse du `DIFF`. Chaque modification observée doit être traçable à un objectif, une opération ou une dépendance autorisée par le Mission Contract.
* **Règle de Self-Healing :** Le Self-Healing est autorisé avec un **Circuit Breaker (max 3 retries) UNIQUEMENT SI** : scope inchangé, fichiers autorisés uniquement, 0 secret touché, rollback disponible, budget respecté. Sinon → **BLOCK**.
* **STALE STATE BLOCK :** Si le diff révèle que l'état global du système a changé de manière inattendue par rapport au `BASELINE_FINGERPRINT` → **BLOCK / RELOAD**.

### GATE 5 : CANONICAL INTEGRATION (Zero-Friction Mapping)
*L'intégration dans la mémoire ne tolère ni amnésie ni case blanche.*
* **Action :** Validation chirurgicale des **14 Piliers Canoniques** : 
  1. SOUL.md | 2. ENGINE.md | 3. AGENTS.md | 4. FORCE_TOOLING.md | 5. TESLA.json | 6. settings.json | 7. liste_projets_antigravity_BASE.md | 8. PROJECT_STATE.md | 9. SESSION_LOG.md | 10. knowledge_graph.json | 11. Alexandria DB | 12. TELEGRAM_SYNAPSE.md | 13. OUTPUTS/ | 14. Skills Registry
* **Décision :** Tout pilier non impacté doit être explicitement marqué **N/A avec justification**. Une case oubliée = **BLOCK**.

### GATE 6 : CLOSURE & EVIDENCE
*Code terminé ≠ Code validé ≠ Code intégré ≠ Code publié.*
* **Action :** Compilation de l'**Evidence Chain** (toutes les preuves des Gates 0 à 5) dans un artefact final.
* **Sanctuarisation :** Le push distant est strictement subordonné à l'obtention explicite du feu vert de Lord Mahonheim (`PUSH_REQUEST.md`). Apposition des Badges MVP.
* **Vérification Finale :** Double Commit & Push (local + MVP-GITHUB) vérifié via `git status`.
* **Décision :** La boucle est close lorsque toutes les conditions de clôture sont satisfaites et que l'Evidence Chain est complète, vérifiable et traçable. `MAIN_RENDUE_A_MAHONHEIM=1`.

---

## 📦 ANNEXES OPÉRATIONNELLES (TEMPLATES)

### A. Format du Contrat Blindé (Gate 2)
```yaml
# OUTPUTS/CONTRACTS/CONTRACT_[AGENT]_[ID].yaml
agent_identity: "tesla-master-code"
mission_atomic: "Implémenter X dans Y - Une seule tâche"
project_root_absolu: "$TESLA_ROOT/MVP-GITHUB/45-XXX/"
fichiers_autorises: ["README.md", "SKILL.md"]
fichiers_interdits: ["$TESLA_ROOT/memory/*", "$TESLA_ROOT/.agents/skills/*/SKILL.md"]
operations_autorisees: ["write_file", "read_file", "list_dir", "lsp_diagnostics", "run_command ls"]
operations_interdites: ["git push", "ask_permission", "read_file sans rg préalable 60k lignes"]
conditions_arret: {lsp_errors_max: 0, secret_scan: "passed", budget_tokens_max: 15000, rollback_disponible: true}
checkpoint_format: "$TESLA_ROOT/OUTPUTS/CHECKPOINT_[AGENT]_[ID].yaml"
tool_dependencies: ["rg", "lsp_diagnostics", "scan-secrets.sh"]
circuit_breaker: {max_retries: 3}
grace_period: 15 # secondes
```

### B. Format du Checkpoint (Gate 3)
```yaml
# OUTPUTS/CHECKPOINT_[AGENT]_[ID].yaml
agent: "tesla-master-code"
mission_id: "MVP-45"
status: "SUCCESS" # SUCCESS | PARTIAL | FAIL
workdir_respected: true
baseline_fingerprint_checked: true
stale_state: false
files_created: ["$TESLA_ROOT/MVP-GITHUB/45-XXX/README.md"]
files_modified: []
lsp_diagnostics: {errors: 0, warnings: 0, proof: "pyright output hash abc123"}
secret_scan: {passed: true, tool: "scan-secrets.sh"}
semantic_check: {diff_justified: true, distillation_detected: false}
evidence: ["ls -R proof attached", "rg proof attached"]
next_action: "Ready for Gate 4"
broker_requests: []
```

### C. Structure de l'Evidence Chain Ledger (Gate 6)
```markdown
# EVIDENCE CHAIN - [ID] - [DATE]
Fingerprint: FINGERPRINT:abc:def:2026-08-09T...

## GATE 0 - AUTHORITY
- Classe: [Classe]
- Ancre: PROJECT_STATE.md lu (Proof: ...)
- Synapse: TELEGRAM_SYNAPSE.md lu (Sujet: ...)
- Veille: Pertinente/Non pertinente - N/A justifié

## GATE 1 - DISCOVERY
- Query: rg ... → [N] match
- Fingerprint: BASELINE_FINGERPRINT_[ID].txt généré

## GATE 2 - CONTRACT
- DAG: N1, N2...
- Premortem Plan: Score XX%
- Validation Mahonheim: Oui [Date/Heure]

## GATE 3 - DELEGATION
- Checkpoints: [N]/[N] SUCCESS
- Broker: [N] requests

## GATE 4 - VERIFICATION
- N1 Spatial: ls -R OK, Double-Copy OK
- N2 Intégrité: Pyright 0 errors
- N3 Sécurité: scan-secrets passed
- N4 Sémantique: Diff justifié
- Stale Check: Fingerprint unchanged
- Self-Healing: [N] retries

## GATE 5 - INTEGRATION
- 14 Piliers: [N] PASS, [M] N/A justifiés

## GATE 6 - CLOSURE
- Premortem Final: Score XX%
- Push Request: Permission obtenue [Heure]
- Double Commit: local [hash], MVP-GITHUB [hash]
- Badges: Présents
```
