---
type: reference
tags: [architecture/second-brain, statut/a-valider, methode/planification]
source: "[[Alexandria::tesla-video-director-plan]]"
date: 2026-07-03
version: 1.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# Plan d'Intervention : Déploiement de la Skill d'Élite "tesla-video-director" (Shadow-Targeting)

## 1. Objectifs & Profil du Sous-Agent
Le présent plan d'intervention détaille les étapes techniques de déploiement de la skill d'élite **`tesla-video-director`**, activée sous le protocole de **Shadow-Targeting** (injection dynamique au sein de l'agent autorisé `self`).

### Missions de `tesla-video-director` :
*   **Créer & Éditer** : Conception générative de clips courts (Text-to-Video, Image-to-Video, keyframe interpolation) et modification stylistique (inpainting/style transfer) via l'API Google Gemini Omni Flash.
*   **Segmenter & Assembler** : Montage non-linéaire déterministe (MoviePy), découpage structurel automatique par détection de coupures de scènes (PySceneDetect) et téléchargement de flux de test (yt-dlp).
*   **Analyser & Transcrire** : Raisonnement sémantique profond sur longs formats et films (Gemini 1.5 Pro via l'API Files) et transcription de parole optimisée (API Groq Whisper).

---

## 2. Architecture Technique & Dépendances
Le sous-agent s'appuiera sur un écosystème hybride local/cloud afin de respecter la règle stricte de **Zero IA Locale** sur la machine MIDGARD :

### A. Dépendances Locales à installer dans le `.venv/` de Tesla :
*   `google-genai >= 2.10.0` (Client Interactions et Files API).
*   `moviepy` (Montage non-linéaire).
*   `scenedetect[opencv]` (Détection de coupures de scènes).
*   `yt-dlp` (Ingestion et cache de streams).

### B. Dépendances Système requises sur MIDGARD :
*   `/usr/bin/ffmpeg` & `/usr/bin/ffprobe` (déjà installés et opérationnels).

### C. Dépendances Cloud (Inférence & IA) :
*   API Gemini (Interactions API / Files API).
*   API Groq (Transcription ultra-rapide via Whisper-1).

---

## 3. Structure Physique de la Skill
La skill sera déployée sous le répertoire : `.agents/skills/tesla-video-director/`

```text
.agents/skills/tesla-video-director/
├── SKILL.md                 # Instructions système, invite d'identité et verrous
├── scripts/
│   ├── upload_file.py       # Upload asynchrone vers l'API Files
│   ├── video/
│   │   ├── prep_video.py    # Découpage, normalisation (720p/24fps) et suppression audio
│   │   ├── inspect_video.py # Extraction JSON de métadonnées vidéo (ffprobe)
│   │   └── generate_video.py# Script de génération Omni Flash (Interactions)
│   └── transcript/
│       └── transcribe.py    # Pont de transcription cloud (Groq/Whisper)
├── examples/
│   ├── jobs_template.json   # Template de configuration de batchs d'édition
│   └── prompt_guidelines.md # Règles d'écriture de prompts vidéo (tags <FIRST_FRAME>, etc.)
```

---

## 4. Directives de Sécurité & Conformité (Vigilum Codex)
1.  **Zéro Modèle IA Local** : Interdiction absolue d'exécuter localement des poids de modèles de vision ou de parole (ex: YOLO local, Whisper local, Stable Video Diffusion local). Les tâches d'inférence complexes doivent être systématiquement déléguées aux APIs distantes (Gemini, Groq).
2.  **Scrubbing de Secrets** : Tous les prompts ou fichiers de configuration de batch envoyés aux APIs cloud doivent être purgés de toute clé privée, token ou mot de passe.
3.  **Contrôle de Flux** : Tout fichier vidéo de plus de 20 Mo destiné à l'analyse sémantique par l'IA doit faire l'objet d'une recommandation automatique de compression (via `ffmpeg` en 480p/720p) afin de minimiser le transfert de bande passante.

---

## 5. Audit de Résilience & Contre-Mesures (Premortem)
*   *Défaillance 1 : Blocage géographique de l'édition vidéo-à-vidéo de Gemini Omni Flash dans l'EEE.*
    *   **Contre-mesure** : Le script `generate_video.py` doit lever une alerte explicite et guider le sous-agent vers l'approche de secours **First-Frame to Video** combinée à des images clés de référence stylistiques.
*   *Défaillance 2 : Dépassement de la fenêtre de contexte de 2M de tokens sur un film de plus de 2 heures.*
    *   **Contre-mesure** : Implémenter une routine dans `prep_video.py` scindant automatiquement la vidéo en segments de 45 minutes et réalisant des appels d'analyse séquentiels avant consolidation.
*   *Défaillance 3 : Conflits de dépendances Python dans le `.venv`.*
    *   **Contre-mesure** : Gérer l'isolation des bibliothèques via un environnement virtuel propre au projet et tester les imports critiques (`google.genai`, `moviepy`) lors de la phase de recette.

---

## 6. Jalons de Déploiement & Recette (Recette v1.0)
*   **Jalon 0 : Préparation de l'environnement (MIDGARD)** :
    *   Installation des paquets python requis dans le `.venv/`.
    *   Validation de la présence des chemins système de `ffmpeg`/`ffprobe`.
*   **Jalon 1 : Scaffolding physique de la Skill** :
    *   Création des fichiers et structures de répertoires sous `.agents/skills/tesla-video-director/`.
    *   Configuration de la clé API Groq au sein des variables d'environnement persistantes de l'agent.
*   **Jalon 2 : Intégration & Test Smoke-Test** :
    *   Exécution d'une transcription de test d'un flux audio léger via Groq.
    *   Exécution d'une génération de test Text-to-Video de 3 secondes via Omni Flash.
*   **Jalon 3 : Indexation et Enregistrement SGC** :
    *   Mise à jour d'Alexandria, indexation FTS5 et mise à jour de `PROJECT_STATE.md`.

---
SHA256: a844ccb34c88b0460f140c374061375b3529ea49c7a571f21f158902ef076f54
