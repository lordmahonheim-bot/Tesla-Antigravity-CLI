# Contrats des Agents (Obsidian Graph)

## Contrat N1
**id:** N1
**agent:** tesla-web-raider, tesla-curator-prime
**input:** [Obsidian_Graph_Report.md, liste_projets_antigravity_BASE.md]
**output:** [specifications_graph.md]
**preconditions:** []
**postconditions:** [specs_valid]
**risks:** [api_changes]
**time_estimate_min:** 15
**model_recommended:** gemini-flash

## Contrat N2
**id:** N2
**agent:** tesla-arcanis-360, premortem
**input:** [specifications_graph.md]
**output:** [premortem_obsidian_graph.md, architecture_valid.md]
**preconditions:** [specs_valid]
**postconditions:** [risks_mitigated]
**risks:** [OOM, infinite_loops]
**time_estimate_min:** 20
**model_recommended:** claude-sonnet

## Contrat N3
**id:** N3
**agent:** tesla-master-code
**input:** [architecture_valid.md]
**output:** [session_to_graph.py, generate_daily_log.py]
**preconditions:** [lsp_clean, git_clean]
**postconditions:** [tests_green, no_lsp_errors]
**risks:** [regression_api]
**time_estimate_min:** 45
**model_recommended:** claude-sonnet

## Contrat N4
**id:** N4
**agent:** tesla-arcanis-360, tesla-curator-prime, premortem
**input:** [session_to_graph.py, generate_daily_log.py]
**output:** [INDEX.md_updated, certification_seal]
**preconditions:** [tests_green]
**postconditions:** [mission_archived]
**risks:** []
**time_estimate_min:** 15
**model_recommended:** claude-opus
