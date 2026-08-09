#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# index_codebase.py — Extract semantic structures and update the knowledge graph.

import os
import ast
import json
import sys

WORKSPACE_ROOT = "/home/lord-mahonheim/bifrost/tesla"
GRAPH_PATH = os.path.join(WORKSPACE_ROOT, "memory/knowledge_graph.json")

TARGET_DIRS = ["sandbox", "memory"]
EXCLUDE_DIRS = [".venv", "OUTPUTS", "Avalon", ".git", "sandboxes", "logs", "__pycache__"]

class PythonCodeVisitor(ast.NodeVisitor):
    def __init__(self, rel_path):
        self.rel_path = rel_path
        self.classes = []
        self.functions = []
        self.imports = []
        self.current_class = None

    def visit_ClassDef(self, node):
        class_name = f"{self.rel_path}::{node.name}"
        self.classes.append({
            "name": class_name,
            "simple_name": node.name,
            "line": node.lineno,
            "docstring": ast.get_docstring(node) or "",
            "bases": [ast.unparse(b) for b in node.bases]
        })
        old_class = self.current_class
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        func_name = node.name
        if self.current_class:
            full_name = f"{self.current_class}.{func_name}"
        else:
            full_name = f"{self.rel_path}::{func_name}"
        
        self.functions.append({
            "name": full_name,
            "simple_name": func_name,
            "parent_class": self.current_class,
            "line": node.lineno,
            "docstring": ast.get_docstring(node) or ""
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)


def scan_file_details(abs_path, rel_path):
    # Determine type and extract metadata
    size = os.path.getsize(abs_path)
    try:
        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            line_count = len(lines)
    except Exception:
        line_count = 0

    observations = [
        f"Path: {rel_path}",
        f"Size: {size} bytes",
        f"Lines: {line_count}"
    ]

    # Try extracting top-level comment or description
    desc = ""
    if abs_path.endswith('.py'):
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=abs_path)
                doc = ast.get_docstring(tree)
                if doc:
                    desc = doc.split('\n')[0]
        except Exception:
            pass
    elif abs_path.endswith('.sh'):
        # Get first few comment lines
        comments = []
        for line in lines[:5]:
            if line.startswith('#'):
                cleaned = line.lstrip('#').strip()
                if cleaned and not cleaned.startswith('!'):
                    comments.append(cleaned)
        if comments:
            desc = " | ".join(comments)

    if desc:
        observations.append(f"Description: {desc}")

    return {
        "name": rel_path,
        "entityType": "File",
        "observations": observations
    }


def main():
    print("[*] Starting semantic codebase scan...")
    
    # 1. Load existing knowledge graph
    if os.path.exists(GRAPH_PATH):
        try:
            with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
                graph = json.load(f)
        except Exception as e:
            print(f"[-] Error reading existing graph: {e}")
            graph = {"entities": [], "relations": []}
    else:
        graph = {"entities": [], "relations": []}

    # Keep manual entities/relations (non-code ones)
    retained_types = ["Agent", "User", "Project", "Vault", "Sandbox", "Subagent", "Folder"]
    
    original_entities = graph.get("entities", [])
    original_relations = graph.get("relations", [])
    
    entities = [e for e in original_entities if e.get("entityType") in retained_types]
    
    # Retain relations whose source and destination are both retained entities
    retained_names = {e["name"] for e in entities}
    relations = [
        r for r in original_relations 
        if r.get("from") in retained_names and r.get("to") in retained_names
    ]

    new_entities = []
    new_relations = []

    # Walk directories
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Check if root is in target directories or subdirectories of target directories
        rel_root = os.path.relpath(root, WORKSPACE_ROOT)
        if rel_root == ".":
            # Only scan targeted direct files or proceed to subdirs
            pass
        else:
            first_part = rel_root.split(os.sep)[0]
            if first_part not in TARGET_DIRS:
                continue

        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, WORKSPACE_ROOT)
            
            # Skip if hidden file
            if file.startswith('.'):
                continue
                
            # Scan file metadata
            file_entity = scan_file_details(abs_path, rel_path)
            new_entities.append(file_entity)

            # If it's a Python file, scan internal AST structure
            if file.endswith('.py'):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    
                    tree = ast.parse(source, filename=abs_path)
                    visitor = PythonCodeVisitor(rel_path)
                    visitor.visit(tree)

                    # Add class entities and relations
                    for cls in visitor.classes:
                        cls_obs = [
                            f"Declared in {rel_path} at line {cls['line']}"
                        ]
                        if cls["docstring"]:
                            cls_obs.append(f"Docstring: {cls['docstring'].strip()}")
                        if cls["bases"]:
                            cls_obs.append(f"Inherits from: {', '.join(cls['bases'])}")
                            
                        new_entities.append({
                            "name": cls["name"],
                            "entityType": "Class",
                            "observations": cls_obs
                        })
                        # Relation from file to class
                        new_relations.append({
                            "from": rel_path,
                            "to": cls["name"],
                            "relationType": "declares_class"
                        })

                    # Add function entities and relations
                    for func in visitor.functions:
                        func_obs = [
                            f"Defined in {rel_path} at line {func['line']}"
                        ]
                        if func["docstring"]:
                            func_obs.append(f"Docstring: {func['docstring'].strip()}")
                        if func["parent_class"]:
                            func_obs.append(f"Member of class: {func['parent_class']}")
                            
                        new_entities.append({
                            "name": func["name"],
                            "entityType": "Function",
                            "observations": func_obs
                        })
                        
                        # Relation from file or class to function
                        if func["parent_class"]:
                            new_relations.append({
                                "from": func["parent_class"],
                                "to": func["name"],
                                "relationType": "declares_method"
                            })
                        else:
                            new_relations.append({
                                "from": rel_path,
                                "to": func["name"],
                                "relationType": "declares_function"
                            })

                except Exception as e:
                    print(f"[-] Failed to parse AST for {rel_path}: {e}")

    # Combine retained and new entities
    entities.extend(new_entities)
    relations.extend(new_relations)

    # Save back
    updated_graph = {
        "entities": entities,
        "relations": relations
    }

    try:
        with open(GRAPH_PATH, 'w', encoding='utf-8') as f:
            json.dump(updated_graph, f, indent=2, ensure_ascii=False)
        print(f"[+] Successfully indexed codebase. Saved {len(new_entities)} new entities and {len(new_relations)} relations to {GRAPH_PATH}.")
    except Exception as e:
        print(f"[-] Error writing updated graph: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
