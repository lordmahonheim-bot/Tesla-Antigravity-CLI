## 2026-07-10T00:18:42Z
You are a worker agent assigned to synthesize the four independent audit reports (Arcanis, Curator, Master-Code, Premortem) into a consolidated Plan of Intervention.
Your working directory is: `/home/lord-mahonheim/bifrost/tesla/.agents/worker_synthesis/`

Perform the following tasks:
1. Initialize your `progress.md` at your working directory.
2. Read the capability inventory report (`OUTPUTS/capability_inventory.md`) and the four reports in `OUTPUTS/`:
   - `rapport_arcanis_loop_engineering_v1.0_2026-07-10.md`
   - `rapport_curator_loop_engineering_v1.0_2026-07-10.md`
   - `rapport_master-code_loop_engineering_v1.0_2026-07-10.md`
   - `rapport_premortem_loop_engineering_v1.0_2026-07-10.md`
3. Generate the consolidated synthesis plan at `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/plan_intervention_loop_engineering_v1.0_2026-07-10.md`.
   The report must respect the following format:
   - A **Dependency Map** of the components (indicating who depends on what, e.g. text/diagram)
   - A **Sequence Diagram** Mermaid of the complete Act/Verify/Learn/Repeat cycle
   - A **Resource Allocation Table** (mapping agents/skills to each step)
   - A high-level **Plan of Intervention** detailing priorities and sequencing
   - Include any critical mitigations recommended by Premortem (anti-stagnation, AST fallback for SemGrep, SQLite retry backoff).
4. When complete, write a handoff report at `/home/lord-mahonheim/bifrost/tesla/.agents/worker_synthesis/handoff.md` and message the parent with the results.

Strictly adhere to the Tesla/Antigravity governance:
- DO NOT CHEAT. All implementations must be genuine.
- Keep progress.md updated.
