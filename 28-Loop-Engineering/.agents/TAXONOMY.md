---
role: Taxonomic Governance
status: canonical
title: TAXONOMY
version: 1
---

# TAXONOMY.md

> **Mission**
> Ce fichier définit la doctrine taxonomique formalisée par Lord Mahonheim pour la structuration de l'écosystème Tesla. Il fige le vocabulaire et son implémentation physique.

## 1. Taxonomie Conceptuelle

La doctrine impose les définitions strictes suivantes :

- **Projet** = Stratégie (Vision, périmètre global, alignement long terme)
- **Chantier** = Opérationnel (Exécution ciblée, tâches actionnables, MVP)
- **Workflow** = Procédural (Règles, enchaînement d'actions, pipelines)
- **Composant** = Tangible (Code, scripts, modèles, agents, outils physiques)

## 2. Emplacements Physiques

L'implémentation de cette doctrine se traduit par deux répertoires distincts dont les rôles ne doivent jamais être confondus :

- **SGP (Gestionnaire-de-Projets)**
  - *Emplacement physique* : `/home/lord-mahonheim/bifrost/tesla/Gestionnaire-de-Projets/`
  - *Rôle* : Centralisation de la dimension stratégique. Héberge les documents de vision globale et d'alignement.

- **SGC (Gestion-de-Chantiers)**
  - *Emplacement physique* : `/home/lord-mahonheim/bifrost/tesla/Gestion-de-Chantiers/`
  - *Rôle* : Suivi opérationnel. Héberge les cahiers des charges des chantiers (fichiers `[NOM-DU-CHANTIER]_v1.0_AAAA-MM-JJ.md`), l'`INDEX.md` de suivi des tâches, et l'orchestration des composants tangibles et workflows procéduraux de chaque chantier.
