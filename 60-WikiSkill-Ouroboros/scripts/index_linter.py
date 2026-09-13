#!/usr/bin/env python3
import sys
import os

MAX_TOKENS = 4000
CHAR_PER_TOKEN = 4
REQUIRED_COLUMNS = ["ID", "PATTERN_NAME", "DOMAIN", "HITS", "RECENCY", "REL_PATH"]

def lint_index(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} n'existe pas.")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = [line for line in content.split('\n') if line.strip()]
    if not lines:
        print("Error: Le fichier index est vide.")
        sys.exit(1)
        
    header_cleaned = [h.strip() for h in lines[0].split('\t')]
    
    if header_cleaned != REQUIRED_COLUMNS:
        print(f"Error: En-têtes TSV invalides.\nAttendu: {REQUIRED_COLUMNS}\nReçu: {header_cleaned}")
        sys.exit(1)
        
    char_count = len(content)
    approx_tokens = char_count / CHAR_PER_TOKEN
    
    print(f"Index stats: {char_count} chars, ~{approx_tokens:.0f} tokens.")
    if approx_tokens > MAX_TOKENS:
        print(f"Error: Limite de tokens dépassée ({approx_tokens:.0f} > {MAX_TOKENS}).")
        sys.exit(1)
        
    print("Linting passé avec succès.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python index_linter.py <path_to_index.tsv>")
        sys.exit(1)
    lint_index(sys.argv[1])
