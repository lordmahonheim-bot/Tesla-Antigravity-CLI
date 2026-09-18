#!/usr/bin/env bash
# Hook 11 — Ouroboros Auto-Capture (couche immediate, best-effort).
#
# Role : a la fin d'une execution de sous-agent (payload post-outil contenant
# un resultat), deposer un recu JSON dans runtime/ouroboros/inbox/ pour
# ingestion deterministe par ouroboros_daemon.py (Phase A, sans LLM).
#
# Garanties Vigilum :
#   - ne bloque JAMAIS la mission : sortie systematique {"decision":"allow"},
#     exit 0, toutes les erreurs sont avalees (|| true) ;
#   - fail-closed sur l'integrite : le recu est valide a l'ingestion, les
#     recus invalides partent en inbox_quarantine/ (jamais dans les traces).
#   - si le runtime n'emet que des payloads pre-outil (sans resultat), le hook
#     ne fait rien : le demon reconciliateur (scan transcripts) reste la voie
#     garantie.
set -u

allow() { echo '{"decision": "allow"}'; exit 0; }

PAYLOAD="$(cat || true)"
[ -z "$PAYLOAD" ] && allow

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MVP_DIR="$(cd "$HOOK_DIR/../.." && pwd)"

ROOT_DIR="${TESLA_ROOT:-$(git -C "$MVP_DIR" rev-parse --show-toplevel 2>/dev/null || true)}"
[ -z "${ROOT_DIR:-}" ] && allow
[ -d "$ROOT_DIR" ] || allow

INBOX="$ROOT_DIR/runtime/ouroboros/inbox"
mkdir -p "$INBOX" 2>/dev/null || allow

export OUROBOROS_PAYLOAD="$PAYLOAD"
export OUROBOROS_INBOX="$INBOX"

python3 - "$MVP_DIR" <<'PYEOF' 2>/dev/null || true
import json, os, sys, uuid

raw = os.environ.get("OUROBOROS_PAYLOAD", "")
inbox = os.environ.get("OUROBOROS_INBOX", "")
try:
    payload = json.loads(raw)
except Exception:
    sys.exit(0)  # payload non-JSON : rien a capturer
if not isinstance(payload, dict):
    sys.exit(0)

def dig(obj, *keys):
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return None
    return obj

tool_name = str(dig(payload, "toolCall", "name") or dig(payload, "tool", "name") or "")
is_subagent = ("subagent" in tool_name.lower()) or ("subagent" in raw.lower()[:2000])

# Champs resultat possibles (protocole tolerant : pre- et post-outil).
result_text = ""
for candidate in (
    dig(payload, "toolCall", "args", "Result"),
    dig(payload, "toolCall", "args", "result"),
    dig(payload, "toolCall", "args", "report"),
    dig(payload, "toolCall", "args", "output"),
    dig(payload, "toolResult", "output"),
    dig(payload, "toolResult", "result"),
    dig(payload, "result"),
    dig(payload, "report"),
):
    if isinstance(candidate, str) and candidate.strip():
        result_text = candidate
        break
    if isinstance(candidate, dict):
        try:
            result_text = json.dumps(candidate)[:8000]
            break
        except Exception:
            pass

if not is_subagent or not result_text:
    sys.exit(0)  # pre-outil ou outil non-sous-agent : voie demon garantie

skill = (
    dig(payload, "toolCall", "args", "agentName")
    or dig(payload, "toolCall", "args", "agent")
    or dig(payload, "agentName")
    or "unknown"
)
conv = str(payload.get("conversationId", "hook"))
step = payload.get("step_index", payload.get("stepIndex", "hook"))

receipt = {
    "skill": str(skill),
    "task_id": f"{conv}#{step}",
    "model": "antigravity-cli",
    "outcome": "unknown",
    "verdict_sources": [f"hook11:{conv}:{step}"],
    "steps": [{"index": 0, "type": "hook11-post-tool",
               "summary": result_text[:2000]}],
    "final_answer": result_text[:8000],
}
# Statut explicite uniquement (jamais d'inference).
upper = result_text.upper()
for kw, outcome, score in (("SUCCESS", "success", 1.0),
                           ("PARTIAL", "partial", 0.5),
                           ("FAILURE", "failure", 0.0),
                           ("FAILED", "failure", 0.0),
                           ("ERROR", "failure", 0.0)):
    if kw in upper:
        receipt["outcome"] = outcome
        receipt["score"] = score
        receipt["verdict_sources"].append(f"marker:{kw}")
        break

name = f"hook11_{uuid.uuid4().hex[:12]}.json"
tmp = os.path.join(inbox, f".tmp_{name}")
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh)
os.replace(tmp, os.path.join(inbox, name))
PYEOF

allow
