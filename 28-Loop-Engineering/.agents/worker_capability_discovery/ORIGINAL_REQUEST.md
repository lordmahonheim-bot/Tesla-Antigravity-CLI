## 2026-07-10T00:41:00+01:00
You are a worker agent assigned to execute Milestone 1: Capability Discovery for the Tesla/Antigravity Loop Engineering project.
Your working directory is: `/home/lord-mahonheim/bifrost/tesla/.agents/worker_capability_discovery/`

Perform the following tasks:
1. Initialize your `progress.md` at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_capability_discovery/progress.md` and keep it updated.
2. Investigate the environment and inventory:
   - Existing skills under `/home/lord-mahonheim/bifrost/tesla/.agents/skills/` (their roles, purpose, and status).
   - Available MCP servers and their tools (e.g. check MCP schema/instructions under `/home/lord-mahonheim/.gemini/antigravity-cli/mcp/` or system environment).
   - Available system tools on MIDGARD: Check if python3, semgrep, pyright, git, mypy are installed. Document their paths/availability.
   - Existing Python wrappers in the codebase (e.g., look for any wrappers around semgrep, pyright, git, etc.).
   - Current FORCE_TOOLING rules and AGENTS.md content.
3. Generate the file `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/capability_inventory.md` with the gathered data. Ensure the markdown is structured and professional.
4. When done, write a handoff report at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_capability_discovery/handoff.md` and message the parent with the result.

Strictly adhere to the Tesla/Antigravity governance:
- DO NOT CHEAT. All implementations must be genuine.
- Keep progress.md updated.
- Verify the generated inventory file exists and matches requirements.
