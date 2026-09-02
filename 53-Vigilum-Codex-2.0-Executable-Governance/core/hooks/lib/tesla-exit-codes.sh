#!/usr/bin/env bash
# Vigilum Codex 2.1.3 — Codes POSIX normalisés (arbitrage #3 : codes physiques
# uniques + identifiants sémantiques documentés ; aucun alias numérique double).
#
# Identifiants sémantiques (traçabilité documentaire, non exécutables) :
#   ERR_SPEC_LOCKED            -> TESLA_EXIT_LOCK (80)   [L-001]
#   ERR_PUBLIC_STAGING_MISSING -> staging_gate.py (exit 1) [S-002]
#   ERR_AGENT_THEATER          -> TESLA_EXIT_ORCH (81)   [D-007/D-008]
export TESLA_EXIT_OK=0
export TESLA_EXIT_SCHEMA=10
export TESLA_EXIT_SECRET=20
export TESLA_EXIT_SCOPE=30
export TESLA_EXIT_STATE=40
export TESLA_EXIT_MARBLE=50
export TESLA_EXIT_LINT=60
export TESLA_EXIT_UNKNOWN=66
export TESLA_EXIT_PUSH=70
export TESLA_EXIT_LOCK=80
export TESLA_EXIT_ORCH=81
export TESLA_EXIT_DRAFT=90
