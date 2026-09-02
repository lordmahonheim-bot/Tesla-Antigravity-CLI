#!/usr/bin/env bash
set -eu
. "$(dirname "$0")/../lib/tesla-exit-codes.sh"
. "$(dirname "$0")/../lib/tesla-logging.sh"

auth_file=${TESLA_PUSH_AUTH_FILE:-}
[ -n "$auth_file" ] || { tesla_log ERROR "push blocked: TESLA_PUSH_AUTH_FILE is unset"; exit "$TESLA_EXIT_PUSH"; }
[ -s "$auth_file" ] || { tesla_log ERROR "push blocked: authorization file is missing or empty"; exit "$TESLA_EXIT_PUSH"; }

python3 - "$auth_file" <<'PY'
import json
import os
import sys
import time
from pathlib import Path

try:
    auth_path = Path(sys.argv[1]).resolve()
    data = json.loads(auth_path.read_text(encoding="utf-8"))
    required = {"authorized", "mission_id", "expires_at", "repository", "ref", "nonce"}
    if not required.issubset(data):
        raise ValueError(f"missing authorization fields: {required - set(data.keys())}")
    if data["authorized"] is not True:
        raise ValueError("authorized must be true")
    if float(data["expires_at"]) <= time.time():
        raise ValueError("authorization token has expired")
    if not str(data["mission_id"]).strip() or not str(data["repository"]).strip() or not str(data["ref"]).strip():
        raise ValueError("authorization scope is incomplete")
    
    nonce = str(data["nonce"]).strip()
    if not nonce:
        raise ValueError("nonce cannot be empty")
    
    # Invariant A-003: Atomic Anti-Replay Primitive via POSIX O_CREAT | O_EXCL
    # V2.1.3 (arbitrage #2): registre nonce isolé hors workspace agent.
    #   TESLA_SECURITY_NONCES_DIR  -> répertoire nonce explicite (ex: ~/.tesla/security/nonces/)
    #   sinon défaut : <root>/runtime/nonces/ (rétro-compatible)
    import os as _os
    import pathlib
    root_dir = Path.cwd()
    nonces_dir_env = _os.environ.get("TESLA_SECURITY_NONCES_DIR")
    if nonces_dir_env:
        nonces_dir = pathlib.Path(nonces_dir_env).expanduser()
    else:
        nonces_dir = root_dir / "runtime" / "nonces"
    nonces_dir.mkdir(parents=True, exist_ok=True)
    if nonces_dir_env:
        try:
            _os.chmod(nonces_dir, 0o700)  # mode 0700 : registre confidentiel isolé
        except OSError:
            pass
    nonce_lock = nonces_dir / f"{nonce}.lock"
    
    try:
        # Atomic creation; fails if file already exists
        fd = os.open(str(nonce_lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "nonce": nonce,
                "mission_id": data["mission_id"],
                "repository": data["repository"],
                "ref": data["ref"],
                "consumed_at": time.time(),
            }) + "\n")
    except FileExistsError:
        raise ValueError(f"INVARIANT A-003 VIOLATION: Nonce '{nonce}' has already been consumed (Replay Detected)")

except Exception as exc:
    print(f"push blocked: {exc}", file=sys.stderr)
    sys.exit(70)
PY

tesla_log INFO "push authorization validated and single-use nonce consumed successfully"
exit "$TESLA_EXIT_OK"
