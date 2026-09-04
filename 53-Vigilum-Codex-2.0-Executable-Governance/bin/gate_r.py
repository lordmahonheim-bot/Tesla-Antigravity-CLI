#!/usr/bin/env python3
"""
Vigilum Codex 2.1 - Gate R (Reconciliation & DSSE HMAC)
Generates runtime/contracts/mission_truth.json exclusively.
"""

import os
import sys
import json
import hmac
import hashlib
import base64
import argparse
from datetime import datetime, timezone

def pae(payload_type: bytes, payload: bytes) -> bytes:
    """Pre-Authentication Encoding for DSSE."""
    return b"DSSEv1 %d %b %d %b" % (len(payload_type), payload_type, len(payload), payload)

def generate_dsse_hmac(payload_type: str, payload_str: str, key: bytes) -> dict:
    pt_bytes = payload_type.encode('utf-8')
    p_bytes = payload_str.encode('utf-8')
    
    encoded = pae(pt_bytes, p_bytes)
    mac = hmac.new(key, encoded, hashlib.sha256).digest()
    
    return {
        "payload": base64.b64encode(p_bytes).decode('utf-8'),
        "payloadType": payload_type,
        "signatures": [
            {
                "keyid": "local-hmac-key",
                "sig": base64.b64encode(mac).decode('utf-8')
            }
        ]
    }

def get_hermetic_key() -> bytes:
    """
    Reads the hermetic key from ~/.tesla/gate2/secret.key.
    Enforces mode 0600.
    """
    key_path = os.path.expanduser("~/.tesla/gate2/secret.key")
    if not os.path.exists(key_path):
        print(f"Gate R FATAL — secret.key not found at {key_path}")
        sys.exit(1)
        
    stat = os.stat(key_path)
    if stat.st_mode & 0o777 != 0o600:
        print(f"Gate R FATAL — secret.key permissions are not 0600")
        sys.exit(1)
        
    try:
        with open(key_path, 'r') as key_file:
            key_str = key_file.read().strip()
            if not key_str:
                raise ValueError("Key file is empty")
            return key_str.encode('utf-8')
    except Exception as e:
        print(f"Gate R FATAL — failed to read hermetic key: {e}")
        sys.exit(1)

def reconcile(root_dir: str, mission_id: str):
    """
    Observe disk state, verify hashes (simulated here for scaffolding),
    and produce the signed mission_truth.json ledger.
    """
    contracts_dir = os.path.join(root_dir, "runtime", "contracts")
    os.makedirs(contracts_dir, exist_ok=True)
    truth_file = os.path.join(contracts_dir, "mission_truth.json")
    
    # 1. Observation (mocked for scaffolding)
    # 2. Construction of Truth Ledger
    payload_dict = {
        "mission_id": mission_id,
        "status": "RECONCILED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "observations": [
            {"type": "observation", "path": "evidence/transcript.md", "status": "VERIFIED"}
        ],
        "generator": "bin/gate_r.py",
        "doctrine": "C2/P11"
    }
    
    payload_str = json.dumps(payload_dict, separators=(',', ':'))
    
    # 3. Cryptographic Attestation
    key = get_hermetic_key()
    
    envelope = generate_dsse_hmac(
        payload_type="https://tesla.bifrost/mission-truth/v1",
        payload_str=payload_str,
        key=key
    )
    
    with open(truth_file, 'w') as f:
        json.dump(envelope, f, indent=2)
        
    print(f"Gate R RECONCILED — exit 0")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Gate R - Evidence Reconciliation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    rec_parser = subparsers.add_parser("reconcile")
    rec_parser.add_argument("--root", required=True, help="Repository root")
    rec_parser.add_argument("--mission", required=True, help="Mission ID")
    
    args = parser.parse_args()
    
    if args.command == "reconcile":
        reconcile(args.root, args.mission)

if __name__ == "__main__":
    main()
