# Scheduler Plan

- **Phase 1 (Parallel execution)**:
  - `node_curator`: Initialize `memory/TAXONOMY.md`.
  - `node_web`: Gather semantic contexts for the taxonomy elements.
- **Phase 2**:
  - `node_writer`: Update `Gestion-de-Chantiers/INDEX.md` and related indexes. Depends on `node_curator`.
  - `node_arcanis`: Consolidate the implementation strategy.
- **Phase 3**:
  - `node_coder`: Implement strict structural validations and update code-based indices.
- **Phase 4**:
  - `node_premortem`: Final sign-off. Check for SGC rules violations.
