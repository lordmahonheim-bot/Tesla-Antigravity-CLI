import json
import os

# 1. Update TESLA.json
path_json = "/home/lord-mahonheim/bifrost/tesla/memory/TESLA.json"
with open(path_json, "r") as f:
    data = json.load(f)

modules_to_add = [
    "Master Code",
    "Video Director",
    "Loop Orchestrator",
    "Code Auditor",
    "Team Synergy",
    "Curator Prime",
    "Reddit Commander",
    "Voice Tesla",
    "Writing Skills",
    "Understand Graph"
]

added_modules = 0
for mod in modules_to_add:
    if mod not in data["modules"]["registered"]:
        data["modules"]["registered"].append(mod)
        added_modules += 1

with open(path_json, "w") as f:
    json.dump(data, f, indent=2)

print(f"Added {added_modules} modules to TESLA.json")

# 2. Update AGENTS.md
path_agents = "/home/lord-mahonheim/bifrost/tesla/memory/AGENTS.md"
with open(path_agents, "r") as f:
    content = f.read()

# Append to the delegation table
# We find the table by looking for "tesla-eye (Outil Natif)" which we added earlier.
target_agents = "Inspection visuelle d'écran (UI/GUI debugging et OCR) tesla-eye (Outil Natif)"
new_entries = [
    "  Automatisation et publication sur Reddit tesla-reddit-commander (Skill)",
    "  Contrôle vocal asynchrone et transcription voice-tesla (Outil Natif)",
    "  Optimisation et TDD de compétences tesla-writing-skills (Skill)",
    "  Analyse AST et génération de graphes de code tesla-understand-graph (Outil/Skill)"
]

replace_agents = target_agents
for entry in new_entries:
    if entry.split()[0] not in content and entry.split()[-2] not in content:
        replace_agents += "\n" + entry

if replace_agents != target_agents and target_agents in content:
    content = content.replace(target_agents, replace_agents)
    with open(path_agents, "w") as f:
        f.write(content)
    print("Updated AGENTS.md delegation table.")
else:
    print("AGENTS.md table already up to date or target not found.")

