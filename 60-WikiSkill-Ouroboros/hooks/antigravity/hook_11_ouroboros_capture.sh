#!/usr/bin/env bash
# Hook 11 — Ouroboros Auto-Capture (couche immediate, best-effort) V2.1
#
# Role : a la fin d'une execution de sous-agent (payload post-outil contenant
# un resultat), deposer un recu JSON dans runtime/ouroboros/inbox/ pour
# ingestion deterministe par ouroboros_daemon.py (Phase A, sans LLM).
#
# FIX V2.1 — CECITE LINGUISTIQUE :
#   - Ancienne version ne detectait que SUCCESS/PARTIAL/FAILURE/FAILED/ERROR
#     en anglais strict -> missions francophones "Mission accomplie avec succes"
#     ignorees silencieusement (inbox=0, scan=0).
#   - Nouvelle version : STATUS_MAP multilingue EN+FR avec normalisation sans accents.
#   - Detection is_subagent elargie : tesla-, github-manager, mission, etc.
#   - Capture meme sans statut explicite si skill connu + texte substantiel
#     (score 0.0 = unknown, jamais d'inference de succes).
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
import json, os, sys, uuid, re, unicodedata

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

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize(s: str) -> str:
    return strip_accents(s).upper()

tool_name = str(dig(payload, "toolCall", "name") or dig(payload, "tool", "name") or dig(payload, "name") or "")
raw_lower = raw.lower()
raw_norm = normalize(raw)

# Detection elargie is_subagent (V2.1)
is_subagent = False
if "subagent" in tool_name.lower() or "subagent" in raw_lower[:3000]:
    is_subagent = True
if "tesla-" in raw_lower[:5000]:
    is_subagent = True
if "github-manager" in raw_lower or "github_manager" in raw_lower:
    is_subagent = True
if "task_id" in raw_lower and ("mission" in raw_lower or "task" in raw_lower):
    is_subagent = True

# Champs resultat possibles (protocole tolerant : pre- et post-outil, EN+FR)
result_text = ""
candidates_keys = (
    ("toolCall", "args", "Result"),
    ("toolCall", "args", "result"),
    ("toolCall", "args", "report"),
    ("toolCall", "args", "output"),
    ("toolCall", "args", "final_answer"),
    ("toolCall", "args", "finalAnswer"),
    ("toolCall", "args", "answer"),
    ("toolCall", "args", "response"),
    ("toolResult", "output"),
    ("toolResult", "result"),
    ("toolResult", "final_answer"),
    ("toolResult", "report"),
    ("result",),
    ("report",),
    ("final_answer",),
    ("finalAnswer",),
    ("answer",),
    ("response",),
    ("observation",),
    ("summary",),
    ("output",),
    ("content",),
    ("text",),
)
for path in candidates_keys:
    cand = dig(payload, *path)
    if isinstance(cand, str) and cand.strip():
        result_text = cand
        break
    if isinstance(cand, dict):
        # Cherche sous-champs texte dans dict
        for subk in ("content", "text", "output", "result", "final_answer", "answer", "report"):
            sv = cand.get(subk)
            if isinstance(sv, str) and sv.strip():
                result_text = sv
                break
        if result_text:
            break
        try:
            result_text = json.dumps(cand)[:8000]
            if len(result_text.strip()) >= 50:
                break
        except Exception:
            pass
    if isinstance(cand, list):
        # Concatene les strings de la liste
        texts = []
        for item in cand:
            if isinstance(item, str) and item.strip():
                texts.append(item)
            elif isinstance(item, dict):
                for subk in ("content", "text", "output", "result"):
                    sv = item.get(subk)
                    if isinstance(sv, str) and sv.strip():
                        texts.append(sv)
                        break
        if texts:
            result_text = "\n".join(texts)[:8000]
            break

if not result_text or len(result_text.strip()) < 20:
    sys.exit(0)

# Si pas detecte comme subagent mais texte substantiel avec skill connu, on capture quand meme (voie defensive)
if not is_subagent:
    if len(result_text) >= 80 and ("tesla-" in result_text.lower() or "mission accomplie" in result_text.lower() or "mission" in result_text.lower()[:500]):
        is_subagent = True
    else:
        sys.exit(0)

skill = (
    dig(payload, "toolCall", "args", "agentName")
    or dig(payload, "toolCall", "args", "agent")
    or dig(payload, "toolCall", "args", "skill")
    or dig(payload, "agentName")
    or dig(payload, "agent")
    or dig(payload, "skill")
    or "unknown"
)
# Heuristique skill depuis result_text si unknown
if skill == "unknown":
    low = result_text.lower()
    if "github-manager" in low or ("github" in low and "manager" in low):
        skill = "tesla-github-manager"
    elif "web-raider" in low:
        skill = "tesla-web-raider"
    elif "master-code" in low:
        skill = "tesla-master-code"
    elif "team-synergy" in low:
        skill = "tesla-team-synergy"

conv = str(payload.get("conversationId", payload.get("conversation_id", "hook")))
step = payload.get("step_index", payload.get("stepIndex", payload.get("step", "hook")))

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

# Statut explicite multilingue EN+FR avec normalisation sans accents (V2.1 FIX)
STATUS_MAP_V21 = [
    # SUCCESS FR+EN - phrases specifiques d'abord
    ("MISSION ACCOMPLIE", "success", 1.0),
    ("MISSIONS ACCOMPLIES", "success", 1.0),
    ("100% SUCCES", "success", 1.0),
    ("100% SUCCESS", "success", 1.0),
    ("SUCCES TOTAL", "success", 1.0),
    ("SUCCES", "success", 1.0),
    ("SUCCESS", "success", 1.0),
    ("REUSSITE", "success", 1.0),
    ("REUSSI", "success", 1.0),
    ("ACCOMPLIE", "success", 1.0),
    ("ACCOMPLI", "success", 1.0),
    ("ACHEVEE", "success", 1.0),
    ("ACHEVE", "success", 1.0),
    ("TERMINEE", "success", 1.0),
    ("TERMINE", "success", 1.0),
    ("COMPLETEE", "success", 1.0),
    ("COMPLETE", "success", 1.0),
    ("COMPLETED", "success", 1.0),
    ("VALIDEE", "success", 1.0),
    ("DONE", "success", 1.0),
    # PARTIAL
    ("PARTIELLEMENT", "partial", 0.5),
    ("PARTIELLE", "partial", 0.5),
    ("PARTIEL", "partial", 0.5),
    ("PARTIAL", "partial", 0.5),
    ("INCOMPLETE", "partial", 0.5),
    ("INCOMPLET", "partial", 0.5),
    # FAILURE FR+EN
    ("ECHEC CRITIQUE", "failure", 0.0),
    ("ECHEC", "failure", 0.0),
    ("ECHOUEE", "failure", 0.0),
    ("ECHOUE", "failure", 0.0),
    ("ERREURS", "failure", 0.0),
    ("ERREUR", "failure", 0.0),
    ("FAILURE", "failure", 0.0),
    ("FAILED", "failure", 0.0),
    ("FAIL", "failure", 0.0),
    ("ERROR", "failure", 0.0),
]

norm_text = normalize(result_text)
for kw, outcome, score in STATUS_MAP_V21:
    kw_norm = normalize(kw)
    if " " in kw_norm:
        if kw_norm in norm_text:
            receipt["outcome"] = outcome
            receipt["score"] = score
            receipt["verdict_sources"].append(f"marker:{kw_norm}")
            break
    else:
        if re.search(rf"\b{re.escape(kw_norm)}\b", norm_text):
            receipt["outcome"] = outcome
            receipt["score"] = score
            receipt["verdict_sources"].append(f"marker:{kw_norm}")
            break

# Checkpoint Contract governance (Option B) : si present, on force outcome success si pas deja failure
if "[CHECKPOINT" in result_text.upper() or "[CONTRAT" in result_text.upper() or "POINT DE CONTROLE" in result_text.upper():
    if receipt["outcome"] == "unknown":
        # On ne devine pas le succes, mais on marque la presence du contrat
        receipt["verdict_sources"].append("marker:CHECKPOINT_CONTRACT")
        # Si le contrat contient explicitement status SUCCESS en FR/EN, deja capture ci-dessus
        # Sinon on laisse unknown (score 0) mais on capture quand meme (evite 0 trace)

name = f"hook11_{uuid.uuid4().hex[:12]}.json"
tmp = os.path.join(inbox, f".tmp_{name}")
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, ensure_ascii=False)
os.replace(tmp, os.path.join(inbox, name))
PYEOF

allow
