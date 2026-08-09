import re

with open("memory/liste_projets_antigravity_BASE.md", "r") as f:
    content = f.read()

# Update MVP 16
content = re.sub(
    r'(### 16\. Projet : Tesla-Master-Code \(Expert en Création et Validation de Code Isolé\))',
    r'\1 [CLOS - Supplanté partiellement par MVP 44]',
    content
)

# Append MVP 44 at the end
mvp_44 = """
### 44. MVP 44 - Tesla-Code-Auditor [EN COURS]
*   **Objectif & Usage :** Déployer une entité de validation et d'audit impartial (Code-Auditor) orchestrée par Loop-Engineering pour garantir le Self-Healing et la validation LSP obligatoire avant restitution.
*   **Réalisations techniques :**
    *   Validation des fichiers canoniques (AGENTS.md, FORCE_TOOLING.md, GEMINI.md, ENGINE.md).
    *   Création des règles de gouvernance pour le Cycle ACT-VERIFY-LEARN-REPEAT.
"""
content += mvp_44

with open("memory/liste_projets_antigravity_BASE.md", "w") as f:
    f.write(content)
