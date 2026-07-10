import json
import sqlite3
import os

DB_PATH = '/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db'

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for raw structural nodes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS understand_nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            name TEXT,
            semantic_summary TEXT
        )
    ''')
    # Table for structural edges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS understand_edges (
            source TEXT,
            target TEXT,
            type TEXT
        )
    ''')
    conn.commit()
    return conn

def ingest_graph(filepath='code_graph.json'):
    if not os.path.exists(filepath):
        print(f"Graph file {filepath} not found.")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        graph = json.load(f)
        
    conn = setup_db()
    cursor = conn.cursor()
    
    # Ingest Nodes
    for node in graph.get('nodes', []):
        cursor.execute('''
            INSERT OR IGNORE INTO understand_nodes (id, type, name, semantic_summary)
            VALUES (?, ?, ?, ?)
        ''', (node['id'], node['type'], node['name'], 'PENDING_SEMANTIC_ENRICHMENT'))
        
    # Ingest Edges
    for edge in graph.get('edges', []):
        cursor.execute('''
            INSERT INTO understand_edges (source, target, type)
            VALUES (?, ?, ?)
        ''', (edge['source'], edge['target'], edge['type']))
        
    conn.commit()
    conn.close()
    print("Graph ingested into Alexandria successfully.")

if __name__ == '__main__':
    ingest_graph()
