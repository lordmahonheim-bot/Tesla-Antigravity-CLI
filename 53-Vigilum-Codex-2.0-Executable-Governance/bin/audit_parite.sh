#!/usr/bin/env bash
# Wrapper d'exécution POSIX pour l'audit de parité binaire
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESLA_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MISSION_ID="${MISSION_ID:-SGC-EXEC-GOV-03}"
COMPONENT_ID="${COMPONENT_ID:-COMP-PARITY-01}"
COMPONENT_TYPE="${COMPONENT_TYPE:-TOOLING}"
BASELINE_FINGERPRINT="${BASELINE_FINGERPRINT:-}"
ROOT_DIR="${TESLA_ROOT}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root)
            ROOT_DIR="$2"
            shift 2
            ;;
        --mission)
            MISSION_ID="$2"
            shift 2
            ;;
        --baseline)
            BASELINE_FINGERPRINT="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 64
            ;;
    esac
done

python3 "${SCRIPT_DIR}/audit_parite.py" \
    --id "${COMPONENT_ID}" \
    --type "${COMPONENT_TYPE}" \
    --root "${ROOT_DIR}" \
    --mission "${MISSION_ID}" \
    --baseline "${BASELINE_FINGERPRINT}"
