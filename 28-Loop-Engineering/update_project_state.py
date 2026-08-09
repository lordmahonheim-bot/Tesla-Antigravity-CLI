import datetime
import re

with open("memory/PROJECT_STATE.md", "r") as f:
    content = f.read()

# Update Last Action
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
content = re.sub(
    r'- \*\*Horodatage de Clôture\*\* : .*',
    f'- **Horodatage de Clôture** : {now_str}',
    content
)

content = re.sub(
    r'- \*\*Dernière Action \(.*?\)\*\* : .*',
    f'- **Dernière Action ({now_str.split()[0]})** : Exécution du Noeud 3 du Plan : Mise à jour des fichiers canoniques (AGENTS, FORCE_TOOLING, GEMINI, ENGINE), mise à jour du SGC MVP 44 (Tesla-Code-Auditor), et ancrage mémoire.',
    content
)

with open("memory/PROJECT_STATE.md", "w") as f:
    f.write(content)

