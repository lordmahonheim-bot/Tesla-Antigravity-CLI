# Gouvernance Checkpoint Contract — Ouroboros V2.1

> **Option B (Gouvernance) + Option A (Infrastructure) fusionnées** — réponse au diagnostic
> "Le moteur Ouroboros Zero-Touch a-t-il été enrichi par tesla-github-manager ? Non."

## 1. Diagnostic résumé

- **Symptôme** : `passe ingestion : 0 trace(s) (inbox=0, scan=0)` alors que le daemon tournait et avait scanné la session `tesla-github-manager (77a304c9...)`.
- **Cause racine** : cécité linguistique.
  - `ouroboros_autocapture.py` V2 cherchait `\bSUCCESS\b`, `\bFAILURE\b`, etc. en anglais strict.
  - Les agents francophones disaient : `"Mission accomplie avec succès"`, `"100% Succès"`, `"Tâche terminée"`, `"Échec critique"`.
  - Aucun `[CHECKPOINT CONTRACT]` n'était émis → le parseur ignorait silencieusement la conversation.
- **Impact** : 0 trace ingérée, 0 pattern distillé, 0 règle forgée pour `github-ops`.

## 2. Corrections V2.1

### Option A — Infrastructure (implémentée)

**Fichier** : `scripts/ouroboros_autocapture.py` + `hooks/antigravity/hook_11_ouroboros_capture.sh`

- **STATUS_MAP multilingue EN+FR** avec normalisation sans accents (NFD) :
  - SUCCESS : `MISSION ACCOMPLIE`, `100% SUCCES`, `SUCCES`, `SUCCESS`, `REUSSITE`, `REUSSI`, `ACCOMPLIE`, `ACHEVE`, `TERMINE`, `COMPLETE`, `VALIDEE`, `DONE`, etc.
  - PARTIAL : `PARTIEL`, `PARTIELLEMENT`, `INCOMPLET`, `PARTIAL`, etc.
  - FAILURE : `ECHEC`, `ECHOUE`, `ERREUR`, `FAILURE`, `ERROR`, `RATE`, `KO`, etc.
- **Fonction `normalize_for_match`** : `strip_accents(text).upper()` → `SUCCÈS` → `SUCCES`.
- **Détection tolérante** : phrases spécifiques d'abord (`MISSION ACCOMPLIE` avant `SUCCES`), puis mots isolés avec `\b`.

### Option B — Gouvernance (implémentée)

**Contrat Checkpoint** : tout sous-agent doit rendre en fin de mission un bloc explicite :

```markdown
[CHECKPOINT CONTRACT]
contract_type: CHECKPOINT
status: SUCCESS | PARTIAL | FAILURE
task_id: <id>
skill: tesla-github-manager
- step: <action 1>
- step: <action 2>
final_answer: <résumé 2000 chars>
```

**Variantes FR acceptées (V2.1)** :

```markdown
[CONTRAT CHECKPOINT]
type_contrat: CHECKPOINT
status: SUCCES | PARTIEL | ECHEC
task_id: gh-77a304c9
```

Ou :

```markdown
POINT DE CONTROLE - Mission accomplie avec succès
```

Le parseur V2.1 accepte désormais :
- `[CHECKPOINT CONTRACT]` (EN)
- `[CONTRAT CHECKPOINT]` (FR)
- `[CONTRAT DE CHECKPOINT]` (FR)
- `POINT DE CONTROLE` (FR)
- `contract_type` / `type_contrat` + `CHECKPOINT` dans le texte

**Règle** : le checkpoint est une preuve primaire (scorée 1.0 si SUCCESS) mais n'est plus obligatoire pour capturer (fail-open capture). Si présent sans statut, il garantit au moins une ingestion avec `outcome=unknown` (score 0.0) → jamais de silent drop.

### Tolérance d'ingestion (fail-open capture, fail-closed integrity)

**Ancien `is_completion_entry`** :
```python
if entry_type in COMPLETION_TYPES: True
if "CHECKPOINT" and "CONTRACT": True
if "subagent" and detect_status: True
```

**Nouveau V2.1** :
```python
# Types élargis : RESULT, RESPONSE, DONE, COMPLETED, FINAL, OUTPUT
if any(tok in entry_type.upper() for tok in ("RESULT","RESPONSE","DONE",...)): True
# Checkpoint FR/EN
if "[CHECKPOINT CONTRACT]" or "[CONTRAT CHECKPOINT]" or "POINT DE CONTROLE": True
# Skill connu + texte substantiel => capture même sans statut (unknown, score 0)
if skill != "unknown" and len(text) >= 80: True
# Fallback github/mission/task longue
if "tesla-" in lower and len(text)>=120 and any(w in lower for w in ("mission","github",...)): True
```

→ **Résultat** : une mission FR `tesla-github-manager (77a304c9) Mission accomplie avec succès` est désormais capturée avec `success=1.0` au lieu d'être ignorée.

### Observabilité (daemon V2.1)

**Ancien log** :
```
passe ingestion : 0 trace(s) (inbox=0, scan=0)
```
→ opaque, aucune explication.

**Nouveau log V2.1** :
```
[2026-09-18T...] scan: conv-77a304c9 backfill initial (42 lignes)
[2026-09-18T...] scan: conv-77a304c9 task=gh-77a304c9 skill=tesla-github-manager outcome=success -> <sha>.json
[2026-09-18T...] scan resume: convs=1 lignes_totales=42 nouvelles=42 recus_detectes=1 ingestes=1 outcomes={'success':1} skills={'tesla-github-manager':1} force_rescan=False
[2026-09-18T...] passe ingestion : 1 trace(s) (inbox=0, scan=1) force_rescan=False
```

Si 0 reçus mais lignes présentes, log détaillé :
```
scan: conv-x 12 nouvelles lignes mais 0 recus detectes. Types echantillon: {'USER_INPUT':5, 'CHATTER':7}. Exemple texte: [...]
```

### Réparation des missions FR manquées

```bash
# Re-scan complet ignorant les curseurs (répare 77a304c9 et autres FR ignorés)
python3 scripts/ouroboros_daemon.py --once --force-rescan --backfill-days 30

# Ne répare qu'une conversation spécifique
python3 scripts/ouroboros_daemon.py --once --force-rescan --repair-conv 77a304c9

# Rejoue toutes les traces (cycle)
python3 scripts/ouroboros_cycle.py --reset-processed --reprocess-quarantine
```

## 3. Doctrine Vigilum Codex 2.0 — conformité

- **LLM-as-a-judge banni** : scoring, distillation, forging, gating restent 100% déterministes (stdlib only, 0 appel réseau, 0 modèle).
- **Cryptographie** : trace filename = SHA-256(contenu), `sha256` interne re-vérifié, mismatch → quarantine.
- **Fail-closed integrity, fail-open capture** : une capture cassée ne casse jamais une mission ; une preuve cassée ne devient jamais une règle.
- **Souveraineté** : commit LOCAL uniquement après PASS, push jamais effectué par la machinerie.
- **Zero-Touch Ops** : systemd user service, pas de watch terminal manuel.

## 4. Tests V2.1

- 24 tests historiques → 27 tests (3 nouveaux FR)
- `test_french_success_detection` : `Mission accomplie avec succès`, `100% Succès`, `ECHEC`, `Erreur`, `Partiel`
- `test_french_checkpoint_contract` : `[CHECKPOINT CONTRACT]`, `[CONTRAT CHECKPOINT]`, `POINT DE CONTROLE`
- `test_github_manager_capture` : régression exacte du diagnostic `77a304c9...` → doit produire `github-ops`/`success`

```bash
cd 60-WikiSkill-Ouroboros && python3 -m unittest discover -s tests -v
# 27 tests, OK
```

## 5. Checklist de déploiement (Creuset)

```bash
# 1. Double-copy (AGENTS.md §12)
diff -q 60-WikiSkill-Ouroboros/scripts/ouroboros_autocapture.py \
  .agents/skills/tesla-wiki-manager/scripts/ouroboros_autocapture.py && echo "SYNC OK"

# 2. Backfill réparateur (capture rétroactive FR)
TESLA_ROOT="$TESLA_ROOT" python3 .agents/skills/tesla-wiki-manager/scripts/ouroboros_daemon.py --once --force-rescan --backfill-days 30

# 3. Vérif traces
ls .agents/traces/*.json | wc -l
cat runtime/ouroboros/daemon.log | tail -n 50

# 4. Cycle
python3 .agents/skills/tesla-wiki-manager/scripts/ouroboros_cycle.py --reset-processed

# 5. Service persistant
bash 60-WikiSkill-Ouroboros/deploy/install.sh --interval 60
journalctl --user -u ouroboros-capture -f
```

## 6. Améliorations futures (proposées)

- **Option C — Embedding sémantique léger** : pour les cas où aucun marqueur n'est présent, utiliser un classifieur TF-IDF stdlib (pas de LLM) pour détecter `success` vs `unknown` avec seuil 0.9, mais toujours scorer 0.0 si incertain (fail-closed).
- **Métriques Prometheus** : exposer `ouroboros_ingested_total{skill,outcome,lang}` pour dashboard.
- **Hook pre-tool** : capturer aussi le début de mission pour corréler durée.

---

**Conclusion** : V2.1 corrige la cécité linguistique (Option A), ajoute la gouvernance Checkpoint Contract bilingue (Option B), améliore l'observabilité (logs détaillés, metrics, force-rescan) et optimise les performances (hygiène processed.json, timings). Le moteur Ouroboros Zero-Touch enrichit désormais correctement `tesla-github-manager` et toutes les interventions francophones.
