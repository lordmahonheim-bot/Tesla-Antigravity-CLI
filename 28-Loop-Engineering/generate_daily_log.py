import os
import json
from datetime import datetime
from pathlib import Path

# Configuration
TRACKER_FILE = os.getenv("TRACKER_FILE", ".etl_tracker.json")
DELTA_FILE = os.getenv("DELTA_FILE", ".etl_delta.json")
LOGS_DIR = os.getenv("DAILY_LOGS_DIR", "Avalon/_MOC/Daily_Logs")

def format_yaml_frontmatter(date_str: str) -> str:
    yaml = "---\n"
    yaml += "tags:\n"
    yaml += "  - daily-log\n"
    yaml += "  - etl\n"
    yaml += f"date: {date_str}\n"
    yaml += "connections:\n"
    yaml += "  - \"[[session_to_graph]]\"\n"
    yaml += "---\n"
    return yaml

def generate_daily_log():
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    log_filename = f"Daily_Log_{date_str}.md"
    log_filepath = Path(LOGS_DIR) / log_filename
    
    # Load delta to get newly ingested files
    delta = {"files_processed_today": 0}
    if os.path.exists(DELTA_FILE):
        with open(DELTA_FILE, 'r', encoding='utf-8') as f:
            try:
                delta = json.load(f)
            except json.JSONDecodeError:
                pass
                
    files_processed = delta.get("files_processed_today", 0)
    
    is_new_file = not log_filepath.exists()
    
    with open(log_filepath, 'a', encoding='utf-8') as f:
        if is_new_file:
            f.write(format_yaml_frontmatter(date_str))
            f.write(f"# Daily Log: {date_str}\n\n")
            f.write("## ETL Operations\n\n")
        
        f.write(f"### Run at {time_str}\n")
        f.write(f"- **Nouveaux transcripts ingérés** : {files_processed}\n")
        f.write("- **Pipeline** : `session_to_graph.py` exécuté.\n\n")
        
    print(f"Appended daily log at {log_filepath}")
    
    # Reset delta after reading to avoid counting them again if log runs multiple times without ETL
    with open(DELTA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"files_processed_today": 0}, f)

if __name__ == "__main__":
    generate_daily_log()
