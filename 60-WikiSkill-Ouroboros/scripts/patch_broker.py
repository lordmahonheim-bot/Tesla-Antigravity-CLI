#!/usr/bin/env python3
import sys
import json
import re
import os

def process_patch(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} introuvable.")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Recherche du point de départ du Unified Diff
    diff_start_match = re.search(r'^(diff --git|--- a/|--- \./)', content, re.MULTILINE)
    if not diff_start_match:
        print("Error: Aucune section Unified Diff valide trouvée dans le patch.")
        sys.exit(1)
        
    diff_start_idx = diff_start_match.start()
    json_section = content[:diff_start_idx].strip()
    
    # Nettoyage d'un éventuel délimiteur markdown ou manuel
    json_section = re.sub(r'^---+\s*$', '', json_section, flags=re.MULTILINE).strip()
    
    try:
        metadata = json.loads(json_section)
    except json.JSONDecodeError as e:
        print(f"Error: En-tête JSON invalide. {e}")
        sys.exit(1)
        
    required_keys = {"skill_target", "justification", "parent_hash"}
    if not required_keys.issubset(metadata.keys()):
        missing = required_keys - metadata.keys()
        print(f"Error: Clés JSON manquantes: {missing}")
        sys.exit(1)
        
    print("Patch validé avec succès (Structure JSON & format Diff OK).")
    print(f"Target: {metadata['skill_target']}, Parent Hash: {metadata['parent_hash']}")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python patch_broker.py <path_to_patch>")
        sys.exit(1)
    process_patch(sys.argv[1])
