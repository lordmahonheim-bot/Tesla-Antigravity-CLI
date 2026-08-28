#!/usr/bin/env bash
export TESLA_EXIT_OK=0
export TESLA_EXIT_SCHEMA=10
export TESLA_EXIT_SECRET=20
export TESLA_EXIT_SCOPE=30
export TESLA_EXIT_STATE=40
export TESLA_EXIT_MARBLE=50
export TESLA_EXIT_LINT=60
export TESLA_EXIT_UNKNOWN=66
export TESLA_EXIT_PUSH=70

# Vigilum Codex 2.1.1 — plan Sovereign Shield : aliases sémantiques.
# Les codes physiques (80/81/90) restent la référence exécutable ; les codes
# 71/72/73 du plan sont exposés comme alias pour la traçabilité documentaire.
export TESLA_EXIT_SPECLOCK=71    # Plan L-001 : alias sémantique de TESLA_EXIT_LOCK (80)
export TESLA_EXIT_STAGING=72     # Plan S-002 : vérificateur staging public (pipeline, staging_gate.py)
export TESLA_EXIT_THEATER=73     # Plan D-007/D-008 : alias sémantique de TESLA_EXIT_ORCH (81)

export TESLA_EXIT_LOCK=80
export TESLA_EXIT_ORCH=81
export TESLA_EXIT_DRAFT=90
