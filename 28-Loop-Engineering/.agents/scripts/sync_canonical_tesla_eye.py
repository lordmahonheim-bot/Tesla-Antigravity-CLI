import json
import os

# 1. Update TESLA.json
with open("/home/lord-mahonheim/bifrost/tesla/memory/TESLA.json", "r") as f:
    data = json.load(f)
if "Tesla-Eye" not in data["modules"]["registered"]:
    data["modules"]["registered"].append("Tesla-Eye")
with open("/home/lord-mahonheim/bifrost/tesla/memory/TESLA.json", "w") as f:
    json.dump(data, f, indent=2)

# 2. Update settings.json
with open("/home/lord-mahonheim/bifrost/tesla/memory/settings.json", "r") as f:
    data2 = json.load(f)
eye_perm = {"action": "command", "target": "python3 /home/lord-mahonheim/bifrost/tesla/.agents/scripts/tesla_eye.py"}
if eye_perm not in data2.get("permissions", {}).get("allow", []):
    data2.setdefault("permissions", {}).setdefault("allow", []).append(eye_perm)
with open("/home/lord-mahonheim/bifrost/tesla/memory/settings.json", "w") as f:
    json.dump(data2, f, indent=2)

# 3. Update AGENTS.md
path_agents = "/home/lord-mahonheim/bifrost/tesla/memory/AGENTS.md"
with open(path_agents, "r") as f:
    content = f.read()
target_agents = "Validation impartiale de code (impartial gatekeeper code validator) tesla-code-auditor (Skill)"
replace_agents = target_agents + "\n  Inspection visuelle d'écran (UI/GUI debugging et OCR) tesla-eye (Outil Natif)"
if "tesla-eye" not in content and target_agents in content:
    content = content.replace(target_agents, replace_agents)
    with open(path_agents, "w") as f:
        f.write(content)

# 4. Update FORCE_TOOLING.md
path_ft = "/home/lord-mahonheim/bifrost/tesla/memory/FORCE_TOOLING.md"
with open(path_ft, "r") as f:
    content_ft = f.read()
target_ft = "2. **Anti-Lecture Linéaire (Économie de Tokens) :**"
replace_ft = "2. **Anti-Lecture Linéaire (Économie de Tokens) :**\n   - *Corollaire Visuel (Tesla-Eye)* : En cas de blocage avec une interface graphique (Obsidian, Terminal, GUI local), interdiction de deviner l'état du système. Obligation d'invoquer le script `tesla_eye.py` pour effectuer une capture visuelle et l'analyser de façon déterministe avant toute altération."
if "tesla_eye.py" not in content_ft and target_ft in content_ft:
    content_ft = content_ft.replace(target_ft, replace_ft)
    with open(path_ft, "w") as f:
        f.write(content_ft)

# 5. Update ENGINE.md
path_engine = "/home/lord-mahonheim/bifrost/tesla/memory/ENGINE.md"
if os.path.exists(path_engine):
    with open(path_engine, "r") as f:
        content_e = f.read()
    if "Tesla-Eye" not in content_e:
        content_e += "\n\n## Extension Sensorielle Multimodale (Tesla-Eye)\nLe moteur cognitif est désormais couplé à la vision artificielle (Tesla-Eye). Lors de l'analyse d'une capture d'écran, l'ENGINE a l'interdiction de poétiser la description. Il doit se concentrer sur l'identification chirurgicale d'états d'interfaces (boutons, codes d'erreur, structures de graphes) et traduire directement ce stimulus en action exécutive."
        with open(path_engine, "w") as f:
            f.write(content_e)

print("Synchronisation massive terminée.")
