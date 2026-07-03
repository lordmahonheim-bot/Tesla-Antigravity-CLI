#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate_note.py - Script de validation AST du frontmatter des fiches Markdown.
Vérifie la syntaxe YAML et la conformité sémantique (champs, types, formats).
"""

import sys
import re
import datetime
from pathlib import Path
import frontmatter

def validate_frontmatter(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"[!] Fichier introuvable : {path}")
        return False
        
    try:
        # Tenter le chargement AST du frontmatter
        post = frontmatter.load(path)
    except Exception as e:
        print(f"[!] Erreur de syntaxe YAML (AST) critique dans {path.name} : {e}")
        return False
        
    # Vérification des champs requis et de leur type/format
    metadata = post.metadata
    
    # Si aucun frontmatter n'est présent mais que le fichier est vide ou sans métadonnées, c'est un avertissement
    if not metadata:
        print(f"[!] Aucun frontmatter YAML détecté dans {path.name}.")
        return False

    errors = []
    
    # 1. Validation du champ 'type'
    note_type = metadata.get("type")
    allowed_types = ["decision", "fait", "reference", "tache"]
    if not note_type:
        errors.append("Champ 'type' manquant.")
    elif note_type not in allowed_types:
        errors.append(f"Valeur 'type' invalide : '{note_type}'. Doit être l'une des suivantes : {allowed_types}")

    # 2. Validation du champ 'tags'
    tags = metadata.get("tags")
    if tags is None:
        errors.append("Champ 'tags' manquant.")
    elif not isinstance(tags, list):
        errors.append("Le champ 'tags' doit être une liste (ex: [tag1, tag2]).")

    # 3. Validation du champ 'date'
    date_val = metadata.get("date")
    if not date_val:
        errors.append("Champ 'date' manquant.")
    else:
        # S'assurer que c'est un format de date valide (soit objet date, soit string ISO)
        if not isinstance(date_val, (datetime.date, datetime.datetime)):
            # Tenter de parser la string
            try:
                datetime.date.fromisoformat(str(date_val))
            except ValueError:
                errors.append(f"Format de 'date' invalide : '{date_val}'. Utiliser AAAA-MM-JJ.")

    # 4. Validation du champ 'source'
    source = metadata.get("source")
    if not source:
        errors.append("Champ 'source' manquant.")
    elif not isinstance(source, str):
        errors.append("Le champ 'source' doit être une chaîne de caractères.")

    # 5. Validation du champ 'statut'
    statut = metadata.get("statut")
    allowed_statuts = ["a-valider", "valide", "archive"]
    if not statut:
        errors.append("Champ 'statut' manquant.")
    elif statut not in allowed_statuts:
        errors.append(f"Valeur 'statut' invalide : '{statut}'. Doit être l'une des suivantes : {allowed_statuts}")

    # 6. Validation du champ 'version'
    version = metadata.get("version")
    if version is None:
        errors.append("Champ 'version' manquant.")
    else:
        # Doit être convertible en float ou format X.Y
        if not isinstance(version, (int, float, str)):
            errors.append("Le champ 'version' doit être un nombre ou une chaîne de type X.Y.")

    if errors:
        print(f"[!] Anomalies détectées dans le frontmatter de {path.name} :")
        for err in errors:
            print(f"  - {err}")
        return False
        
    print(f"[+] Frontmatter de {path.name} valide (AST & Schéma conformes).")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_note.py <chemin_de_la_note_a_valider>")
        sys.exit(1)
        
    valid = validate_frontmatter(sys.argv[1])
    sys.exit(0 if valid else 1)
