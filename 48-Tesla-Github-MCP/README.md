# Tesla-Github-MCP (MVP 48)

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

**Tesla-Github-MCP** implements a Dual Instantiation Model Context Protocol (MCP) server architecture. It strictly segregates GitHub authority between agents, ensuring absolute Zero-Trust hardware-level constraints.

## 📐 Architecture & Dual Instantiation

The ecosystem relies on deploying two separate local MCP servers pointing to the same `@modelcontextprotocol/server-github` NPM package but configured with different authentication environments:

1. **`github-manager` Server**: Powered by a GitHub Token (PAT or OAuth) with full mutation rights. Exclusively routed to the `tesla-github-manager` agent.
2. **`github-arcanis` Server**: Powered by a Fine-Grained PAT strictly restricted to Read-Only access. Exclusively routed to the `tesla-arcanis-360` agent for OSINT tasks.

By enforcing tool namespace prefixes (`github-manager_*` vs `github-arcanis_*`), any cognitive error attempting unauthorized writes is physically blocked by the GitHub API (403 Forbidden).

## 🛡 Security & Resilience

- **Hardware-Level Isolation**: Read-Only restrictions are not just enforced via agent prompts; they are hardcoded into the Fine-Grained PAT, providing a fail-closed boundary against unauthorized mutations.
- **Zero-Trust Segregation**: Tokens are isolated securely in local environment variables and independently fed to their respective MCP server instance.

## 🤝 Contribution & Governance

The evolution of this module is governed by the **Vigilum Codex**.
- **Strict English** for all future technical documentation.
- Module modifications are subject to **Rule 12 (Double Copy)** (MIDGARD / MVP-GITHUB Sync).
