#!/usr/bin/env python3
"""Vigilum Codex 2.1.3 — Gate 2 Delegation Guard (verrou d'interception Gate 2).

Correctif exécutable de l'incident SPINOFF-DIAG-GATE2-BYPASS (2026-09-02,
19:14:36) : invocation de sous-agents sans validation humaine du Mission
Graph. Ce composant compose les mécanismes existants au lieu de les
réinventer (principe « AI Proposes, Code Validates ») :

  1. INTÉGRITÉ DU CONTENU (sceau, TAMPER_EVIDENT) — hérité :
     ``orchestration_gate.dag_verify`` garantit structure DAG (Kahn) +
     présence du sceau ``approval_sha256``. Le sceau est une empreinte
     d'intégrité : il DÉTECTE la falsification mais n'est pas une preuve
     d'identité de l'approbateur (n'importe qui peut recalculer un SHA-256).

  2. AUTORISATION HUMAINE (jeton, usage unique) — nouveau :
     ``gate2_approval.token``, jeton JSON signé HMAC-SHA256 avec un secret
     DÉTENU HORS DU WORKSPACE AGENT (``TESLA_GATE2_SECRET``, ``--secret-file``
     ou ``~/.tesla/gate2/secret.key`` mode 0600). Le jeton est lié
     cryptographiquement à (mission_id, graph_sha256, autorité, fenêtre de
     validité, nonce) — postulat P-AGENT-002 : un agent ne peut ni approuver
     son propre graphe, ni forger le jeton de sa propre exécution.

  3. ANTI-REJEU (A-003) : consommation atomique ``O_CREAT|O_EXCL`` du nonce
     dans un registre isolé (``runtime/gate2/nonces/``, arbitrage #2), puis
     enregistrement dans un grand livre d'échange chaîné par SHA-256
     (``runtime/gate2/redemptions.jsonl`` + ``chain_head.sha256``).

Correction clé vs spécification initiale du verrou 1 : ``pre-flight`` est une
vérification PURE (lecture seule, idempotente). La consommation du jeton est
une opération SÉPARÉE, explicite et atomique (``consume``), exécutée au moment
de la délégation réelle — un simple contrôle ne brûle plus l'autorisation.

Modèle de menace honnête (aucun masquage) : sur un hôte à UID partagé, un
agent malveillant disposant d'un accès shell peut lire le fichier de secret ;
la défense contre la dérive autonome / le momentum d'exécution / le rejeu est
déterministe et effective, mais l'isolation d'un agent réellement hostile
exige l'exécution du courtier de délégation sous un UID séparé (recommandation
consignée dans docs/RETEX_GATE2_BYPASS.md §7).

Sorties : 0 PASS | 1 BLOCKED | 64 USAGE | 66 UNKNOWN (P3 : UNKNOWN != PASS).
Aucun nouveau code numérique : les identifiants sémantiques ``GATE2_*``
sont portés par les verdicts JSON ; en contexte hook, BLOCKED est cartographié
sur les codes canoniques existants (81 TESLA_EXIT_ORCH, 70 TESLA_EXIT_PUSH).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Shim d'exécution : `python3 core/orchestration/gate2_guard.py` depuis
# n'importe quel CWD, avec imports de paquet résolus (conformité E4).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.orchestration.orchestration_gate import (  # noqa: E402
    EXIT_BLOCKED,
    EXIT_PASS,
    EXIT_UNKNOWN,
    EXIT_USAGE,
    compute_approval_sha256,
    dag_verify,
    load_graph_file,
    GraphError,
)

TOKEN_VERSION = "G2T-1"
DEFAULT_TTL_SECONDS = 900
TOKEN_FILE_NAME = "gate2_approval.token"
NONCES_DIR_NAME = "nonces"
LEDGER_NAME = "redemptions.jsonl"
CHAIN_HEAD_NAME = "chain_head.sha256"
GENESIS_HASH = "0" * 64
DEFAULT_SECRET_PATH = Path("~/.tesla/gate2/secret.key").expanduser()
SECRET_ENV_VAR = "TESLA_GATE2_SECRET"

# États du verrou de nonce (A-7) : RESERVED = spawn réservé mais non observé
# (crash possible entre RESERVE et OBSERVE — fail-closed, release manuel signé
# requis) ; tout autre état (ou verrou legacy illisible) = définitivement
# consommé. Un nonce terminal n'est JAMAIS réutilisable automatiquement.
LOCK_STATE_RESERVED = "RESERVED"
LOCK_STATE_CONSUMED = "CONSUMED"


# --------------------------------------------------------------------------- #
# Helpers temps / sérialisation                                               #
# --------------------------------------------------------------------------- #
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_iso(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    """Sérialisation canonique (RFC-8785-style, cohérente avec le dépôt)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- #
# Secret (détenu hors du périmètre d'écriture agent)                          #
# --------------------------------------------------------------------------- #
def resolve_secret(secret_file: str | None) -> tuple[bytes | None, str | None]:
    """Résout le secret HMAC. Retourne (secret, reason).

    Ordre : --secret-file > TESLA_GATE2_SECRET (env) > ~/.tesla/gate2/secret.key.
    Fail-closed : fichier de secret lisible par groupe/autres => refusé (P3).
    """
    if secret_file:
        path = Path(os.path.expanduser(secret_file))
        if not path.is_file():
            return None, "GATE2_SECRET_FILE_MISSING"
        mode = path.stat().st_mode & 0o077
        if mode:
            return None, "GATE2_SECRET_UNSAFE_PERMISSIONS"
        try:
            return path.read_bytes().strip(), None
        except OSError:
            return None, "GATE2_SECRET_UNREADABLE"
    env_secret = os.environ.get(SECRET_ENV_VAR)
    if env_secret:
        return env_secret.encode("utf-8"), None
    if DEFAULT_SECRET_PATH.is_file():
        mode = DEFAULT_SECRET_PATH.stat().st_mode & 0o077
        if mode:
            return None, "GATE2_SECRET_UNSAFE_PERMISSIONS"
        try:
            return DEFAULT_SECRET_PATH.read_bytes().strip(), None
        except OSError:
            return None, "GATE2_SECRET_UNREADABLE"
    return None, "GATE2_SECRET_UNAVAILABLE"


# --------------------------------------------------------------------------- #
# Jeton Gate 2 : charge utile, signature, vérification                        #
# --------------------------------------------------------------------------- #
def sign_token(payload: dict[str, Any], secret: bytes) -> str:
    return hmac.new(secret, canonical_bytes(payload), hashlib.sha256).hexdigest()


def verify_token_signature(token: dict[str, Any], secret: bytes) -> bool:
    supplied = token.get("hmac")
    if not isinstance(supplied, str) or not supplied:
        return False
    expected = sign_token({k: v for k, v in token.items() if k != "hmac"}, secret)
    return hmac.compare_digest(supplied, expected)


def _load_token_file(token_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not token_path.is_file():
        return None, "GATE2_TOKEN_MISSING"
    try:
        raw = json.loads(token_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "GATE2_TOKEN_MALFORMED"
    if not isinstance(raw, dict):
        return None, "GATE2_TOKEN_MALFORMED"
    return raw, None


def _check_binding(token: dict[str, Any], graph_sha256: str, mission_id: str,
                   now: datetime) -> str | None:
    """Vérifications de liaison pures. None == liaison valide."""
    if token.get("token_version") != TOKEN_VERSION:
        return "GATE2_TOKEN_VERSION_UNSUPPORTED"
    if not isinstance(token.get("authority"), str) or not token["authority"].strip():
        return "GATE2_TOKEN_AUTHORITY_MISSING"
    if not isinstance(token.get("nonce"), str) or not token["nonce"].strip():
        return "GATE2_TOKEN_NONCE_MISSING"
    if token.get("mission_id") != mission_id:
        return "GATE2_TOKEN_MISSION_MISMATCH"
    if token.get("graph_sha256") != graph_sha256:
        return "GATE2_TOKEN_GRAPH_MISMATCH"
    issued = _parse_iso(token.get("issued_at", ""))
    expires = _parse_iso(token.get("expires_at", ""))
    if issued is None or expires is None or not issued < expires:
        return "GATE2_TOKEN_WINDOW_INVALID"
    if now < issued:
        return "GATE2_TOKEN_NOT_YET_VALID"
    if now >= expires:
        return "GATE2_TOKEN_EXPIRED"
    return None


# --------------------------------------------------------------------------- #
# Registre de nonces consommés (arbitrage #2) & grand livre d'échange         #
# --------------------------------------------------------------------------- #
def nonces_dir(root: Path) -> Path:
    return root / "runtime" / "gate2" / NONCES_DIR_NAME


def nonce_lock_path(root: Path, nonce: str) -> Path:
    return nonces_dir(root) / f"{nonce}.lock"


def nonce_consumed(root: Path, nonce: str) -> bool:
    return nonce_lock_path(root, nonce).is_file()


def _lock_state(lock: Path) -> str:
    """État du verrou de nonce. Verrou legacy/inconnu => CONSUMED (fail-closed)."""
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return LOCK_STATE_CONSUMED
    state = data.get("state") if isinstance(data, dict) else None
    return state if isinstance(state, str) else LOCK_STATE_CONSUMED


def gate2_dir(root: Path) -> Path:
    return root / "runtime" / "gate2"


def _read_ledger(ledger_path: Path) -> tuple[list[dict[str, Any]], str | None]:
    """Lit le grand livre et vérifie la chaîne SHA-256. Retourne (entrées, reason)."""
    if not ledger_path.is_file():
        return [], None
    entries: list[dict[str, Any]] = []
    prev = GENESIS_HASH
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return [], "GATE2_LEDGER_UNREADABLE"
    for line in lines:
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return entries, "GATE2_LEDGER_CORRUPT"
        if not isinstance(entry, dict):
            return entries, "GATE2_LEDGER_CORRUPT"
        if entry.get("prev_hash") != prev:
            return entries, "GATE2_LEDGER_CHAIN_BROKEN"
        payload = {k: v for k, v in entry.items() if k != "entry_hash"}
        if entry.get("entry_hash") != _sha256_hex(canonical_bytes(payload)):
            return entries, "GATE2_LEDGER_CHAIN_BROKEN"
        prev = entry["entry_hash"]
        entries.append(entry)
    return entries, None


def _append_ledger(root: Path, record: dict[str, Any]) -> tuple[str | None, str | None]:
    """Ajoute une entrée chaînée au grand livre d'échange. Retourne (entry_hash, reason)."""
    gate2 = gate2_dir(root)
    gate2.mkdir(parents=True, exist_ok=True)
    ledger_path = gate2 / LEDGER_NAME
    entries, reason = _read_ledger(ledger_path)
    if reason is not None:
        return None, reason  # fail-closed : chaîne brisée => refus d'écrire
    prev = entries[-1]["entry_hash"] if entries else GENESIS_HASH
    entry = dict(record)
    entry["prev_hash"] = prev
    entry_hash = _sha256_hex(canonical_bytes({k: v for k, v in entry.items() if k != "entry_hash"}))
    entry["entry_hash"] = entry_hash
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    (gate2 / CHAIN_HEAD_NAME).write_text(entry_hash + "\n", encoding="utf-8")
    return entry_hash, None


# --------------------------------------------------------------------------- #
# Cérémonie humaine : émission du jeton (issue-token)                         #
# --------------------------------------------------------------------------- #
def issue_token(graph_path: Path, token_out: Path, mission_id: str, authority: str,
                secret: bytes, ttl_seconds: int = DEFAULT_TTL_SECONDS,
                issued_at: datetime | None = None) -> tuple[int, dict[str, Any]]:
    """Scelle la boucle d'approbation : un jeton ne peut être émis QUE pour un
    graphe structurellement valide ET déjà scellé, et SEULEMENT par un détenteur
    du secret humain (cérémonie Gate 2)."""
    if not authority or not authority.strip():
        # BYPASS-04 : aucun jeton n'est émis avec une autorité vide (P-AGENT-002).
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "GATE2_TOKEN_AUTHORITY_MISSING",
            "note": "Émission refusée : l'autorité émettrice est vide ou absente.",
        }

    code, dag = dag_verify(graph_path)
    if code != EXIT_PASS:
        return EXIT_BLOCKED, {
            "verdict": "BLOCKED",
            "reason": "GATE2_GRAPH_NOT_SEALABLE",
            "note": "Un jeton Gate 2 ne peut bénir un graphe invalide ou non scellé.",
            "dag": dag,
        }

    try:
        graph = load_graph_file(graph_path)
    except GraphError as exc:
        return EXIT_BLOCKED, {"verdict": "BLOCKED", "reason": str(exc)}

    issued = issued_at or _utc_now()
    expires = issued.timestamp() + max(int(ttl_seconds), 1)
    payload = {
        "token_version": TOKEN_VERSION,
        "mission_id": mission_id,
        "graph_sha256": compute_approval_sha256(graph),
        "authority": authority.strip(),
        "issued_at": _iso(issued),
        "expires_at": _iso(datetime.fromtimestamp(expires, tz=timezone.utc)),
        "nonce": secrets.token_hex(16),
    }
    token = dict(payload)
    token["hmac"] = sign_token(payload, secret)

    # Écriture atomique + permissions 0600 (le jeton est une autorisation).
    token_out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{token_out.name}.", dir=str(token_out.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(token, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, token_out)
    finally:
        if os.path.exists(tmp_name):
            try:
                os.unlink(tmp_name)
            except OSError:
                pass

    return EXIT_PASS, {
        "verdict": "PASS",
        "reason": "GATE2_TOKEN_ISSUED",
        "mission_id": mission_id,
        "authority": payload["authority"],
        "graph_sha256": payload["graph_sha256"],
        "issued_at": payload["issued_at"],
        "expires_at": payload["expires_at"],
        "ttl_seconds": max(int(ttl_seconds), 1),
        "token": str(token_out),
        "token_sha256": _sha256_hex(canonical_bytes(token)),
        "note": "Jeton éphémère à usage unique — présenter via pre-flight puis consume.",
    }


# --------------------------------------------------------------------------- #
# Pré-vol de délégation : vérification PURE (le cœur du verrou 1 corrigé)     #
# --------------------------------------------------------------------------- #
def pre_flight_delegation_check(graph_path: Path, token_path: Path, mission_id: str,
                                *, secret: bytes | None = None,
                                secret_reason: str | None = None,
                                now: datetime | None = None,
                                root: Path | None = None) -> tuple[int, dict[str, Any]]:
    """Vérification déterministe PRÉ-VOL, LECTURE SEULE et idempotente.

    Contrairement à la spécification initiale (verrou 1 du RETEX brut), cette
    fonction ne consomme AUCUN jeton : elle peut être appelée plusieurs fois,
    y compris par des gardes en cascade (hook, broker, orchestrateur), sans
    épuiser l'autorisation. La consommation est déléguée à `redeem`.
    ``secret_reason`` permet de propager la cause exacte d'indisponibilité du
    secret (absent, permissions laxistes, illisible) — aucun masquage.
    """
    moment = now or _utc_now()
    verdict: dict[str, Any] = {"guard": "Gate 2 Delegation Guard", "token_version": TOKEN_VERSION}

    # 1. Structure DAG + sceau d'intégrité (réutilisation, pas de réinvention)
    code, dag = dag_verify(graph_path)
    verdict["dag"] = dag
    if code != EXIT_PASS:
        verdict.update({"verdict": "BLOCKED", "reason": dag.get("reason", "GATE2_DAG_VERIFY_FAILED"),
                        "stage": "DAG_VERIFY"})
        return EXIT_BLOCKED, verdict
    try:
        graph = load_graph_file(graph_path)
        graph_sha256 = compute_approval_sha256(graph)
    except GraphError as exc:
        verdict.update({"verdict": "BLOCKED", "reason": str(exc), "stage": "DAG_RELOAD"})
        return EXIT_BLOCKED, verdict
    verdict["graph_sha256"] = graph_sha256

    # 2. Jeton présent et bien formé
    token, reason = _load_token_file(token_path)
    if token is None:
        verdict.update({"verdict": "BLOCKED", "reason": reason, "stage": "TOKEN_LOAD",
                        "token": str(token_path)})
        return EXIT_BLOCKED, verdict

    # 3. Signature HMAC (preuve d'identité de l'autorité émettrice)
    if secret is None:
        verdict.update({"verdict": "UNKNOWN", "reason": secret_reason or "GATE2_SECRET_UNAVAILABLE",
                        "stage": "TOKEN_SIGNATURE",
                        "note": "P3 : secret non observable — jamais un PASS implicite."})
        return EXIT_UNKNOWN, verdict
    if not verify_token_signature(token, secret):
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_TOKEN_SIGNATURE_INVALID",
                        "stage": "TOKEN_SIGNATURE"})
        return EXIT_BLOCKED, verdict

    # 4. Liaison (mission, graphe, autorité, fenêtre de validité)
    binding_reason = _check_binding(token, graph_sha256, mission_id, moment)
    if binding_reason is not None:
        verdict.update({"verdict": "BLOCKED", "reason": binding_reason, "stage": "TOKEN_BINDING"})
        return EXIT_BLOCKED, verdict

    # 5. Anti-rejeu (lecture seule) : le nonce a-t-il déjà été consommé ?
    if root is not None:
        lock = nonce_lock_path(root, str(token["nonce"]))
        if lock.is_file():
            # RESERVED = spawn réservé non observé (crash possible, A-7) —
            # fail-closed : libération uniquement par `release` manuel signé.
            state_reason = ("GATE2_TOKEN_RESERVED_UNOBSERVED"
                            if _lock_state(lock) == LOCK_STATE_RESERVED
                            else "GATE2_TOKEN_ALREADY_CONSUMED")
            verdict.update({"verdict": "BLOCKED", "reason": state_reason,
                            "stage": "NONCE_REGISTRY", "nonce": token["nonce"]})
            return EXIT_BLOCKED, verdict

    verdict.update({
        "verdict": "PASS",
        "reason": "GATE2_DELEGATION_AUTHORIZED",
        "stage": "PRE_FLIGHT",
        "mission_id": mission_id,
        "authority": token["authority"],
        "nonce": token["nonce"],
        "expires_at": token["expires_at"],
        "token_sha256": _sha256_hex(canonical_bytes(token)),
        "note": "Vérification pure — consommer le nonce via `consume` au moment de la délégation.",
    })
    return EXIT_PASS, verdict


# --------------------------------------------------------------------------- #
# Rédemption atomique : consommation à usage unique (A-003)                   #
# --------------------------------------------------------------------------- #
def redeem_delegation_token(graph_path: Path, token_path: Path, mission_id: str,
                            secret: bytes, *, now: datetime | None = None,
                            root: Path) -> tuple[int, dict[str, Any]]:
    """Consomme atomiquement le jeton au moment de la délégation réelle.

    Toutes les vérifications du pré-vol sont rejouées (anti-TOCTOU), puis le
    nonce est verrouillé par création exclusive ``O_CREAT|O_EXCL`` (A-003) et
    l'échange est scellé dans le grand livre chaîné.
    """
    moment = now or _utc_now()
    code, verdict = pre_flight_delegation_check(graph_path, token_path, mission_id,
                                                secret=secret, now=moment)
    if code != EXIT_PASS:
        return code, verdict

    nonce = str(verdict["nonce"])
    lock = nonce_lock_path(root, nonce)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(lock.parent, 0o700)
    except OSError:
        pass
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                              "reason": "GATE2_TOKEN_REPLAY_DETECTED", "stage": "NONCE_CLAIM"}
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "nonce": nonce,
                "state": LOCK_STATE_CONSUMED,
                "mission_id": mission_id,
                "graph_sha256": verdict["graph_sha256"],
                "token_sha256": verdict["token_sha256"],
                "redeemed_at": _iso(moment),
            }, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError:
        return EXIT_UNKNOWN, {**verdict, "verdict": "UNKNOWN",
                              "reason": "GATE2_NONCE_WRITE_FAILED", "stage": "NONCE_CLAIM"}

    entry_hash, ledger_reason = _append_ledger(root, {
        "event": "GATE2_DELEGATION_REDEEMED",
        "mission_id": mission_id,
        "graph_sha256": verdict["graph_sha256"],
        "nonce": nonce,
        "authority": verdict["authority"],
        "token_sha256": verdict["token_sha256"],
        "redeemed_at": _iso(moment),
        "nonce_lock": str(lock.relative_to(root.resolve())),
    })
    if ledger_reason is not None:
        return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED", "reason": ledger_reason,
                              "stage": "REDEMPTION_LEDGER"}

    verdict.update({"reason": "GATE2_DELEGATION_REDEEMED", "stage": "CONSUMED",
                    "redemption_entry_hash": entry_hash,
                    "note": "Nonce consommé (A-003) — tout rejeu est désormais détecté et bloqué."})
    return EXIT_PASS, verdict


# --------------------------------------------------------------------------- #
# Transaction Safe-Spawn (A-7) : RESERVE -> SPAWN -> OBSERVE                   #
# --------------------------------------------------------------------------- #
def _rewrite_lock_state(lock: Path, payload: dict[str, Any]) -> None:
    """Réécrit le verrou de nonce avec un état terminal (observation consignée)."""
    with lock.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _terminal_lock(lock: Path, verdict: dict[str, Any], state: str, moment: datetime) -> None:
    _rewrite_lock_state(lock, {
        "nonce": verdict["nonce"],
        "state": state,
        "mission_id": verdict["mission_id"],
        "graph_sha256": verdict["graph_sha256"],
        "token_sha256": verdict["token_sha256"],
        "observed_at": _iso(moment),
    })


def spawn_delegation_transaction(graph_path: Path, token_path: Path, mission_id: str,
                                 secret: bytes, *, root: Path,
                                 spawn_command: list[str],
                                 timeout_seconds: int = 120,
                                 spawn_cwd: Path | None = None,
                                 now: datetime | None = None) -> tuple[int, dict[str, Any]]:
    """Transaction de délégation Safe-Spawn (A-7).

    Séquence déterministe :
      1. PRE_FLIGHT  — vérification pure (structure, sceau, jeton, liaison, nonce).
      2. RESERVE     — verrou exclusif O_CREAT|O_EXCL sur le nonce.
      3. SPAWN       — exécution de la commande d'instanciation observée.
      4. OBSERVE     — quatre issues fermées :
           - SPAWN_SUCCEEDED             -> COMMIT_SUCCESS   (nonce consommé, ledger)
           - SPAWN_FAILED post-start     -> COMMIT_FAILURE   (nonce consommé, ledger)
           - SPAWN_NOT_STARTED (certain) -> ABORT_SAFE       (nonce libéré, ledger)
           - SPAWN_UNKNOWN / timeout     -> UNKNOWN_CONFINED (nonce consommé, ledger)

    Règle absolue : dès qu'il existe une possibilité non nulle que le spawn ait
    débuté, le nonce est DÉFINITIVEMENT consommé — aucun retry automatique.
    La reprise après crash (verrou RESERVED non observé) passe par `release`,
    un geste manuel signé et ledgeré.
    """
    moment = now or _utc_now()
    code, verdict = pre_flight_delegation_check(graph_path, token_path, mission_id,
                                                secret=secret, now=moment, root=root)
    if code != EXIT_PASS:
        return code, verdict

    nonce = str(verdict["nonce"])
    lock = nonce_lock_path(root, nonce)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(lock.parent, 0o700)
    except OSError:
        pass

    # --- RESERVE ---------------------------------------------------------- #
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                              "reason": "GATE2_TOKEN_REPLAY_DETECTED", "stage": "RESERVE"}
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "nonce": nonce,
                "state": LOCK_STATE_RESERVED,
                "mission_id": mission_id,
                "graph_sha256": verdict["graph_sha256"],
                "token_sha256": verdict["token_sha256"],
                "reserved_at": _iso(moment),
            }, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError:
        return EXIT_UNKNOWN, {**verdict, "verdict": "UNKNOWN",
                              "reason": "GATE2_NONCE_WRITE_FAILED", "stage": "RESERVE"}

    # Re-vérification d'intégrité post-RESERVE (anti-TOCTOU) : si le graphe a
    # été retouché entre le pré-vol et le spawn, le spawn n'a PAS commencé ->
    # ABORT_SAFE propre.
    code_post, dag_post = dag_verify(graph_path)
    if code_post != EXIT_PASS:
        try:
            os.unlink(lock)
        except OSError:
            pass
        _, ledger_reason = _append_ledger(root, {
            "event": "GATE2_SPAWN_ABORT_SAFE",
            "mission_id": mission_id,
            "graph_sha256": verdict["graph_sha256"],
            "nonce": nonce,
            "abort_reason": "GATE2_GRAPH_CHANGED_AFTER_RESERVE",
            "observed_at": _iso(moment),
        })
        if ledger_reason is not None:
            return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                                  "reason": ledger_reason, "stage": "REDEMPTION_LEDGER"}
        verdict.update({"verdict": "BLOCKED", "stage": "SPAWN",
                        "reason": "GATE2_GRAPH_CHANGED_AFTER_RESERVE",
                        "dag": dag_post,
                        "note": "ABORT_SAFE : nonce libéré — le spawn n'a pas démarré."})
        return EXIT_BLOCKED, verdict

    # --- SPAWN ------------------------------------------------------------ #
    try:
        proc = subprocess.run(spawn_command, capture_output=True, text=True,
                              timeout=max(int(timeout_seconds), 1), check=False,
                              cwd=str(spawn_cwd) if spawn_cwd is not None else None)
    except subprocess.TimeoutExpired:
        # --- OBSERVE : UNKNOWN_CONFINED (fail-closed, zéro retry) --------- #
        _terminal_lock(lock, verdict, "UNKNOWN_CONFINED", moment)
        entry_hash, ledger_reason = _append_ledger(root, {
            "event": "GATE2_SPAWN_UNKNOWN_CONFINED",
            "mission_id": mission_id,
            "graph_sha256": verdict["graph_sha256"],
            "nonce": nonce,
            "authority": verdict["authority"],
            "spawn_command": spawn_command,
            "timeout_seconds": max(int(timeout_seconds), 1),
            "observed_at": _iso(moment),
        })
        if ledger_reason is not None:
            return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                                  "reason": ledger_reason, "stage": "REDEMPTION_LEDGER"}
        verdict.update({"verdict": "UNKNOWN", "reason": "GATE2_SPAWN_UNKNOWN_CONFINED",
                        "stage": "OBSERVE", "redemption_entry_hash": entry_hash,
                        "note": "Nonce DÉFINITIVEMENT consommé — inspection requise, "
                                "aucun retry automatique (A-7)."})
        return EXIT_UNKNOWN, verdict
    except (OSError, subprocess.SubprocessError):
        # --- OBSERVE : SPAWN_NOT_STARTED certain -> ABORT_SAFE ------------ #
        try:
            os.unlink(lock)
        except OSError:
            pass
        _, ledger_reason = _append_ledger(root, {
            "event": "GATE2_SPAWN_ABORT_SAFE",
            "mission_id": mission_id,
            "graph_sha256": verdict["graph_sha256"],
            "nonce": nonce,
            "abort_reason": "GATE2_SPAWN_NOT_STARTED",
            "spawn_command": spawn_command,
            "observed_at": _iso(moment),
        })
        if ledger_reason is not None:
            return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                                  "reason": ledger_reason, "stage": "REDEMPTION_LEDGER"}
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_SPAWN_NOT_STARTED_ABORT_SAFE",
                        "stage": "SPAWN",
                        "note": "ABORT_SAFE : échec de lancement certain (spawn jamais "
                                "démarré) — nonce libéré et réutilisable."})
        return EXIT_BLOCKED, verdict

    # --- OBSERVE : résultat déterministe ----------------------------------- #
    if proc.returncode == 0:
        _terminal_lock(lock, verdict, LOCK_STATE_CONSUMED, moment)
        entry_hash, ledger_reason = _append_ledger(root, {
            "event": "GATE2_DELEGATION_SPAWN_SUCCEEDED",
            "mission_id": mission_id,
            "graph_sha256": verdict["graph_sha256"],
            "nonce": nonce,
            "authority": verdict["authority"],
            "token_sha256": verdict["token_sha256"],
            "spawn_command": spawn_command,
            "spawn_exit_code": 0,
            "observed_at": _iso(moment),
            "nonce_lock": str(lock.relative_to(root.resolve())),
        })
        if ledger_reason is not None:
            return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                                  "reason": ledger_reason, "stage": "REDEMPTION_LEDGER"}
        verdict.update({"verdict": "PASS", "reason": "GATE2_DELEGATION_SPAWN_SUCCEEDED",
                        "stage": "OBSERVE", "spawn_exit_code": 0,
                        "redemption_entry_hash": entry_hash,
                        "note": "COMMIT_SUCCESS : nonce consommé, grand livre chaîné mis à jour."})
        return EXIT_PASS, verdict

    _terminal_lock(lock, verdict, LOCK_STATE_CONSUMED, moment)
    entry_hash, ledger_reason = _append_ledger(root, {
        "event": "GATE2_DELEGATION_SPAWN_FAILED",
        "mission_id": mission_id,
        "graph_sha256": verdict["graph_sha256"],
        "nonce": nonce,
        "authority": verdict["authority"],
        "spawn_command": spawn_command,
        "spawn_exit_code": proc.returncode,
        "observed_at": _iso(moment),
        "nonce_lock": str(lock.relative_to(root.resolve())),
    })
    if ledger_reason is not None:
        return EXIT_BLOCKED, {**verdict, "verdict": "BLOCKED",
                              "reason": ledger_reason, "stage": "REDEMPTION_LEDGER"}
    verdict.update({"verdict": "BLOCKED", "reason": "GATE2_DELEGATION_SPAWN_FAILED",
                    "stage": "OBSERVE", "spawn_exit_code": proc.returncode,
                    "redemption_entry_hash": entry_hash,
                    "note": "COMMIT_FAILURE : spawn démarré puis échoué — nonce "
                            "définitivement consommé, anomalie consignée."})
    return EXIT_BLOCKED, verdict


def release_reserved_nonce(root: Path, nonce: str, *, secret: bytes | None,
                           now: datetime | None = None) -> tuple[int, dict[str, Any]]:
    """Release MANUEL signé d'un verrou RESERVED non observé (reprise post-crash).

    Refuse tout verrou terminal : un nonce consommé n'est jamais relâchable.
    Le geste est ledgeré (GATE2_NONCE_RELEASED_MANUAL) pour garantir la
    traçabilité de toute remise en jeu d'autorisation.
    """
    verdict: dict[str, Any] = {"guard": "Gate 2 Delegation Guard", "nonce": nonce}
    if secret is None:
        verdict.update({"verdict": "UNKNOWN", "reason": "GATE2_SECRET_UNAVAILABLE",
                        "note": "P3 : release manuel refusé sans autorité observable."})
        return EXIT_UNKNOWN, verdict
    lock = nonce_lock_path(root, nonce)
    if not lock.is_file():
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_NONCE_LOCK_MISSING"})
        return EXIT_BLOCKED, verdict
    state = _lock_state(lock)
    if state != LOCK_STATE_RESERVED:
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_NONCE_LOCK_TERMINAL",
                        "state": state,
                        "note": "Un nonce consommé n'est jamais relâchable."})
        return EXIT_BLOCKED, verdict
    try:
        os.unlink(lock)
    except OSError:
        verdict.update({"verdict": "UNKNOWN", "reason": "GATE2_NONCE_RELEASE_FAILED"})
        return EXIT_UNKNOWN, verdict
    entry_hash, ledger_reason = _append_ledger(root, {
        "event": "GATE2_NONCE_RELEASED_MANUAL",
        "nonce": nonce,
        "released_at": _iso(now or _utc_now()),
        "note": "Release manuel signé — spawn certainement jamais démarré "
                "(verrou RESERVED, jamais observé).",
    })
    if ledger_reason is not None:
        verdict.update({"verdict": "BLOCKED", "reason": ledger_reason,
                        "stage": "REDEMPTION_LEDGER"})
        return EXIT_BLOCKED, verdict
    verdict.update({"verdict": "PASS", "reason": "GATE2_NONCE_RELEASED_MANUAL",
                    "redemption_entry_hash": entry_hash,
                    "note": "Nonce libéré et ledgeré — la délégation peut être rejouée "
                            "par un nouveau pré-vol."})
    return EXIT_PASS, verdict


# --------------------------------------------------------------------------- #
# Statut                                                                      #
# --------------------------------------------------------------------------- #
def cmd_status(root: Path, token_path: Path, mission_id: str | None, secret: bytes | None,
               now: datetime | None) -> tuple[int, dict[str, Any]]:
    verdict: dict[str, Any] = {"guard": "Gate 2 Delegation Guard", "root": str(root),
                               "token": str(token_path)}
    token, reason = _load_token_file(token_path)
    if token is None:
        verdict.update({"verdict": "UNKNOWN" if reason == "GATE2_TOKEN_MISSING" else "BLOCKED",
                        "reason": reason})
        return (EXIT_UNKNOWN if reason == "GATE2_TOKEN_MISSING" else EXIT_BLOCKED), verdict

    consumed = nonce_consumed(root, str(token.get("nonce", "")))
    verdict["nonce_consumed"] = consumed
    if secret is None:
        verdict.update({"verdict": "UNKNOWN", "reason": "GATE2_SECRET_UNAVAILABLE",
                        "note": "P3 : authenticité du jeton non observable."})
        return EXIT_UNKNOWN, verdict
    if not verify_token_signature(token, secret):
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_TOKEN_SIGNATURE_INVALID"})
        return EXIT_BLOCKED, verdict

    graph_sha = str(token.get("graph_sha256", ""))
    binding_reason = _check_binding(token, graph_sha, mission_id or str(token.get("mission_id", "")),
                                    now or _utc_now())
    if consumed:
        verdict.update({"verdict": "BLOCKED", "reason": "GATE2_TOKEN_ALREADY_CONSUMED"})
        return EXIT_BLOCKED, verdict
    if binding_reason is not None and mission_id is not None:
        verdict.update({"verdict": "BLOCKED", "reason": binding_reason})
        return EXIT_BLOCKED, verdict

    verdict.update({"verdict": "PASS", "reason": "GATE2_TOKEN_VALID_UNCONSUMED",
                    "mission_id": token.get("mission_id"), "authority": token.get("authority"),
                    "expires_at": token.get("expires_at")})
    return EXIT_PASS, verdict


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #
def _emit(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vigilum Codex 2.1.3 — Gate 2 Delegation Guard")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser, need_root: bool = True) -> None:
        p.add_argument("--graph", type=Path, required=True, help="Mission Graph scellé")
        p.add_argument("--mission", required=True, help="ID de mission attendu")
        p.add_argument("--root", type=Path, default=None, help="Racine runtime (défaut: CWD)")
        p.add_argument("--token", type=Path, default=None,
                       help=f"Chemin du jeton (défaut: <root>/runtime/gate2/{TOKEN_FILE_NAME})")
        p.add_argument("--secret-file", default=None, help="Fichier de secret HMAC (0600)")
        p.add_argument("--now", default=None, help="Horodatage ISO-8601 (tests déterministes)")

    p_issue = sub.add_parser("issue-token", help="Cérémonie humaine : émettre le jeton Gate 2")
    common(p_issue)
    p_issue.add_argument("--authority", default="Lord Mahonheim")
    p_issue.add_argument("--ttl-seconds", type=int, default=DEFAULT_TTL_SECONDS)
    p_issue.add_argument("--issued-at", default=None, help="Horodatage ISO-8601 (tests déterministes)")

    p_pre = sub.add_parser("pre-flight", help="Pré-vol de délégation (vérification PURE)")
    common(p_pre)

    p_consume = sub.add_parser("consume", help="Consommer le jeton (usage unique, A-003)")
    common(p_consume)

    p_delegate = sub.add_parser(
        "delegate",
        help="Transaction Safe-Spawn (A-7) : RESERVE -> SPAWN -> OBSERVE (usage unique)")
    common(p_delegate)
    p_delegate.add_argument("--spawn-command", nargs="+", required=True,
                            help="Commande d'instanciation à observer (transaction A-7)")
    p_delegate.add_argument("--spawn-timeout", type=int, default=120,
                            help="Timeout du spawn (s) — au-delà : UNKNOWN_CONFINED")
    p_delegate.add_argument("--spawn-cwd", type=Path, default=None,
                            help="Répertoire de travail du spawn (défaut: hérité)")

    p_release = sub.add_parser(
        "release",
        help="Release manuel signé d'un nonce RESERVED non observé (reprise post-crash)")
    p_release.add_argument("--root", type=Path, default=None)
    p_release.add_argument("--nonce", required=True)
    p_release.add_argument("--secret-file", default=None)

    p_status = sub.add_parser("status", help="État du verrou Gate 2")
    p_status.add_argument("--root", type=Path, default=None)
    p_status.add_argument("--token", type=Path, default=None)
    p_status.add_argument("--mission", default=None)
    p_status.add_argument("--secret-file", default=None)
    p_status.add_argument("--now", default=None)

    args = parser.parse_args(argv)
    root = (getattr(args, "root", None) or Path.cwd()).resolve()
    token_path = getattr(args, "token", None) or (gate2_dir(root) / TOKEN_FILE_NAME)
    secret, secret_reason = resolve_secret(getattr(args, "secret_file", None))
    now = _parse_iso(args.now) if getattr(args, "now", None) else None
    if getattr(args, "now", None) and now is None:
        _emit({"verdict": "BLOCKED", "reason": "GATE2_TIMESTAMP_INVALID"})
        return EXIT_USAGE

    if args.command == "issue-token":
        if secret is None:
            _emit({"verdict": "BLOCKED", "reason": secret_reason,
                   "note": "Émission impossible sans secret humain (P-AGENT-002)."})
            return EXIT_BLOCKED
        issued_at = _parse_iso(args.issued_at) if args.issued_at else None
        if args.issued_at and issued_at is None:
            _emit({"verdict": "BLOCKED", "reason": "GATE2_TIMESTAMP_INVALID"})
            return EXIT_USAGE
        code, result = issue_token(args.graph, token_path, args.mission, args.authority,
                                   secret, args.ttl_seconds, issued_at)
        _emit(result)
        return code

    if args.command == "pre-flight":
        code, result = pre_flight_delegation_check(args.graph, token_path, args.mission,
                                                   secret=secret, secret_reason=secret_reason,
                                                   now=now, root=root)
        _emit(result)
        return code

    if args.command == "consume":
        if secret is None:
            _emit({"verdict": "UNKNOWN", "reason": secret_reason,
                   "note": "P3 : consommation refusée sans secret observable."})
            return EXIT_UNKNOWN
        code, result = redeem_delegation_token(args.graph, token_path, args.mission,
                                               secret, now=now, root=root)
        _emit(result)
        return code

    if args.command == "delegate":
        if secret is None:
            _emit({"verdict": "UNKNOWN", "reason": secret_reason,
                   "note": "P3 : transaction de délégation refusée sans secret observable."})
            return EXIT_UNKNOWN
        code, result = spawn_delegation_transaction(
            args.graph, token_path, args.mission, secret, root=root,
            spawn_command=list(args.spawn_command),
            timeout_seconds=args.spawn_timeout,
            spawn_cwd=args.spawn_cwd, now=now)
        _emit(result)
        return code

    if args.command == "release":
        code, result = release_reserved_nonce(root, args.nonce, secret=secret, now=now)
        _emit(result)
        return code

    if args.command == "status":
        code, result = cmd_status(root, token_path, args.mission, secret, now)
        _emit(result)
        return code

    _emit({"verdict": "BLOCKED", "reason": "GATE2_COMMAND_UNSUPPORTED"})
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())

