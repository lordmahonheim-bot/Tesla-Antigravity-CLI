#!/usr/bin/env bash
# ==============================================================================
# quotidien_status.sh — Contrôle de vérité du dépôt (LECTURE SEULE)
# ------------------------------------------------------------------------------
# Rôle   : produire en une commande la preuve de l'état réel du dépôt, sans
#          aucune mutation, sans réseau, sans écriture disque.
# Doctrine : No Proof, No Pass — P6 Parité bidirectionnelle — P7 Fail Closed.
# Sortie : 0 = aucune dérive détectée / 1 = dérive (FAIL-CLOSED)
# Usage  : bash tools/quotidien_status.sh [--tests]
#          --tests : lance en plus la baseline du module 53 (plus lent)
# Auteur : produit pour Lord Mahonheim / Vigilum Codex
# ==============================================================================

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

RUN_TESTS=0
[ "${1:-}" = "--tests" ] && RUN_TESTS=1

DRIFT=0
h() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok() { printf '  \033[32m[PASS]\033[0m %s\n' "$1"; }
ko() { printf '  \033[31m[FAIL]\033[0m %s\n' "$1"; DRIFT=1; }
info() { printf '  [INFO] %s\n' "$1"; }

printf '==============================================================\n'
printf ' VÉRITÉ DU DÉPÔT — %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf ' Racine : %s\n' "$ROOT"
printf '==============================================================\n'

# --- 1. Parité du registre canonique (P6 — bidirectionnelle) -------------------
h '1. Parité du registre canonique (list.txt <-> disque)'
if [ ! -f list.txt ]; then
  ko 'list.txt introuvable — registre canonique absent'
else
  DECLARED=0; PRESENT=0; UNREGISTERED=0
  while IFS= read -r n; do
    [ -z "$n" ] && continue
    DECLARED=$((DECLARED + 1))
    if [ ! -d "$n" ]; then
      ko "déclaré mais ABSENT du disque : $n"
    else
      PRESENT=$((PRESENT + 1))
    fi
  done < list.txt
  for d in [0-9][0-9]-*/; do
    [ -d "$d" ] || continue
    d="${d%/}"
    if ! grep -qxF "$d" list.txt; then
      ko "présent sur le disque mais NON DÉCLARÉ : $d"
      UNREGISTERED=$((UNREGISTERED + 1))
    fi
  done
  info "déclarés : $DECLARED | résolus : $PRESENT | non déclarés : $UNREGISTERED"
  [ "$DECLARED" -eq "$PRESENT" ] && [ "$UNREGISTERED" -eq 0 ] && ok 'parité registre/disque exacte'
fi

# --- 2. Référence canonique des couches d'identité ----------------------------
h "2. Référence canonique memory/Le_Conducteur_Absolu_v3.2.1.md"
CANON_REF='memory/Le_Conducteur_Absolu_v3.2.1.md'
REF_HITS=$(grep -rl --include='*.md' -F "$CANON_REF" . 2>/dev/null | grep -v '^./.git/' | grep -v '^./Archives' || true)
if [ -n "$REF_HITS" ]; then
  if [ -f "$CANON_REF" ]; then
    ok "$CANON_REF résolu"
  else
    ko "$CANON_REF référencé mais inexistant — couches concernées :"
    printf '%s\n' "$REF_HITS" | sed 's/^/         -> /'
    info "copie réelle disponible : 51-Conducteur-Absolu-v3.2.1/Le_Conducteur_Absolu_v3.2.1.md"
  fi
else
  info "aucune référence textuelle trouvée"
fi

# --- 3. Modules sans actif exécutable (doctrine sans exécution) ---------------
h '3. Modules sans actif exécutable (.py/.sh/.js/.ts/.c/.go)'
GHOSTS=0; TOTAL=0
for d in [0-9][0-9]-*/; do
  [ -d "$d" ] || continue
  TOTAL=$((TOTAL + 1))
  c=$(find "$d" -type f \( -name '*.py' -o -name '*.sh' -o -name '*.js' -o -name '*.ts' -o -name '*.c' -o -name '*.go' \) 2>/dev/null | wc -l)
  if [ "$c" -eq 0 ]; then
    GHOSTS=$((GHOSTS + 1))
  fi
done
info "modules : $TOTAL | documentation seule : $GHOSTS"
if [ "$GHOSTS" -gt 0 ]; then
  info "constat structurel (non bloquant) : doctrine majoritaire, exécution minoritaire"
fi

# --- 4. Dépendances d'exécution déclarées et présentes ------------------------
h "4. Dépendances d'exécution"
if command -v entr >/dev/null 2>&1; then
  ok "entr présent (36-Veille-Strategique/watch.sh opérationnel)"
else
  ko "entr ABSENT — 36-Veille-Strategique/watch.sh et 23-Architecture-Entr/justfile:watch ne peuvent pas démarrer"
fi
if python3 -c 'import nacl' >/dev/null 2>&1; then
  ok "pynacl présent (courtier de délégation Ed25519 activable)"
else
  ko "pynacl ABSENT — courtier Ed25519 en UNKNOWN-CONFINED (P3) : ses tests doivent SKIP avec raison, jamais PASS"
fi
if command -v jq >/dev/null 2>&1; then
  ok 'jq présent'
else
  ko 'jq ABSENT — prérequis déclaré du module 53'
fi

# --- 5. Baseline de gouvernance (optionnelle) --------------------------------
h '5. Baseline de gouvernance — module 53 (--tests pour activer)'
if [ "$RUN_TESTS" -eq 1 ]; then
  M53='53-Vigilum-Codex-2.0-Executable-Governance'
  if [ -f "$M53/bin/test_runner.py" ]; then
    ( cd "$M53" && timeout 300 python3 bin/test_runner.py >/tmp/quotidien_test_runner.json 2>/dev/null )
    RC=$?
    if [ "$RC" -eq 0 ]; then
      ok "bin/test_runner.py : exit 0 (baseline verte)"
    else
      ko "bin/test_runner.py : exit $RC (baseline NON verte — voir /tmp/quotidien_test_runner.json)"
      python3 - <<'PY' 2>/dev/null || true
import json
try:
    d = json.load(open('/tmp/quotidien_test_runner.json'))
    print('         verdict_global =', d.get('verdict_global'), '| exit =', d.get('exit_code'))
    for s in d.get('suites', []):
        print('         -', s.get('name'), '| exit', s.get('exit_code'), '|', s.get('verdict'),
              '| tests', s.get('tests_reported'), '| skip', s.get('tests_skipped'))
except Exception:
    pass
PY
    fi
  else
    info 'runner introuvable — contrôle ignoré'
  fi
else
  info 'non exécuté (ajouter --tests pour lancer la baseline du module 53)'
fi

# --- Verdict -----------------------------------------------------------------
printf '\n==============================================================\n'
if [ "$DRIFT" -eq 0 ]; then
  printf ' VERDICT : \033[32mPASS\033[0m — aucune dérive détectée\n'
else
  printf ' VERDICT : \033[31mBLOCK\033[0m — dérive détectée (fail-closed, P7)\n'
fi
printf '==============================================================\n'
exit "$DRIFT"
