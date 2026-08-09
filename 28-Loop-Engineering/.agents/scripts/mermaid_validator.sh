#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file.md>"
    exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not found."
    exit 1
fi

python3 - "$FILE" << 'EOF'
import sys
import re

def validate_mermaid(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Failed to read file: {e}")
        sys.exit(1)

    in_mermaid = False
    has_error = False

    # Matches content inside [/ ... /]
    node_pattern = re.compile(r'\[/(.*?)/\]')

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('```mermaid'):
            in_mermaid = True
            continue
        elif stripped.startswith('```') and in_mermaid:
            in_mermaid = False
            continue

        if in_mermaid:
            matches = node_pattern.finditer(line)
            for match in matches:
                inner_text = match.group(1)
                # Check for unescaped slashes inside the node text
                if re.search(r'(?<!\\)/', inner_text):
                    print(f"Mermaid Validation Error in '{file_path}' at line {i}:")
                    print(f"  Unescaped slash found in node: {line.strip()}")
                    has_error = True

    if has_error:
        sys.exit(1)
    
    print(f"Mermaid validation passed for '{file_path}'.")
    sys.exit(0)

if __name__ == '__main__':
    validate_mermaid(sys.argv[1])
EOF
