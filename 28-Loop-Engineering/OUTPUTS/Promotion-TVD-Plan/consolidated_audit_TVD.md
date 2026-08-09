---
type: reference
tags: [curation/certified, curator/prime, status/valid, tvd, video, audit]
coterie: tesla
date: 2026-07-19
author: tesla-curator-prime
confidence_score: 95%
sources: 
  - "[[Audit-Promotion-TVD-By-Apodex.md]]"
  - "[[Audit-Promotion-TVD-By-ChatGPT.txt]]"
  - "[[Audit-Promotion-TVD-By-GEMINI.txt]]"
  - "[[Audit-Promotion-TVD-By-RENA.md]]"
  - "[[Tesla-Video-Director-Report_2026-07-19.md]]"
---

# CERTIFIED REPORT: Stratégie d'Intégration OpenCut vs FreeCut pour Tesla-Video-Director

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

## 1. Diagnostic Summary
Ce rapport consolide l'analyse de quatre audits externes (Apodex, ChatGPT, GEMINI, RENA) confrontés aux capacités et contraintes du rapport interne de `tesla-video-director`. L'objectif est de statuer sur le choix d'un moteur de montage automatisé (OpenCut vs FreeCut) pour la ligne de commande Antigravity CLI sur la machine MIDGARD. Le consensus stratégique dicte une approche hybride temporelle : l'adoption conceptuelle et adaptée de **FreeCut** à court terme pour le montage piloté par le texte, tout en conservant **OpenCut** en cible architecturale long-terme dès stabilisation de ses interfaces MCP.

## 2. Verified Facts & Evidence Pack

| Asserted Fact | Primary Source Reference | Confidence |
| :--- | :--- | :--- |
| **Interdiction des modèles locaux lourds** (ex: Whisper, YOLO) pour protéger MIDGARD. | Tesla-Video-Director-Report (Sec 3.B) | 100% |
| **TVD orchestre, Master Code code** : TVD n'écrit pas de code FFmpeg directement. | Tesla-Video-Director-Report (Sec 1) | 100% |
| **OpenCut possède une architecture cible idéale** (Rust, MCP, Headless) mais est en pleine réécriture instable. | Audit RENA, Audit Apodex | 95% |
| **FreeCut est expérimental** (2 commits, pas de release) mais son workflow (Audio → Transcription → EDL → FFmpeg) correspond au pipeline de TVD. | Audit RENA, Audit GEMINI | 95% |
| **FreeCut dépend par défaut de Whisper local**, ce qui viole la doctrine de MIDGARD. | Audit RENA, Audit GEMINI | 98% |

## 3. Comparative Reasoning & Hypotheses

*   **L'Alignement Architectural (Le Futur)** : Tous les audits s'accordent à dire qu'OpenCut, avec son serveur MCP et son mode headless annoncés, est la fondation naturelle pour l'orchestration par des agents dans Antigravity CLI. Cependant, la réécriture en cours empêche son déploiement immédiat en production.
*   **L'Alignement Opérationnel (Le Présent)** : Le rapport interne stipule que TVD possède des capacités de "Montage piloté par le Texte" (Text-Based Editing). C'est exactement le paradigme de FreeCut. En extrayant la logique de FreeCut (génération d'une EDL à partir d'une transcription textuelle) et en l'associant à l'arsenal existant de TVD (FFmpeg local pour le rendu), on obtient un pipeline fonctionnel immédiat.
*   **L'Hypothèse de Substitution (Le Fix)** : Pour utiliser la logique de FreeCut tout en respectant la contrainte "zéro modèle local" de MIDGARD, il est impératif de bypasser son moteur Whisper local au profit de la **Transcription Enrichie via l'API Gemini** dont dispose déjà TVD.

## 4. Contradictions & System Limits

*   **Contradiction sur l'Automatisation Immédiate** : L'audit GEMINI recommande FreeCut pour un déploiement clé-en-main avec Whisper local, ce qui est en **violation directe** des règles du `Tesla-Video-Director-Report` interdisant les modèles locaux. L'audit RENA corrige cette faille en imposant une adaptation gouvernée de FreeCut (substitution de Whisper par une API).
*   **Limite de Maturité** : FreeCut est perçu comme une simple preuve de concept (PoC) par Apodex et RENA. Il ne peut donc pas être intégré comme dépendance aveugle. Il doit être audité et recréé sous forme d'un adaptateur expérimental (ex: `tesla-freecut-lab`).
*   **Limite d'OpenCut** : Recommandé par ChatGPT et Apodex, OpenCut n'est concrètement pas encore utilisable de manière stable en headless/MCP au moment de cet audit (réécriture en cours).

## 5. Architectural Recommendations

Pour respecter la gouvernance Tesla et maximiser l'efficacité de `tesla-video-director` :

1.  **Cible Court Terme : Pipeline "FreeCut Adapté" (Expérimental)**
    *   Ne pas installer le dépôt FreeCut brut. Extraire sa logique d'EDL (Edit Decision List).
    *   **Pipeline imposé** : Rushes → *Transcription via Gemini API* (bypasser Whisper) → *Analyse sémantique Gemini* → Génération d'une EDL → Validation Humaine → *Rendu FFmpeg local*.
    *   Déléguer la création des scripts adaptateurs Python à `tesla-master-code`.
2.  **Cible Long Terme : OpenCut (Veille Stratégique)**
    *   Maintenir OpenCut sous surveillance. Ne lancer l'intégration que lorsque le mode headless, le serveur MCP et l'API seront stabilisés et documentés.
    *   À terme, remplacer le pipeline expérimental FFmpeg par des requêtes MCP structurées vers le moteur de rendu OpenCut.

---
*Certified and signed on MIDGARD by Tesla Curator Prime.*
