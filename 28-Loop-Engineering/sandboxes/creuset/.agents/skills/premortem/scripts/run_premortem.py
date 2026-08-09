#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'exportation et d'indexation automatique pour les diagnostics Premortem.
Ce script automatise la livraison du rapport Premortem dans Obsidian Avalon (OUTPUTS)
et synchronise l'indexation dans le second cerveau de Tesla.
"""

import os
import sys
import datetime
import re
import json

# Chemins par défaut
WORKSPACE_ROOT = "/home/lord-mahonheim/bifrost/tesla"
OUTPUTS_DIR = os.path.join(WORKSPACE_ROOT, "OUTPUTS")
MEMORY_DIR = os.path.join(WORKSPACE_ROOT, "memory")
TEMPLATE_PATH = os.path.join(WORKSPACE_ROOT, ".agents/skills/premortem/templates/premortem_report.md")

def sanitize_filename(name):
    """Nettoie le nom de fichier pour éviter les caractères spéciaux."""
    name = re.sub(r'[\\/*?:"<>| ]', '_', name)
    return name.lower()

def inject_frontmatter(content, plan_name):
    """
    Injecte le frontmatter YAML requis pour Obsidian Avalon.
    Si le contenu possède déjà un frontmatter, il le remplace ou l'insère proprement.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    frontmatter = f"""---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[{plan_name}]]"
date: {today}
version: 1.0
---

"""
    # Enlever un éventuel frontmatter existant dans le contenu généré
    cleaned_content = content
    if content.strip().startswith("---"):
        parts = content.strip().split("---", 2)
        if len(parts) >= 3:
            cleaned_content = parts[2].lstrip()
            
    return frontmatter + cleaned_content

def export_to_outputs(filename, content):
    """Écrit le fichier dans le dossier de sortie OUTPUTS."""
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)
        
    target_path = os.path.join(OUTPUTS_DIR, filename)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return target_path

def trigger_semantic_indexing():
    """Déclenche la mise à jour de la mémoire sémantique globale."""
    script_path = os.path.join(MEMORY_DIR, "update_session_history.py")
    if os.path.exists(script_path):
        print("[*] Déclenchement de la réindexation sémantique globale...")
        os.system(f"python3 {script_path}")
    else:
        print("[!] Script update_session_history.py introuvable, réindexation manuelle nécessaire.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 run_premortem.py <chemin_du_rapport_brut> <nom_du_plan_original>")
        sys.exit(1)
        
    raw_report_path = sys.argv[1]
    plan_name = sys.argv[2]
    
    if not os.path.exists(raw_report_path):
        print(f"[!] Fichier de rapport brut introuvable : {raw_report_path}")
        sys.exit(1)
        
    with open(raw_report_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        
    # Structuration du rapport final
    final_content = inject_frontmatter(raw_content, plan_name)
    
    # Génération du nom de fichier cible
    sanitized_plan = sanitize_filename(plan_name)
    target_filename = f"premortem_{sanitized_plan}.md"
    
    # Exportation physique
    target_path = export_to_outputs(target_filename, final_content)
    print(f"[+] Rapport Premortem livré avec succès dans Obsidian Avalon :")
    print(f"    {target_path}")
    
    # Indexation
    trigger_semantic_indexing()

if __name__ == "__main__":
    main()
