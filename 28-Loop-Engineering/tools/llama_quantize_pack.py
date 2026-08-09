#!/usr/bin/env python3
"""
Alexandria Tools: llama.cpp Ephemeral Quantization Packager
Implémentation conforme à la doctrine LLAMA_CPP_DOCTRINE.md.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import argparse

# Constante de la doctrine
MIN_DISK_SPACE_GB = 8.0
GGUF_MAGIC_HEADER = b"GGUF"


def check_disk_space(path: str) -> bool:
    """Vérifie si l'espace disque disponible sur la partition est suffisant."""
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (1024 ** 3)
    print(f"[*] Espace disque disponible sur {path} : {free_gb:.2f} Go")
    return free_gb >= MIN_DISK_SPACE_GB


def verify_gguf_integrity(filepath: str) -> bool:
    """Atteste de l'intégrité du fichier en vérifiant le header magique GGUF."""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
            return header == GGUF_MAGIC_HEADER
    except Exception:
        return False


def run_quantization(source: str, output: str, quant_type: str) -> bool:
    """Exécute la quantification de manière isolée et éphémère."""
    # 1. Vérification de l'espace disque
    target_dir = os.path.dirname(os.path.abspath(output))
    if not check_disk_space(target_dir):
        print(f"[-] ERREUR : Espace disque insuffisant (requis >= {MIN_DISK_SPACE_GB} Go).")
        return False

    # 2. Création de l'espace temporaire isolé sous /tmp
    temp_dir = tempfile.mkdtemp(prefix="llama-pack-")
    print(f"[*] Espace temporaire cree : {temp_dir}")

    # Déterminer les chemins temporaires
    temp_output = os.path.join(temp_dir, "quantized_model.gguf")

    try:
        # 3. Appel Subprocess Hermétique
        # Recherche du binaire llama-quantize
        cmd = ["llama-quantize", source, temp_output, quant_type]
        print(f"[*] Lancement du binaire natif : {' '.join(cmd)}")
        
        # Exécuter et capturer les sorties
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print("[✓] Processus llama-quantize termine avec succes.")
        
        # 4. Validation Physique du header GGUF
        if not verify_gguf_integrity(temp_output):
            print("[-] ERREUR : Le fichier quantifie temporaire n'a pas un header GGUF valide.")
            return False

        # Déplacer le fichier vers la destination finale
        os.makedirs(target_dir, exist_ok=True)
        shutil.move(temp_output, output)
        print(f"[✓] Modele quantifie deplace avec succes vers : {output}")

        # Validation physique finale
        if verify_gguf_integrity(output):
            print("[✓] Validation physique finale reussie. Header GGUF certifie.")
            return True
        else:
            print("[-] ERREUR : Le fichier final est corrompu ou incomplet.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[-] ERREUR lors de l'execution du binaire llama-quantize (Code {e.returncode}) :")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"[-] ERREUR inattendue durant la quantification : {e}")
        return False
    finally:
        # 5. Purge Inconditionnelle
        print(f"[*] Purge inconditionnelle de l'espace temporaire : {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Outillage de quantification llama.cpp ephemere")
    parser.add_argument("-s", "--source", required=True, help="Chemin du fichier GGUF source")
    parser.add_argument("-o", "--output", required=True, help="Chemin du fichier GGUF quantifie cible")
    parser.add_argument("-t", "--type", default="Q4_K_M", help="Type de quantification (ex: Q4_K_M, Q8_0, default: Q4_K_M)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"[-] ERREUR : Le fichier source {args.source} n'existe pas.")
        sys.exit(1)

    success = run_quantization(args.source, args.output, args.type)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
