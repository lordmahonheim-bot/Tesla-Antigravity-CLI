import os
import json
import ast

def parse_file(filepath):
    nodes = []
    edges = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                nodes.append({"id": f"{filepath}::{node.name}", "type": "function", "name": node.name})
            elif isinstance(node, ast.ClassDef):
                nodes.append({"id": f"{filepath}::{node.name}", "type": "class", "name": node.name})
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append({"source": filepath, "target": alias.name, "type": "imports"})
    except Exception as e:
        pass
    return nodes, edges

if __name__ == '__main__':
    all_nodes = []
    all_edges = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                n, e = parse_file(os.path.join(root, file))
                all_nodes.extend(n)
                all_edges.extend(e)
    
    with open('code_graph.json', 'w') as f:
        json.dump({"nodes": all_nodes, "edges": all_edges}, f, indent=2)
