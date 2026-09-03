#!/usr/bin/env python3
"""Vigilum Gate Daemon - Frontière d'autorité P0 pour Gate 2.

Ce daemon détient la clé privée Ed25519 et communique via socket UNIX.
Il vérifie l'identité du client via SO_PEERCRED et signe/vérifie les jetons.
"""

import asyncio
import json
import logging
import os
import socket
import struct
import sys
from pathlib import Path

try:
    import nacl.signing
    import nacl.encoding
    import nacl.exceptions
except ImportError:
    # V2.5.1 (audit) : diagnostic sur stderr (canal d'erreur POSIX) — le
    # message aller sur stdout laissait les harnais de test sans cause racine.
    print("Erreur: PyNaCl est requis. Installez-le avec `pip install -r "
          "requirements.txt`.", file=sys.stderr)
    sys.exit(66)  # P3 : dépendance inobservable != silence

# Configuration
SOCKET_PATH = Path(os.environ.get("VIGILUM_GATE_SOCK", "/run/vigilum-gate/gate.sock"))
SECRET_KEY_PATH = Path("/etc/vigilum-gate/secret.key")
PUBLIC_KEY_PATH = Path("/etc/vigilum-gate/public.key")
MAX_PAYLOAD_SIZE = 4096
TIMEOUT = 2.0

# Logging structuré
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger("vigilum_gate")


def init_keys() -> nacl.signing.SigningKey:
    """Charge ou génère la paire de clés Ed25519."""
    # Création du dossier si possible, sinon fallback local pour le test
    sk_path = SECRET_KEY_PATH
    pk_path = PUBLIC_KEY_PATH
    
    try:
        sk_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.warning("Impossible de créer /etc/vigilum-gate, fallback sur ./runtime/vigilum-gate")
        local_dir = Path("runtime/vigilum-gate")
        local_dir.mkdir(parents=True, exist_ok=True)
        sk_path = local_dir / "secret.key"
        pk_path = local_dir / "public.key"

    if sk_path.exists():
        logger.info(f"Chargement de la clé privée depuis {sk_path}")
        raw_key = sk_path.read_bytes()
        signing_key = nacl.signing.SigningKey(raw_key, encoder=nacl.encoding.HexEncoder)
    else:
        logger.info("Génération d'une nouvelle clé Ed25519")
        signing_key = nacl.signing.SigningKey.generate()
        # Sauvegarde
        try:
            sk_path.write_bytes(signing_key.encode(encoder=nacl.encoding.HexEncoder))
            os.chmod(sk_path, 0o400)
            
            verify_key = signing_key.verify_key
            pk_path.write_bytes(verify_key.encode(encoder=nacl.encoding.HexEncoder))
            os.chmod(pk_path, 0o444)
        except OSError as e:
            logger.error(f"Erreur lors de la sauvegarde des clés: {e}")
            
    return signing_key


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, signing_key: nacl.signing.SigningKey):
    """Gère une connexion client IPC."""
    sock = writer.get_extra_info('socket')
    peer_uid = -1
    
    try:
        # Récupération de SO_PEERCRED
        # struct ucred est généralement: pid_t pid, uid_t uid, gid_t gid (3 int de 4 bytes)
        cred_len = struct.calcsize('3i')
        creds = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, cred_len)
        pid, uid, gid = struct.unpack('3i', creds)
        peer_uid = uid
        
        # NOTE: En production, on vérifierait si uid est dans une liste autorisée
        logger.debug(f"Connexion acceptée depuis UID: {uid} (PID: {pid})")
        
        # Timeout court
        data = await asyncio.wait_for(reader.read(MAX_PAYLOAD_SIZE), timeout=TIMEOUT)
        if not data:
            raise ValueError("Payload vide")
            
        req = json.loads(data.decode('utf-8'))
        action = req.get("action")
        payload = req.get("payload", {})
        
        if not isinstance(payload, dict):
            raise ValueError("Payload invalide")
            
        canonical_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

        resp = {}
        if action == "sign_token":
            signature = signing_key.sign(canonical_payload, encoder=nacl.encoding.HexEncoder)
            # nacl sign return la signature + message, on extrait juste la signature
            sig_hex = signature.signature.decode('utf-8')
            resp = {"status": "success", "signature": sig_hex}
            logger.info(f"Jeton signé pour mission {payload.get('mission_id')}")
            
        elif action == "verify_token":
            # Pas strictement nécessaire si on donne pk, mais fourni par le daemon pour la complétude
            provided_sig = req.get("signature")
            if not provided_sig:
                raise ValueError("Signature manquante")
            
            verify_key = signing_key.verify_key
            try:
                verify_key.verify(canonical_payload, bytes.fromhex(provided_sig))
                resp = {"status": "success"}
                logger.info("Jeton vérifié avec succès")
            except nacl.exceptions.BadSignatureError:
                resp = {"status": "error", "error_code": "INVALID_SIGNATURE"}
                logger.warning("Vérification échouée: INVALID_SIGNATURE")
        else:
            raise ValueError(f"Action inconnue: {action}")
            
    except asyncio.TimeoutError:
        logger.error("Timeout de la connexion")
        resp = {"status": "error", "error_code": "TIMEOUT"}
    except Exception as e:
        logger.error(f"Erreur IPC (UID: {peer_uid}): {str(e)}")
        # TAMPER_EVIDENT log
        logger.critical(f"TAMPER_EVIDENT: Echec ou tentative invalide depuis UID {peer_uid} - {str(e)}")
        resp = {"status": "error", "error_code": "MALFORMED_REQUEST"}
        
    try:
        writer.write(json.dumps(resp).encode('utf-8') + b'\n')
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    signing_key = init_keys()
    
    # Préparation du socket
    global SOCKET_PATH
    try:
        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        SOCKET_PATH = Path("runtime/vigilum-gate/gate.sock")
        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.warning(f"Fallback socket sur {SOCKET_PATH}")

    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()
        
    server = await asyncio.start_unix_server(
        lambda r, w: handle_client(r, w, signing_key),
        path=str(SOCKET_PATH)
    )
    
    try:
        os.chmod(SOCKET_PATH, 0o660)
    except OSError:
        pass
        
    logger.info(f"Daemon vigilum-gate démarré sur {SOCKET_PATH}")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
