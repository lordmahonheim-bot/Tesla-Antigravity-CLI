#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import tempfile
from pathlib import Path

def write_trace(json_filepath: str) -> None:
    try:
        with open(json_filepath, 'rb') as f:
            data = f.read()
            # Validation rapide du JSON
            json.loads(data)
    except Exception as e:
        print(f"Erreur de lecture ou JSON invalide : {e}", file=sys.stderr)
        sys.exit(1)

    file_hash = hashlib.sha256(data).hexdigest()
    traces_dir = Path("/home/lord-mahonheim/bifrost/tesla/.agents/traces")
    staging_dir = traces_dir / ".staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    dest_file = traces_dir / f"{file_hash}.json"
    
    # Création du fichier temporaire
    fd, temp_path = tempfile.mkstemp(dir=staging_dir, suffix=".json", prefix="trace_")
    
    try:
        # Écriture et flush forcé sur le disque
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        
        # Déplacement atomique
        os.replace(temp_path, dest_file)
        print(f"Trace écrite avec succès : {dest_file}")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur lors de l'écriture de la trace : {e}", file=sys.stderr)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_json>", file=sys.stderr)
        sys.exit(1)
    write_trace(sys.argv[1])
