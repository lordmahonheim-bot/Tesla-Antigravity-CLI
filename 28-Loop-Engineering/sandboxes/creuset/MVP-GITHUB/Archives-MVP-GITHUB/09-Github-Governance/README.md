# Repository Governance (Vigilum Codex)

## Tesla's Greetings & Nominal Guidelines
In accordance with the project's canonical naming and communication guidelines:
1. All official communications, PRs, and reports address the principal operator as **Mahonheim** or **Lord Mahonheim**. Generic terms like "user" or "operator" are strictly prohibited in user-facing deliverables.
2. The agent is identified as **Tesla**, operating in a quiet, direct, action-first manner.
3. Every session or critical deliverable includes the greeting ritual "Bien le bonjour à toi Mahonheim" and ends with the formal signatures:
   - *Signé / Fait par : Tesla sur Antigravity CLI*
   - *Main rendue à Mahonheim*

## Project Maintenance standards
This project defines repository compliance rules under the doctrine of the Vigilum Codex:
*   **Zero Secrets**: Codebases must be audited to ensure that no hardcoded paths, local environment variables, or private API credentials are committed.
*   **Branching Workflow**: Direct commits or pushes to the `main` branch are strictly forbidden. All features must be developed on normalized branches (`feature/name` or `fix/name`).
*   **Conventional Commits**: Commit messages must respect the format `<type>(<scope>): <description>` (e.g., `feat(scaffolding): deploy local MVP structure`).

## dependabot & CODEOWNERS rules
Repository safety is enforced via:
1. **`CODEOWNERS`**: Configured to assign default ownership of the repository to `@lordmahonheim-bot`, and delegates specific paths (such as `/sandbox/` or `/memory/`) to the agent team `@lordmahonheim-bot/tesla-agent`.
2. **`dependabot.yml`**: Scheduled for weekly automated dependency scans to check for security updates and package updates.
