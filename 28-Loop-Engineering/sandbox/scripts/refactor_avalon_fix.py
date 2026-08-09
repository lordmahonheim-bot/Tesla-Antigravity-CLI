import os
import shutil
import glob
from pathlib import Path
from datetime import datetime
import frontmatter

def main():
    avalon_dir = Path("/home/lord-mahonheim/bifrost/tesla/Avalon")
    res_dir = avalon_dir / "03-Resources"
    scripts_dir = res_dir / "Scripts"
    
    # 1. Move orphan binary db backup
    db_backup = res_dir / "alexandria_brain.db.pre-tmo-v4-2026-07-10"
    if db_backup.exists():
        scripts_dir.mkdir(exist_ok=True)
        shutil.move(str(db_backup), str(scripts_dir / db_backup.name))
        print(f"Moved {db_backup.name} to {scripts_dir}")

    # 2. Merge GitHub-Best-Practices atomically into 03-Resources
    github_bp = res_dir / "GitHub-Best-Practices"
    if github_bp.exists() and github_bp.is_dir():
        for item in github_bp.iterdir():
            dest = res_dir / item.name
            if not dest.exists():
                shutil.move(str(item), str(res_dir))
            else:
                # If it already exists, just remove the item or rename
                shutil.move(str(item), str(res_dir / f"GBP_{item.name}"))
        shutil.rmtree(github_bp)
        print("Atomically merged GitHub-Best-Practices into 03-Resources")

    # 3. Inject strict symmetrical YAML frontmatter on root orphan notes
    today = datetime.now().strftime("%Y-%m-%d")
    
    for md_file in avalon_dir.glob("*.md"):
        if not md_file.is_file():
            continue
        try:
            post = frontmatter.load(md_file)
            updated = False
            
            # Symmetrical perfect YAML fields
            if "title" not in post.metadata:
                post.metadata["title"] = md_file.stem
                updated = True
            if "aliases" not in post.metadata:
                post.metadata["aliases"] = []
                updated = True
            if "tags" not in post.metadata:
                post.metadata["tags"] = ["#concept"]
                updated = True
            if "type" not in post.metadata:
                post.metadata["type"] = "concept"
                updated = True
            if "status" not in post.metadata:
                post.metadata["status"] = "actif"
                updated = True
            if "created" not in post.metadata:
                post.metadata["created"] = today
                updated = True
            if "updated" not in post.metadata:
                post.metadata["updated"] = today
                updated = True
            if "connections" not in post.metadata:
                if md_file.name != "Avalon.md":
                    post.metadata["connections"] = ['"[[Avalon]]"']
                else:
                    post.metadata["connections"] = ['"[[01-Library]]"', '"[[03-Resources]]"']
                updated = True
                
            if updated or True: # Force write to assure order/keys if needed, though frontmatter might not preserve order
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))
                print(f"Injected strict frontmatter into {md_file.name}")
        except Exception as e:
            print(f"Error processing frontmatter for {md_file.name}: {e}")

if __name__ == '__main__':
    main()
