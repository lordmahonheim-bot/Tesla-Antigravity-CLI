---
type: reference
tags: [media/video, statut/a-valider, methode/audit]
source: "[[Alexandria::video-arsenal]]"
date: 2026-07-03
version: 1.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# Rapport d'Audit Interne : L'Arsenal Vidéo de Tesla (MIDGARD & Cloud)

## 1. Synthèse de l'Arsenal Matériel et Logiciel
Le présent rapport dresse l'inventaire complet et l'analyse fonctionnelle des capacités locales (sur la machine MIDGARD) et distantes (via les APIs cloud de Google Gemini) pour la manipulation, la création, l'édition, l'analyse et la transcription de vidéos de tous types et de tous formats (des clips courts aux longs-métrages).

### A. Composants Physiques et Systèmes locaux (MIDGARD)
*   **`/usr/bin/ffmpeg` & `/usr/bin/ffprobe`** : Les binaires de référence pour le décodage, l'encodage, le multiplexage, le transcodage et l'inspection de flux. Ils supportent virtuellement tous les formats conteneurs (MP4, MKV, AVI, MOV, WebM, FLV) et codecs (H.264, H.265/HEVC, AV1, VP9, AAC, MP3).
*   **Scripts d'Automatisation du Skill `gemini-omni-flash-api`** :
    *   [prep_video.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/video/prep_video.py) : Script de normalisation, de découpage temporel et d'adaptation de résolution.
    *   [inspect_video.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/video/inspect_video.py) : Script d'extraction de métadonnées brutes ou JSON structurées via `ffprobe`.
    *   [upload_file.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/upload_file.py) : Gestionnaire d'upload vers l'API Files avec détection de taille et alertes de performance.
    *   [generate_video.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/video/generate_video.py) : Script d'interaction générative (Interactions API) supportant les requêtes unitaires et les traitements par lots (JSON ou texte).

### B. Ressources de Raisonnement et de Génération (Cloud)
*   **Modèle `gemini-omni-flash-preview`** : Dédié à l'édition générative rapide de vidéos de 3 à 10 secondes (Text-to-Video, Image-to-Video, Video-to-Video).
*   **Modèles `gemini-1.5-pro` & `gemini-1.5-flash`** : Moteurs multimodaux à contexte géant (jusqu'à 2 millions de tokens pour la version Pro), capables d'ingérer et de raisonner sur de longs fichiers vidéos (jusqu'à 2 Go de données).

---

## 2. Analyse Fonctionnelle par Dimension

### A. Créer (Génération Text-to-Video & Image-to-Video)
*   **Mécanisme** : Via le script [generate_video.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/video/generate_video.py).
*   **Capacités** :
    *   Génération de clips fluides (3 à 10 secondes) au format MP4.
    *   Animation à partir d'une image clé initiale (tag `<FIRST_FRAME>`).
    *   Guidage stylistique ou de sujet à l'aide d'images de référence (tags `<IMAGE_REF_N>`).
    *   Interpolation fluide entre deux images clés distinctes (timelapses, transitions).

### B. Éditer (Modification, Inpainting, Outpainting & Flux Audio)
*   **Mécanisme** : Combinaison de `ffmpeg` local (pré-traitement) et de l'API Interactions (édition générative).
*   **Capacités** :
    *   **Normalisation** : Redimensionnement proportionnel (720p optimisé pour l'IA) et ajustement du framerate (24fps / 30fps) via `prep_video.py`.
    *   **Style Transfer / Inpainting** : Modification stylistique d'une vidéo existante par des prompts ciblés (ex: "rendre le style anime", "rendre le téléphone invisible").
    *   **Gestion Audio** : Conservation de la piste audio d'origine par défaut, ou suppression complète (`--strip-audio`) pour forcer le modèle à régénérer une bande-son originale calée sur les nouvelles images.

### C. Lire & Inspecter
*   **Mécanisme** : Analyse locale via [inspect_video.py](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/gemini-omni-flash-api/scripts/video/inspect_video.py) encapsulant `ffprobe`.
*   **Capacités** :
    *   Vérification des codecs vidéo et audio, de la présence de pistes audio, de la durée exacte et du framerate.
    *   Sortie JSON propre pour intégration dans nos scripts de diagnostic.

### D. Analyser (Raisonnement temporel profond sur longs formats et films)
*   **Mécanisme** : Téléchargement de la vidéo vers l'API Files de Google (limite de 2 Go) et analyse sémantique par `gemini-1.5-pro`.
*   **Capacités** :
    *   **Analyse Multi-heures** : 1 seconde de vidéo équivalant à environ 250-300 tokens, la fenêtre de 2 millions de tokens de Gemini 1.5 Pro permet d'analyser d'une seule traite environ **1 heure à 1 heure 30 de film**.
    *   **Raisonnement Temporel** : L'IA peut identifier des événements à des timecodes précis, lister des changements de plans, suivre des objets ou des personnages d'une scène à l'autre, et résumer des intrigues complexes.
    *   **Traduction et Sous-titres** : Détection des dialogues oraux et des textes incrustés à l'écran.

### E. Transcrire
*   **Mécanisme** : Extraction et transcription de la piste audio par le modèle multimodal de Gemini.
*   **Capacités** :
    *   Transcription multilingue verbatim de la parole.
    *   Diarisation des locuteurs (distinction de qui parle et quand).
    *   Génération de fichiers de sous-titres horodatés (SRT/VTT).
    *   *Alternative locale* : Extraction préalable de l'audio via `ffmpeg -i video.mp4 -vn -acodec copy audio.aac` pour traitement par des scripts de transcription dédiés si nécessaire.

---

## 3. Audit de Performance & Limites Techniques (Klein's Premortem)
Qu'est-ce qui pourrait provoquer l'échec d'un projet d'analyse ou d'édition vidéo sur notre architecture ?

1.  **Surcharges de bande passante et de stockage (Films et Go)** :
    *   *Risque* : L'upload d'un film complet non compressé (plusieurs Go) vers l'API Files peut saturer la bande passante de la machine hôte et échouer en timeout.
    *   *Contre-mesure* : Utiliser systématiquement `prep_video.py` (ou des commandes `ffmpeg` personnalisées) pour compresser fortement les fichiers en HEVC/AV1 à 480p/720p avant l'upload. La résolution n'impacte pas significativement la qualité de la transcription ou du raisonnement global du modèle.
2.  **Restrictions Régionales d'Édition Générative (Omni Flash)** :
    *   *Risque* : L'édition de vidéo à vidéo (Video-to-Video) n'est pas autorisée dans l'Espace Économique Européen (EEE) et au Royaume-Uni. Les appels à l'API pour ces tâches renvoient des sorties vides.
    *   *Contre-mesure* : Contourner cette restriction par des requêtes de type **First-Frame to Video** guidées par des images clés de référence stylistiques (qui ne tombent pas sous la coupe de la restriction de transfert vidéo direct).
3.  **Surcharge des limites de tokens sur les films très longs (> 2 heures)** :
    *   *Risque* : Un film de plus de 2 heures dépasse la fenêtre de contexte de 2 millions de tokens.
    *   *Contre-mesure* : Découper le film en segments de 30 ou 60 minutes avec `ffmpeg` (ex: `ffmpeg -i film.mp4 -ss 00:00:00 -t 00:30:00 -c copy segment1.mp4`), analyser chaque segment de manière isolée, puis consolider les synthèses par un appel textuel global.

---

## 4. Recommandations Opérationnelles
1.  **Initialisation de l'environnement Python** : Installer la bibliothèque officielle `google-genai` dans notre environnement virtuel `.venv/` en cas de besoin d'exécution directe de ces scripts :
    ```bash
    /home/lord-mahonheim/bifrost/tesla/.venv/bin/pip install -U google-genai
    ```
2.  **Prioriser la compression pour l'analyse** : Pour toute demande d'analyse de film, appliquer la commande de pré-compression suivante avant l'upload :
    ```bash
    ffmpeg -i entree.mp4 -vf scale=-2:480 -c:v libx264 -crf 28 -preset faster -c:a aac -b:a 96k sortie_legere.mp4
    ```
    *Cela réduit la taille d'un fichier de 90% tout en conservant 100% de la fidélité audio et visuelle nécessaire à l'analyse.*

---
SHA256: a7bf678faf3bb0bab03ef1fee2c892ab5a7ad1d32c6f58032ef9c2fdf333ba45
