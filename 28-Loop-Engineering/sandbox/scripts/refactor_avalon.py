import os
import shutil
import glob
from pathlib import Path
import frontmatter

def main():
    avalon_dir = Path("/home/lord-mahonheim/bifrost/tesla/Avalon")
    
    # 1. Merge Archives into 04-Archives
    old_archives = avalon_dir / "Archives"
    new_archives = avalon_dir / "04-Archives"
    
    if old_archives.exists() and old_archives.is_dir():
        new_archives.mkdir(exist_ok=True)
        for item in old_archives.iterdir():
            dest = new_archives / item.name
            if dest.exists():
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    item.replace(dest)
            else:
                shutil.move(str(item), str(new_archives))
        shutil.rmtree(old_archives)
        print(f"Merged {old_archives} into {new_archives}")

    # 2. Move Antigravity-Agent-Design to 01-Library
    agent_design = avalon_dir / "Antigravity-Agent-Design"
    lib_dir = avalon_dir / "01-Library"
    if agent_design.exists() and agent_design.is_dir():
        lib_dir.mkdir(exist_ok=True)
        shutil.move(str(agent_design), str(lib_dir / "Antigravity-Agent-Design"))
        print(f"Moved Antigravity-Agent-Design to 01-Library")

    # 3. Move GitHub-Best-Practices to 03-Resources
    github_bp = avalon_dir / "GitHub-Best-Practices"
    res_dir = avalon_dir / "03-Resources"
    if github_bp.exists() and github_bp.is_dir():
        res_dir.mkdir(exist_ok=True)
        shutil.move(str(github_bp), str(res_dir / "GitHub-Best-Practices"))
        print(f"Moved GitHub-Best-Practices to 03-Resources")

    # 4. Move *.py and *.db from 03-Resources to 03-Resources/Scripts
    scripts_dir = res_dir / "Scripts"
    if res_dir.exists():
        for ext in ["*.py", "*.db"]:
            for f in res_dir.glob(ext):
                scripts_dir.mkdir(exist_ok=True)
                shutil.move(str(f), str(scripts_dir / f.name))
                print(f"Moved {f.name} to {scripts_dir}")

    # 5. Inject YAML frontmatter on orphan files in root
    # such as Avalon.md, COHERENCE_LOG.md, SYNC_LOG.md, DÉPLOIEMENT DU ROUTEUR...
    for md_file in avalon_dir.glob("*.md"):
        if not md_file.is_file():
            continue
        try:
            post = frontmatter.load(md_file)
            updated = False
            
            if "title" not in post.metadata:
                post.metadata["title"] = md_file.stem
                updated = True
            if "type" not in post.metadata:
                post.metadata["type"] = "concept"
                updated = True
            if "status" not in post.metadata:
                post.metadata["status"] = "actif"
                updated = True
            if "connections" not in post.metadata:
                # Add a default link to Avalon.md if not Avalon.md
                if md_file.name != "Avalon.md":
                    post.metadata["connections"] = ['"[[Avalon]]"']
                else:
                    post.metadata["connections"] = ['"[[01-Library]]"', '"[[03-Resources]]"']
                updated = True
                
            if updated:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))
                print(f"Injected frontmatter into {md_file.name}")
        except Exception as e:
            print(f"Error processing frontmatter for {md_file.name}: {e}")

if __name__ == '__main__':
    main()
