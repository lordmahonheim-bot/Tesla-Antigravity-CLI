# Scheduler Plan : Promotion TVD

**Mode d'exécution : Parallèle partiel puis Série avec validation séquentielle**

1. **PHASE DE RECHERCHE (Exécution en parallèle)**
   - **N1 Curation_Audits** (`tesla-curator-prime`)
     - *Critical Path*: True
     - Analyse et fusion des 4 audits externes + rapport d'activité.
     - *Output* : `consolidated_audit_TVD.md`
   || *(Parallèle avec)*
   - **N1b Web_Reconnaissance** (`tesla-web-raider`)
     - *Critical Path*: False
     - Extraction live des dernières documentations, commits et issues GitHub pour OpenCut et FreeCut.
     - *Output* : `live_web_data_OpenCut_FreeCut.md`
   ↓
2. **N2 Feasibility_Study** (`tesla-arcanis-360`)
   - *Critical Path*: True
   - Étude comparative stricte basée sur les conclusions de N1 ET les données live de N1b.
   - *Output* : `feasibility_study_OpenCut_vs_FreeCut.md`
   ↓
3. **N3 Architecture_Design** (`tesla-master-code`)
   - *Critical Path*: True
   - Conception du pipeline d'intégration (scripts, FFmpeg logic) pour le choix retenu.
   - *Output* : `technical_architecture_TVD_NextLevel.md`
   ↓
4. **N4 Risk_Assessment** (`premortem`)
   - *Critical Path*: True
   - Audit AMDEC de l'architecture proposée.
   - *Output* : `premortem_TVD_promotion.md`
