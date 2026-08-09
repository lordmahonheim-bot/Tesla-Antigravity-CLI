---
type: chantier
tags: [chantier/actif, cognitif/deep-research, architecture/subagent, statut/actif]
date_ouverture: 2026-06-30
date_derniere_maj: 2026-06-30
version: 1.0
statut: "Actif"
parent: null
enfants: []
remplace: "PLAN-ARMEMENT-COGNITIF_v1.0_2026-06-29.md"
---

# 🔬 CHANTIER : TESLA-ARCANIS
**Ouvert le :** 2026-06-30  
**Dernière mise à jour :** 2026-06-30  
**Statut :** 🔵 Actif — Phase 1 validée  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Idée Initiale (Genèse du Chantier)

> *« Comment rendre Tesla (Gemini sur Antigravity CLI) un spécialiste de l'analyse de document et de la documentation ? »*
> — Lord Mahonheim

L'idée fondatrice : faire muter Tesla d'un agent conversationnel réactif en un **chercheur virtuel de haute précision**. Contrairement aux IA classiques qui génèrent une réponse instantanée depuis leurs données d'entraînement, **Tesla Arcanis** planifie une enquête, collecte des preuves, utilise des outils externes, teste des hypothèses et synthétise des résultats certifiés.

Sa signature : **un comité de lecture intégré** — Arcanis valide chaque étape de son raisonnement avant de passer à la suivante.

---

## 2. Description du Chantier

**Tesla Arcanis** est le nom complet du sous-agent de deep research de l'écosystème Bifrost.

Ce chantier **remplace et étend** le Chantier 002 (Plan d'Armement Cognitif). Il en reprend la vision (spécialisation documentaire) mais lui confère une identité, une architecture, et une méthodologie propres et définitives.

### Périmètre
- Conception et déploiement d'Arcanis comme **Subagent Dédié** (Option 2 du brief).
- Tesla reste l'orchestrateur généraliste, agile, quotidien.
- Arcanis est instancié par Tesla uniquement lorsque la complexité documentaire l'exige.

### Hors périmètre
- Mutation globale du prompt Tesla (Option 1 — rejetée).
- Simple skill `/arcanis` sans posture propre (Option 3 — rejetée).
- Infrastructure Hardware (domaine du Plan Pluridisciplinaire).

### Étymologie opérationnelle
| Racine | Signification | Traduction méthodologique |
|---|---|---|
| **Arc-** | Arc électrique, foudre | L'étincelle de la recherche — déclencheur, jamais conclusion |
| **Arcan-** | Arcane, savoir enfoui | Exhumer les vérités cachées, croiser les sources occultées |
| **-is** | Suffixe latin d'entité (Anubis, Thothis) | L'agent comme comité de lecture institutionnel et intemporel |

---

## 3. Objectif Cible (Définition du Succès)

Tesla peut invoquer Arcanis avec une commande simple face à un sujet complexe. Arcanis déploie alors sa méthodologie en 5 étapes et produit un **livrable de référence** — dense, sourcé, certifié.

**Signature finale de chaque livrable Arcanis :**
> *Arcanis. Enquête planifiée. Hypothèses testées. Sources croisées. Livrable certifié.*
> — Validé par Arcanis. Archive de référence.

---

## 4. Hiérarchie
- **Parent :** Aucun (chantier racine)
- **Remplace :** `PLAN-ARMEMENT-COGNITIF_v1.0_2026-06-29.md` (Chantier 002 — absorbé et étendu)
- **Enfants :** À définir selon les phases — architecture, implémentation, tests

---

## 5. Méthodologie Arcanis (Deep Research en 5 Étapes)

| Étape | Nom | Description |
|---|---|---|
| **1** | Planification de l'enquête | L'agent cartographie le sujet et élabore une stratégie d'investigation avant toute rédaction |
| **2** | Collecte de preuves & Outils externes | Extraction de faits tangibles via outils (FTS5, read_url, grep, pipelines CLI) |
| **3** | Formulation & Test d'hypothèses | Chaque piste est traitée comme une hypothèse scientifique à valider ou réfuter par les données |
| **4** | Comité de lecture intégré (Vérification) | Arcanis valide rigoureusement chaque étape de son raisonnement avant de passer à la suivante |
| **5** | Synthèse & Certification | Production du rapport de référence, contresigné par l'agent |

---

## 6. Architecture Technique Cible

**Approche retenue : Subagent Dédié (Option 2)**

```
[ Tesla — Orchestrateur Généraliste ]
         │
         │ Détecte un besoin de deep research
         │ (document complexe, audit, analyse multi-sources)
         ▼
[ Tesla instancie Arcanis ]
         │
         ▼
[ Arcanis — Subagent Deep Research ]
    ├── Charge ses outils spécialisés (RAG, web search, pipelines)
    ├── Déploie la méthodologie en 5 étapes
    ├── Produit le livrable certifié
    └── Rend la main à Tesla (résumé + fichier dans OUTPUTS/)
```

**Avantages architecturaux :**
- Économie de tokens maximale : la grosse artillerie n'est sortie que si nécessaire.
- Tesla reste léger et agile pour le quotidien.
- Arcanis peut charger des outils lourds sans encombrer la mémoire de travail de Tesla.

---

## 7. Phases & Calendrier

| Phase | Description | Livrable | Statut |
|---|---|---|---|
| **Phase 1** | Audit et alignement de l'Arsenal MIDGARD (poppler-utils, pandoc, ffmpeg) | Fiche de diagnostic d'intégrité de l'arsenal | ✅ Validée (30/06) |
| **Phase 2** | Déploiement de Whisper.cpp pour la transcription locale | Script wrapper `transcribe_local.py` + fiche | ✅ Validée (30/06) |
| **Phase 3** | Modélisation et enregistrement du Subagent Arcanis | Prompt de posture `arcanis_soul.md` + define | ✅ Validée (30/06) |
| **Phase 4** | Exercice de validation grandeur réelle | Premier rapport de deep research certifié dans OUTPUTS/ | ✅ Validée (30/06) |

---

## 8. TODO List

- [x] **[Phase 1]** Obtenir la validation de Lord Mahonheim sur le plan d'intervention
- [x] **[Phase 1]** Exécuter le script de diagnostic des packages documentaires (`pdftotext`, `pandoc`, `ffmpeg`)
- [x] **[Phase 1]** Installer les utilitaires système manquants sur l'hôte MIDGARD
- [x] **[Phase 1]** Rédiger la fiche de diagnostic de l'arsenal dans `OUTPUTS/`
- [x] **[Phase 2]** Télécharger et compiler `whisper.cpp` localement
- [x] **[Phase 2]** Télécharger le modèle Whisper `base` (141 Mo, adapté à la RAM au lieu de `small`)
- [x] **[Phase 2]** Écrire le script Python wrapper `transcribe_local.py`
- [x] **[Phase 2]** Tester la transcription sur un fichier audio court de référence (`jfk.wav`)
- [x] **[Phase 3]** Rédiger le prompt système de posture `arcanis.md` (déposé dans `.agents/arcanis.md`)
- [x] **[Phase 3]** Déclarer Arcanis via la commande `define_subagent`
- [x] **[Phase 3]** Configurer les outils à exposer à Arcanis (RAG, web search, local tools)
- [x] **[Phase 4]** Sélectionner un document complexe de test avec Lord Mahonheim (Audit RAG Alexandria)
- [x] **[Phase 4]** Instancier Arcanis via `invoke_subagent` (via le protocole Avatar validé)
- [x] **[Phase 4]** Auditer le livrable final d'Arcanis (respect du pipeline, des sources et de la signature)
- [x] **[Formalisation]** Archiver officiellement le Chantier 002 (Plan d'Armement Cognitif) comme absorbé

---

## 9. Ressources & Fichiers Liés

| Ressource | Lien | Type |
|---|---|---|
| Brief initial | `/home/lord-mahonheim/Documents/SyncThing/Tesla/Tesla ARCANIS.txt` | Source |
| Plan d'Intervention Ultime v3.0 | `OUTPUTS/plan_intervention_tesla_arcanis-Updated.md` | Livrable (Plan) |
| Rapport Premortem | `OUTPUTS/premortem_tesla_arcanis.md` | Livrable (Sécurité) |
| Fiche diagnostic Arsenal | `OUTPUTS/fiche_diagnostic_arsenal_arcanis.md` | Livrable (Phase 1) |
| Fiche technique Transcription | `OUTPUTS/fiche_technique_transcription_arcanis.md` | Livrable (Phase 2) |
| Fiche enregistrement Subagent | `OUTPUTS/fiche_enregistrement_subagent_arcanis.md` | Livrable (Phase 3) |
| Profil Avatar physique | `~/.antigravity/profiles/tesla-arcanis.md` | Configuration (Redressement) |
| Livrable Audit Alexandria | `OUTPUTS/rapport_de_divergence_alexandria.md` | Livrable (Phase 4) |
| Prompt Master Arcanis | `.agents/arcanis.md` | Configuration (Phase 3) |
| Script Transcription | `tools/transcribe_local.py` | Script (Phase 2) |
| Chantier absorbé | `Gestion-de-Chantiers/PLAN-ARMEMENT-COGNITIF_v1.0_2026-06-29.md` | Référence (absorbé) |
| Skill document-analyst (v1) | `.agents/skills/document-analyst/SKILL.md` | Fondation existante |
| Dossier agents | `.agents/` | Cible d'implémentation |

---

## 10. Journal de Bord

| Date | Événement | Décision |
|---|---|---|
| 2026-06-30 | Mahonheim ouvre le chantier avec le brief `Tesla ARCANIS.txt` | Document lu et assimilé |
| 2026-06-30 | Questionnaire de cadrage (3 questions) | Option 2 (Subagent Dédié) retenue. Chantier remplace Chantier 002. |
| 2026-06-30 | Rédaction et indexation du Plan d'Intervention Ultime v3.0 | Version 3.0 révisée et confrontée à 6 audits (Nemotron, ChatGPT, etc.) |
| 2026-06-30 | Diagnostic Premortem de la V3.0 | Rapport `premortem_tesla_arcanis.md` créé pour immuniser le plan |
| 2026-06-30 | Validation et exécution de la Phase 1 | Diagnostic validé : `pdftotext`, `pandoc`, `ffmpeg` opérationnels. |
| 2026-06-30 | Validation et exécution de la Phase 2 | compilation `whisper.cpp` réussie, modèle `base` téléchargé, script wrapper `transcribe_local.py` validé Pyright. |
| 2026-06-30 | Validation et exécution de la Phase 3 | Prompt Master enregistré dans `.agents/arcanis.md`, sous-agent déclaré dans `agy` via define_subagent. |
| 2026-06-30 | **Acte de Redressement de Lord Mahonheim** | Modèle AVATAR formalisé. Profil physique créé sous `~/.antigravity/profiles/tesla-arcanis.md`. Interdiction absolue de fallback silencieux. |
| 2026-06-30 | Validation et exécution de la Phase 4 | Activation stricte de l'Avatar via le moteur `self`. Audit RAG Alexandria complété et certifié dans `OUTPUTS/rapport_de_divergence_alexandria.md`. |

---

## 11. Risques & Blocages (Verrous V3.0 intégrés)

| Risque | Niveau | Mitigation (Contre-mesure) |
|---|---|---|
| **Saturation RAM (OOM)** sur MIDGARD | 🔴 Élevé | - whisper.cpp limité aux modèles `base` ou `tiny` (< 150 Mo RAM). <br>- Interdiction brute de fichiers > 500 Ko (RAG chunking). |
| **Boucles de relecture infinies** | 🟡 Moyen | - Auto-critique (Comité de lecture) limitée à **2 passes max**. <br>- Arrêt anticipé avec questions ouvertes si non résolu. |
| **Obsolescence de Webwright** | 🟡 Moyen | - Fallback auto vers `read_url_content` (natif) en cas de blocage de Playwright. |
| **Fragmentation de l'écosystème** | 🟡 Moyen | - Arcanis défini comme un **profil spécialisé de Tesla** (dossier `.agents/`). |
| **Validation intempestive (sudo)** | 🟡 Moyen | - Mode request-review asymétrique : lecture autorisée, écriture/modification bloquée. |

---

## 12. Critères de Clôture (Definition of Done)

- [ ] L'arsenal technique MIDGARD (poppler-utils, pandoc, whisper.cpp) est opérationnel et validé par un script.
- [ ] Le profil Arcanis est enregistré avec succès dans `.agents/arcanis.md`.
- [ ] Le pipeline cognitif adaptatif en 5 étapes est entièrement documenté et codé dans son prompt.
- [ ] Arcanis est capable d'ingérer et d'analyser de manière stable 6 formats sources (MD, PDF, EPUB, HTML, Audio, Vidéo).
- [ ] Un test grandeur réelle a été conduit, validé par Lord Mahonheim et contresigné avec le sceau immuable.
- [ ] Le Chantier 002 (Plan d'Armement Cognitif) est officiellement archivé comme absorbé.
- [ ] Le rapport Premortem est validé et classé.

---

## 13. Signature & Horodatage de Clôture
*(Section à compléter lors de l'archivage)*

- **Date de clôture :** —
- **Résultat final :** —
- **Signé :** Tesla sur Antigravity CLI
- **Main rendue à :** Lord Mahonheim

---
*Chantier géré par Tesla sous la doctrine du Vigilum Codex.*
