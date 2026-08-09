# Scheduler Plan

**Phase 1: Pre-Execution (Scrubbing & Planning)**
- `Tesla-Team-Synergy` initiates the sequence.
- `Tesla-Arcanis-360` gathers required docs (async).
- `Tesla-Curator-Prime` sanitizes the inputs (depends on Arcanis).

**Phase 2: Network & Environment**
- `Tesla-Web-Raider` establishes the PR staging listener (depends on Curator).

**Phase 3: Generation (Cloud Delegate)**
- Jules executes the heavy generation and returns the artifact via PR.

**Phase 4: Local Ingestion & Sandbox**
- `Tesla-Master-Code` pulls the PR into a sandbox.
- Runs Pyright, SemGrep, and formatters. Self-heals if needed. (depends on Jules PR)

**Phase 5: Veto & Wrap-up**
- `Tesla-PREMORTEM` evaluates the merged result. (depends on Master-Code)
- `Tesla-Writing-Skills` generates the changelog. (depends on Premortem)
