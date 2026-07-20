# Obsidian Graph Relationnel

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

A relational graph generator and visualizer for Obsidian vaults, built to map complex interconnected notes and ideas.

## Prerequisites & Quick Install

- **Python 3.12+**
- Obsidian Vault directory structure

```bash
git clone https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI.git
cd Tesla-Antigravity-CLI
pip install -r requirements.txt
```

## Usage & Examples

Run the generator on your local Obsidian vault to instantly produce a relational node graph:

```bash
python generate_graph.py --vault-path /path/to/your/obsidian/vault --output graph.html
```

## Architecture & Design Decisions

The application uses standard Markdown parsing to extract `[[]]` wiki-links and builds a directed network graph using `networkx`. The visualization layer is rendered via D3.js or `pyvis` for interactive exploration. This approach ensures maximum compatibility with existing Obsidian workflows without requiring a dedicated plugin.

## Contribution & Governance

We welcome contributions! Please refer to the `CONTRIBUTING.md` file for guidelines. Ensure all pull requests follow Conventional Commits and pass the CI checks before requesting a review.
