---
title: "Manifeste du Sanctuaire d'Acquisition Cognitive"
status: "Canonical"
version: "1.0.0"
---

![Status](https://img.shields.io/badge/Status-CANONICAL-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red)

# 🏛️ Sanctuaire d'Acquisition Cognitive (/LEARN)

Bienvenue dans le centre de mémoire à long terme de l'écosystème Tesla. Ce répertoire n'est pas un simple dossier de stockage documentaire : c'est un **mécanisme d'ingénierie mémorielle** conçu pour empêcher l'évaporation des apprentissages cognitifs et centraliser la gouvernance.

---

## 1. Le Diagnostic Technique : Le Piège de la Mémoire Volatile

Par défaut, l'écosystème Antigravity génère ses artéfacts dans un répertoire encapsulé et isolé, propre à chaque session active (`~/.gemini/antigravity-cli/brain/<uuid>/`). 

Cette mécanique native crée une mémoire **compartimentée et volatile**. À l'ouverture d'une nouvelle session, l'ancien "cerveau" devient inactif et ses apprentissages sont cognitivement inaccessibles pour la nouvelle instance de l'Agent. Dans ce paradigme : *hors de vue = hors de conscience*.

Pour sanctuariser la connaissance et la rendre globale, l'apprentissage doit obligatoirement **s'échapper de ce silo éphémère** pour s'ancrer de manière permanente dans le disque dur global : la Source de Vérité absolue.

---

## 2. La Loi Dogmatique [VC-MEM-06]

Afin d'automatiser cet échappement, l'utilisation de ce répertoire est régie de manière stricte par le Vigilum Codex :

> **[VC-MEM-06] Sanctuaire d'Acquisition Cognitive (/LEARN)**
> Le répertoire `/home/lord-mahonheim/bifrost/tesla/memory/LEARN/` est officiellement érigé en sous-domaine canonique de la source de vérité.
> 
> 1. **Bypass du Silo Mémoriel (Routage Absolu) :** Lors de l'exécution d'une commande `/Learn`, l'Agent a l'interdiction de se contenter de générer un artéfact d'interface standard (qui finit piégé dans le dossier `brain/`). Il DOIT obligatoirement utiliser un appel système `write_to_file` pointant vers le chemin absolu du sanctuaire : `/home/lord-mahonheim/bifrost/tesla/memory/LEARN/`.
> 2. **Ségrégation Historique (Anti-Semantic Bloat) :** Le sanctuaire doit abriter une architecture d'archivage (`ARCHIVES/`). Le répertoire racine `/LEARN/` est réservé aux apprentissages "frais" (en cours d'assimilation). Dès qu'une leçon est intégrée à la *Cartographie Intégrale*, le fichier source brut doit être basculé dans les archives pour maintenir la clarté cognitive de l'écosystème.

---

## 3. Architecture et Routage (Pour les Agents)

Pour respecter la loi d'Anti-Semantic Bloat, ce répertoire applique une ségrégation physique entre la Règle (l'Index), l'Apprentissage (le Flux) et l'Archive (l'Historique fossilisé).

```text
/memory/LEARN/
├── README.md                                  # Le présent manifeste architectural
├── CARTOGRAPHIE_APPRENTISSAGES_INTEGRALE.md   # L'Index Gouverné (Les règles actives VC-XXX)
├── [fichier_apprentissage_frais.md]           # Nouvel output /Learn (en attente d'assimilation)
└── ARCHIVES/                                  # Sous-répertoire de relégation (Fossiles)
    └── ARCHIVES_APPRENTISSAGES.md             # Compilation des anciennes leçons historiques
```

---

## 4. Preuve de Conformité (Evidence Chain)

L'audit de ce comportement est déterministe et s'appuie sur la vérification des appels système de l'Agent.

> **[EVIDENCE_CHAIN]**:
> `EVIDENCE_TYPE: TRACE`
> Traçabilité stricte dans les logs de l'appel système `write_to_file` ciblant le chemin absolu `/memory/LEARN/`, validant le contournement réussi du dossier éphémère `brain/`.
