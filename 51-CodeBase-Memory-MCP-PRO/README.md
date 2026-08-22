![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# CodeBase Memory MCP Pro (MVP 51)

## Présentation

CodeBase Memory MCP Pro est un module avancé d'indexation et d'exploration structurelle du code. Ce composant (MVP 51) s'intègre à l'écosystème TESLA ANTIGRAVITY pour fournir des capacités robustes de mémoire de code.

## Architecture Two-Phase et Technologies

Ce module repose sur le fork C/C++ **win4r** de Codebase Memory et exploite **Tree-sitter** pour le parsing sémantique des AST.
Il s'articule autour d'une architecture stricte en deux phases :
1. **Indexation Hors-Ligne (Offline)** : Exécution d'un balayage complet du dépôt sous un plafond strict de mémoire (`MemoryMax=6G`) avec un `.cbmignore` agressif pour générer les arêtes relationnelles (edges) dans une base SQLite centralisée.
2. **Serveur en Ligne (Online MCP)** : Exposition de la base via le protocole MCP, permettant aux agents de requêter la topologie du code en langage **Cypher**.

## Sécurité et Failsafes (Gatekeeper)

L'intégrité de la machine hôte (MIDGARD) est blindée par trois verrous physiques implémentés au niveau du daemon MCP :
- **Plafond Mémoire Strict (`MemoryMax=4G`)** : Le pont d'exécution MCP est encapsulé dans `systemd-run --scope -p MemoryMax=4G`.
- **Foudroyage Temporel (`timeout 15s`)** : Pour prévenir les boucles infinies ou les produits cartésiens d'une requête Cypher générée par un LLM, le processus est systématiquement killé au bout de 15 secondes.
- **Étanchéité Base de Données (`CBM_SQLITE_MODE=ro`)** : La connexion SQLite du serveur MCP est verrouillée en lecture seule absolue (Read-Only) au niveau du driver. Toute requête de mutation `CREATE/DROP/DELETE` provenant d'un agent sera instantanément rejetée.

## Déploiement et Configuration

Le serveur MCP s'injecte silencieusement dans le manifeste `settings.json` d'Antigravity CLI :
```json
"mcp": {
    "codebase-memory-mcp": {
        "command": "systemd-run",
        "args": [
            "--user", "--scope", "-p", "MemoryMax=4G",
            "timeout", "15s",
            "/home/lord-mahonheim/bifrost/tesla/tools/codebase-memory-mcp-pro/codebase-memory-mcp-pro/build/c/codebase-memory-mcp",
            "mcp"
        ],
        "env": {
            "CBM_SQLITE_MODE": "ro"
        }
    }
}
```
