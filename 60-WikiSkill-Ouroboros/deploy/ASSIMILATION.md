# ASSIMILATION — Ouroboros Auto-Capture (GEMINI.md R18)

> Zero-Friction Mapping for the Creuset (`$TESLA_ROOT`). This file is the
> assimilation artifact: apply it once, atomically, after double-copying the
> MVP scripts to `.agents/skills/tesla-wiki-manager/` (AGENTS.md §12).

## Classification (R18 surgical grid)

New **native execution tooling** (daemon + cycle + converter) under the existing
`tesla-wiki-manager` skill. Therefore:

- `AGENTS.md` delegation table: **no new row** (not a routable capability).
- `TESLA.json` `modules.registered`: **unchanged** (no new module).
- `settings.json` `permissions.scripts`: **whitelist the 3 entry points** below.
- `memory/*.md`: standard closure entries (project list + session log + state).

## Atomic patch (settings.json)

```bash
cp "$TESLA_ROOT/GENESE-v1/settings.json" "$TESLA_ROOT/GENESE-v1/settings.json.bak.$(date +%Y%m%dT%H%M%S)"
TESLA_ROOT="$TESLA_ROOT" python3 - <<'EOF'
import json, os
p = os.path.join(os.environ["TESLA_ROOT"], "GENESE-v1", "settings.json")
with open(p, encoding="utf-8") as fh:
    data = json.load(fh)
scripts = data.setdefault("permissions", {}).setdefault("scripts", {})
scripts[".agents/skills/tesla-wiki-manager/scripts/ouroboros_daemon"] = {
    "allowed": True,
    "arguments": ["once", "interval", "ingest-only", "cycle-only",
                  "backfill-days", "min-hits", "min-score", "no-commit"],
    "description": "Ouroboros Zero-Touch reconciler (ingest + cycle)"
}
scripts[".agents/skills/tesla-wiki-manager/scripts/ouroboros_cycle"] = {
    "allowed": True,
    "arguments": ["min-hits", "min-score", "no-commit", "max-attempts"],
    "description": "Ouroboros A-to-D engine (distill, forge, gate, commit local)"
}
scripts[".agents/skills/tesla-wiki-manager/scripts/ouroboros_autocapture"] = {
    "allowed": True,
    "arguments": ["receipt", "transcript", "conversation"],
    "description": "Receipt/transcript to sealed ExecutionTrace converter"
}
with open(p, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print("settings.json patched:", len(scripts), "scripts whitelisted")
EOF
python3 -c "import json; json.load(open('$TESLA_ROOT/GENESE-v1/settings.json'))" && echo "JSON valid"
```

## Verification (Creuset)

```bash
# 1. Double-copy check (AGENTS.md §12)
diff -q 60-WikiSkill-Ouroboros/scripts/ouroboros_cycle.py \
  .agents/skills/tesla-wiki-manager/scripts/ouroboros_cycle.py && echo "SYNC OK"
# 2. One-shot backfill (captures this morning's missions retroactively)
TESLA_ROOT="$TESLA_ROOT" python3 .agents/skills/tesla-wiki-manager/scripts/ouroboros_daemon.py --once
# 3. Persistent service
TESLA_ROOT="$TESLA_ROOT" bash 60-WikiSkill-Ouroboros/deploy/install.sh --interval 60
# 4. Traces flow without the orchestrator
ls .agents/traces/*.json | wc -l
```

Rollback: restore the `.bak.*` settings file, run `install.sh --uninstall`.
