import os
import sys
import json
import hashlib
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import frontmatter

try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
except ImportError:
    genai = None
    ResourceExhausted = Exception

# Configuration
INPUT_DIR = os.getenv("TRANSCRIPTS_DIR", "transcripts")
OUTPUT_DIR = os.getenv("GRAPH_NODES_DIR", "Avalon/_MOC/Graph_Nodes")
TRACKER_FILE = os.getenv("TRACKER_FILE", ".etl_tracker.json")
DELTA_FILE = os.getenv("DELTA_FILE", ".etl_delta.json")

def calculate_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def load_tracker() -> Dict[str, str]:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tracker(tracker: Dict[str, str]):
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(tracker, f, indent=4)

def sanitize_link(link: str) -> str:
    link = link.strip('\"\'')
    if not link.startswith('[['):
        link = f"[[{link}]]"
    return f'"{link}"'

def parse_llm_response(response_text: str) -> List[Dict[str, Any]]:
    try:
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != -1:
            return json.loads(response_text[start:end])
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
    return []

def chunk_text(text: str, max_chars: int = 15000) -> List[str]:
    """Basic chunking by paragraphs to avoid tokens limit/OOM."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < max_chars:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def call_gemini_with_backoff(prompt: str, max_retries: int = 5) -> str:
    if not genai or not os.getenv("GEMINI_API_KEY"):
        return '[{"title": "MockNode", "content": "Mock", "tags": ["mock"], "aliases": [], "links": []}]'
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            wait_time = 2 ** attempt
            print(f"Rate limit hit (429). Waiting {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            break
    return "[]"

def extract_nodes_from_text(text: str) -> List[Dict[str, Any]]:
    chunks = chunk_text(text)
    all_nodes = []
    for chunk in chunks:
        prompt = f"""
        Extract key entities and concepts from the following transcript.
        Format the output as a JSON array of objects. Each object should have:
        - title: A CamelCase, PascalCase, or kebab-case name for the node.
        - content: A brief summary.
        - tags: A list of tags (without #).
        - aliases: A list of alternative names.
        - links: A list of related concepts (names only).
        Do not create empty nodes.
        
        Transcript:
        {chunk}
        """
        response_text = call_gemini_with_backoff(prompt)
        nodes = parse_llm_response(response_text)
        all_nodes.extend(nodes)
    return all_nodes

def write_node(node: Dict[str, Any]):
    title = node.get("title", "").strip()
    if not title: return
    
    filepath = Path(OUTPUT_DIR) / f"{title}.md"
    new_content = node.get("content", "").strip()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    daily_log_link = f"[[Daily_Log_{date_str}]]"

    # Wikilink injection in text
    for link in node.get("links", []):
        link_clean = link.strip('\"\'')
        if not link_clean.startswith('[['):
            link_clean = f"[[{link_clean}]]"
        new_content = new_content.replace(link, link_clean)

    if filepath.exists():
        post = frontmatter.load(filepath)
        
        def as_list(val):
            if val is None: return []
            if isinstance(val, list): return val
            return [val]
            
        existing_tags = set(as_list(post.metadata.get("tags")))
        existing_aliases = set(as_list(post.metadata.get("aliases")))
        existing_connections = set(as_list(post.metadata.get("connections")))
        
        existing_tags.update([f"#vigilum-codex/concept" if not t.startswith("#") else t for t in node.get("tags", [])])
        existing_aliases.update(node.get("aliases", []))
        existing_connections.update([sanitize_link(l) for l in node.get("links", [])])
        
        post.metadata["tags"] = list(existing_tags)
        post.metadata["aliases"] = list(existing_aliases)
        post.metadata["connections"] = list(existing_connections)
        
        # Append strategy
        if new_content and new_content not in post.content:
            post.content += f"\n\n## Historique : {daily_log_link}\n\n{new_content}"
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
            
    else:
        post = frontmatter.Post(new_content)
        post.metadata["type"] = "concept"
        post.metadata["status"] = "active"
        post.metadata["tags"] = [f"#vigilum-codex/concept" if not t.startswith("#") else t for t in node.get("tags", [])]
        post.metadata["aliases"] = node.get("aliases", [])
        post.metadata["date_created"] = date_str
        post.metadata["connections"] = [sanitize_link(l) for l in node.get("links", [])]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))

def process_transcript(filepath: str) -> bool:
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    nodes = extract_nodes_from_text(text)
    if not nodes:
        return False
        
    for node in nodes:
        write_node(node)
    return True

def run_etl():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(INPUT_DIR):
        Path(INPUT_DIR).mkdir(parents=True, exist_ok=True)
        return

    tracker = load_tracker()
    new_tracker = tracker.copy()
    
    files = list(Path(INPUT_DIR).glob("*.md")) + list(Path(INPUT_DIR).glob("*.txt"))
    
    files_processed = 0
    for filepath in files:
        fpath = str(filepath)
        fhash = calculate_hash(fpath)
        
        if fpath in tracker and tracker[fpath] == fhash:
            continue
            
        if process_transcript(fpath):
            new_tracker[fpath] = fhash
            files_processed += 1
            time.sleep(2)  # Rate Limiting
            
    save_tracker(new_tracker)
    
    # Save delta for daily log
    with open(DELTA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"files_processed_today": files_processed}, f)
    
    print("ETL completed successfully.")

if __name__ == "__main__":
    run_etl()
