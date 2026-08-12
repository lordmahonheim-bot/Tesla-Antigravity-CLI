# Tesla-Forge-Cloud (MVP 47)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Tesla-Forge-Cloud** est un serveur Model Context Protocol (MCP) basé sur FastMCP permettant l'instanciation et l'orchestration Zero-Trust d'environnements de développement cloud éphémères (E2B Sandboxes) depuis la station locale MIDGARD.

## 🚀 Prérequis & Installation Rapide

**Audience cible :** Agents d'exécution locaux (Tesla, Master-Code) nécessitant un environnement d'exécution distant hautement outillé sans compromettre le système hôte.

### Prérequis
- `uv` (Gestionnaire de paquets Python 3.12+)
- Clé API E2B (`E2B_API_KEY` dans l'environnement)
- Template E2B `tesla-forge-v1` buildé

### Configuration MCP Locale
Pour déclarer le serveur MCP dans l'écosystème Antigravity (`~/.gemini/antigravity-cli/mcp_config.json`) :

```json
{
  "mcpServers": {
    "tesla-forge-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-forge-mcp",
        "server.py"
      ],
      "env": {
        "E2B_API_KEY": "e2b_..."
      }
    }
  }
}
```

## 🛠 Usage & Exemples (Outils MCP Exposés)

Le module expose **6 outils natifs** via FastMCP pour le pilotage de la sandbox :

1. `create_forge()` : Instancie une nouvelle sandbox `tesla-forge-v1` (Timeout 300s).
2. `forge_exec(command: str)` : Exécute une commande shell arbitraire.
3. `forge_write_file(path: str, content: str)` : Écrit un fichier distant.
4. `forge_read_file(path: str)` : Lit un fichier distant.
5. `forge_sync_to_midgard(remote_path: str, local_path: str)` : Rapatrie un fichier sur MIDGARD en toute sécurité.
6. `forge_destroy()` : Termine la session de la sandbox.

### Workflow d'Orchestration Type

```mermaid
sequenceDiagram
    participant Agent as Tesla-Master-Code
    participant MCP as Tesla-Forge-MCP
    participant E2B as E2B Cloud Sandbox
    
    Agent->>MCP: call create_forge()
    MCP->>E2B: instanciate "tesla-forge-v1"
    E2B-->>MCP: Sandbox ID
    Agent->>MCP: call forge_exec("npm run build")
    MCP->>E2B: process.start()
    E2B-->>MCP: Stdout / Stderr
    Agent->>MCP: call forge_sync_to_midgard("/dist/out.js", "./out.js")
    MCP->>E2B: filesystem.read_bytes()
    E2B-->>MCP: stream
    MCP->>Agent: Fichier rapatrié (Zero-Trust)
    Agent->>MCP: call forge_destroy()
    MCP->>E2B: kill()
```

## 📐 Architecture & Design Decisions

Le serveur utilise `mcp.server.fastmcp.FastMCP` pour exposer rapidement les fonctions Python.
L'environnement cloud (template `tesla-forge-v1`) est basé sur `ubuntu:24.04` et embarque le SDK E2B. 
Le Dockerfile associé provisionne un outillage massif non-interactif :
- `python3.12`, `pip`, `venv`
- `nodejs 20.x`
- `ripgrep (rg)`, `fd-find (fd)`, `curl`, `wget`
- `just` (Command runner)

La décision d'utiliser **E2B** au lieu de conteneurs locaux (Docker) s'inscrit dans la doctrine de préservation des ressources (CPU/RAM) de la station locale MIDGARD. L'isolation est stricte : les dépendances lourdes sont exécutées à distance et seuls les artefacts générés sont rapatriés.

## 🛡 Sécurité & Résilience

- **Pattern Broker & Zero-Trust :** Les agents ne peuvent exécuter le code qu'au travers des 6 verrous (outils) MCP. Le rapatriement de fichiers (`forge_sync_to_midgard`) est le seul pont unidirectionnel vers l'hôte.
- **Fail-Closed & Timeout :** La sandbox est configurée avec un `timeout` absolu de 300 secondes. En cas de blocage d'un agent, l'environnement se détruit automatiquement (auto-kill).
- **ID LOCKED :** La clé API E2B n'est jamais exposée aux agents. Elle réside hermétiquement dans l'environnement (`os.getenv`) injecté par le fichier de configuration MCP.

## 🤝 Contribution & Gouvernance

L'évolution de ce module est régie par le **Vigilum Codex**.
- **Anglais strict** pour toute future documentation technique.
- Modification du module assujettie à la **Règle 12 (Double Copie)** (Synchro MIDGARD / MVP-GITHUB).
- Tout nouveau endpoint MCP doit être accompagné de la mise à jour correspondante dans les graphes Mermaid.
