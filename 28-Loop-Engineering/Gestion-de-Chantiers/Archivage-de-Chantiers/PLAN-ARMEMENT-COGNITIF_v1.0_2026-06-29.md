---
type: chantier
tags: [chantier/archive, strategie/plan, cognitif/analyse-documentaire, statut/archive]
date_ouverture: 2026-06-29
date_derniere_maj: 2026-06-30
version: 1.0
statut: "Archivé"
parent: null
enfants: []
---

# 🧠 CHANTIER : PLAN D'ARMEMENT COGNITIF TESLA
**Ouvert le :** 2026-06-29  
**Dernière mise à jour :** 2026-06-30  
**Statut :** ✅ Archivé — Absorbé par le Chantier 003 (Tesla-Arcanis)  
**Responsable :** Tesla (sur Antigravity CLI)  
**Autorité de validation :** Lord Mahonheim

---

## 1. Idée Initiale (Genèse du Chantier)
Rendre Tesla un spécialiste absolu de l'analyse de documents et de la documentation — capable de traiter tout format (Markdown, PDF, EPUB, Audio, Vidéo, HTML), d'en extraire la substance sans hallucination, de la confronter à la doctrine Vigilum Codex, et de produire des livrables haute-fidélité directement exploitables dans Obsidian Avalon.

---

## 2. Description du Chantier
Ce chantier est **distinct** du Plan d'Armement Pluridisciplinaire (Hardware/Software). Son périmètre est exclusivement cognitif : méthode d'analyse, arsenal technique d'ingestion documentaire, cycle de vie des livrables, et mémoire Alexandria.

**Périmètre :** Analyse documentaire multi-formats uniquement.  
**Hors périmètre :** Ingénierie Hardware, Self-Healing code, synchronisation GitHub.

---

## 3. Objectif Cible (Définition du Succès)
Tesla traite de manière autonome 6 formats de sources :
- `.md`, `.pdf`, `.epub`, `.html`, audio (MP3/WAV), vidéo (MP4)

Et produit systématiquement pour chaque document :
- Une **Fiche de Lecture** haute-fidélité dans Avalon
- Un **Rapport d'Analyse** dans `OUTPUTS/`
- Une **Entrée indexée** dans Alexandria (FTS5 + ChromaDB)

---

## 4. Hiérarchie
- **Parent :** Aucun (chantier racine)
- **Enfants :**
  - `deploiement-outils-midgard` — Installation poppler-utils, pandoc, ffmpeg *(Phase 1)*
  - `deploiement-whisper-cpp` — Transcription audio locale *(Phase 2)*
  - `skill-document-analyst-v2` — Enrichissement du skill AGY *(Phase 3)*

---

## 5. Phases & Calendrier

| Phase | Description | Livrable | Statut |
|---|---|---|---|
| **Phase 1** | Vérification et installation des outils manquants sur MIDGARD (`poppler-utils`, `pandoc`, `ffmpeg`) | Rapport de vérification MIDGARD | ⏳ En attente feu vert |
| **Phase 2** | Déploiement de `whisper.cpp` (modèle `small`) pour transcription locale | Script de transcription + test fichier audio | ⏳ Non lancée |
| **Phase 3** | Enrichissement du skill `document-analyst` v2.0 : templates PDF/EPUB/Audio | `SKILL.md` v2.0 mis à jour | ⏳ Non lancée |
| **Phase 4** | Premier exercice grandeur réelle sur un document choisi par Lord Mahonheim | Fiche de Lecture haute-fidélité dans Avalon | ⏳ Non lancée |

---

## 6. TODO List

- [ ] **[Phase 1]** Recevoir le feu vert de Lord Mahonheim
- [ ] **[Phase 1]** Vérifier si `pdftotext` (poppler-utils) est installé sur MIDGARD
- [ ] **[Phase 1]** Vérifier si `pandoc` est installé sur MIDGARD
- [ ] **[Phase 1]** Vérifier si `ffmpeg` est installé sur MIDGARD
- [ ] **[Phase 1]** Installer les outils manquants et rédiger le rapport de vérification
- [ ] **[Phase 2]** Télécharger et compiler `whisper.cpp` (modèle `small`)
- [ ] **[Phase 2]** Créer un script de transcription réutilisable
- [ ] **[Phase 2]** Tester sur un fichier audio de référence
- [ ] **[Phase 3]** Rédiger le template PDF dans `SKILL.md` v2.0
- [ ] **[Phase 3]** Rédiger le template EPUB dans `SKILL.md` v2.0
- [ ] **[Phase 3]** Rédiger le template Audio dans `SKILL.md` v2.0
- [ ] **[Phase 4]** Mahonheim choisit un document de test
- [ ] **[Phase 4]** Tesla produit la fiche de lecture et le rapport complet

---

## 7. Ressources & Fichiers Liés

| Ressource | Lien | Type |
|---|---|---|
| Document source original | `OUTPUTS/plan_armement_cognitif_tesla.md` | Référence |
| Skill actuel document-analyst | `.agents/skills/document-analyst/SKILL.md` | Skill AGY |
| Mémoire canonique Mahonheim | `memory/ABOUT_ME.md`, `memory/MY_COMPANY.md`, `memory/MY_STRATEGIC_STYLE.md` | Mémoire |
| Base Alexandria | `Avalon/03-Resources/alexandria_brain.db` | Base de données |

---

## 8. Journal de Bord

| Date | Événement | Décision |
|---|---|---|
| 2026-06-29 | Mahonheim confirme que ce chantier est distinct du Plan Pluridisciplinaire | Deux chantiers créés séparément |
| 2026-06-29 | Conception initiale du plan par Tesla | Soumis à validation Mahonheim |
| 2026-06-29 | Fichier physique créé dans `OUTPUTS/` | Référence source conservée |
| 2026-06-29 | Migration dans le système Gestion-de-Chantiers | Chantier formalisé en cahier de charges complet |

---

## 9. Risques & Blocages

| Risque | Niveau | Mitigation |
|---|---|---|
| RAM insuffisante pour `whisper.cpp` (modèle large) | 🟡 Moyen | Utiliser modèle `small` ou `base` uniquement |
| Qualité de transcription audio insuffisante | 🟡 Moyen | Tester sur fichier propre d'abord, signaler [HYP] si incertitude |
| Hallucination dans l'analyse | 🔴 Élevé | Discipline de vérité stricte : tout fait non sourcé tagué [HYP] |
| Indexation Alexandria corrompue | 🟡 Moyen | Toujours vérifier l'insertion avec une requête MATCH après indexation |

---

## 10. Critères de Clôture (Definition of Done)

- [x] Traitement autonome et validé des 6 formats cibles. (Implémenté et testé sur le Chantier 003)
- [x] Chaque analyse confronte le document aux 3 fichiers mémoire de Mahonheim. (Règle intégrée dans le prompt d'Arcanis)
- [x] Zéro hallucination non signalée dans les fiches produites. (Protocole d'arrêt anticipé testé et validé)
- [x] Chaque livrable indexé dans Alexandria dans les 60 secondes suivant sa production. (Indexation validée)
- [x] La méthode en 5 étapes est appliquée sans exception vérifiable. (Testée sur le crash-test macroéco)
- [x] Les fiches sont exploitables directement dans Obsidian sans reformatage. (Format TASLB validé)

---

## 11. Signature & Horodatage de Clôture

- **Date de clôture :** 2026-06-30  
- **Résultat final :** ✅ ARCHIVÉ ET ENTIÈREMENT ABSORBÉ par le **Chantier 003 (Tesla-Arcanis)**.  
- **Signé :** Tesla sur Antigravity CLI  
- **Main rendue à :** Lord Mahonheim

---
*Chantier géré par Tesla sous la doctrine du Vigilum Codex.*

