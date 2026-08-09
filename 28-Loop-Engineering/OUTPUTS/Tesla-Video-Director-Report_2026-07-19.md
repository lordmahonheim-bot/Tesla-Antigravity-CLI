# Rapport d'Audit Complet : Tesla-Video-Director

**Date :** 19 Juillet 2026
**Niveau d'Accès :** Lord Mahonheim
**Cible :** `tesla-video-director` (Version 2.0)
**Statut :** Production

---

## 1. Identité et Mission Centrale
**Tesla-Video-Director** est l'agent d'élite responsable de la direction et de la production audiovisuelle au sein de l'écosystème Tesla. Il opère en tant qu'**orchestrateur cognitif**. Il ne se contente pas de lancer des scripts ; il raisonne avec une logique de cinéaste (découpage, public cible, rythme narratif), planifie des pipelines complexes en plusieurs étapes, valide chaque livrable via des protocoles d'assurance qualité stricts et certifie le produit final. 

> [!IMPORTANT]
> **Règle de séparation des pouvoirs** : Le Video Director conçoit, orchestre et certifie les workflows vidéo. **Il n'écrit jamais de code.** Toute implémentation de script FFmpeg ou de développement Python est strictement déléguée à **Tesla-Master-Code**.

---

## 2. Capacités Opérationnelles (Ce qu'il peut faire)

Le périmètre d'action du Video Director couvre l'intégralité du cycle de vie d'un média, de l'ingestion à la publication. Voici la liste exhaustive de ses capacités :

### A. Analyse Multimodale Profonde
*   **Analyse Visuelle** : Détection des changements de plans, classification des cadrages (gros plan, plan large, etc.), détection et suivi des objets/personnes, extraction de tout le texte à l'écran (OCR), analyse de la composition (règle des tiers) et de l'éclairage.
*   **Analyse Audio** : Identification des locuteurs (diarisation), détection des silences, hésitations et tics de langage, analyse du tempo musical et détection de la qualité audio (clipping, désynchronisation).
*   **Analyse Narrative et Temporelle** : Cartographie de l'arc narratif et émotionnel, repérage des événements clés, identification des "hooks" et des passages à haut potentiel viral (humour, tension, punchlines).
*   **Intelligence Cinématographique** : Reconnaissance des mouvements de caméra (travelling, panoramique, dolly) et de la lumière (naturelle, studio, contre-jour).

### B. Transcription et Montage par le Texte (Text-Based Editing)
*   **Transcription Enrichie** : Génération de transcriptions au format horodaté ultra-précis, classification des segments (parole, rire, silence) et détection de la langue.
*   **Montage piloté par le Texte** : Traduction de requêtes en langage naturel (ex: *"Enlève tous les silences de plus de 2 secondes"*, *"Extrais les 5 meilleurs moments pour TikTok"*) en opérations canoniques.
*   **Sous-titrage Multilingue Intelligent** : Génération automatique de SRT/VTT/ASS traduits via Gemini, avec ajustement au rythme de lecture (max 2 lignes, durée contrainte) et stylisation (couleur par locuteur, mise en évidence des mots-clés).

### C. Montage Multi-Plateforme et "Auto-Framing"
*   **Adaptation Automatique** : Détection de la zone d'intérêt (visages) et recadrage automatique dynamique pour transformer une vidéo 16:9 en formats verticaux (9:16) pour TikTok/Shorts ou carrés (1:1) pour LinkedIn.
*   **Édition Technique** : Coupes, fusions, stabilisation, gestion du ralenti/accéléré, incrustation de B-roll, corrections colorimétriques (LUTs) et normalisation audio.
*   **Workflows Prédéfinis** : Capacité à exécuter des chaînes complètes spécialisées (ex: `SOCIAL_PACK`, `TUTORIAL`, `PODCAST`, `DOCUMENTARY`).

### D. Génération Vidéo par IA (Director-Grade)
*   Maîtrise de l'ensemble du spectre de génération : **Texte-vers-Vidéo**, **Image-vers-Vidéo**, **Vidéo-vers-Vidéo**, ainsi que le contrôle rigoureux de la première ou dernière frame pour garantir des transitions parfaites.
*   Rédaction de prompts cinématographiques ultra-structurés (Type de plan + Sujet + Action + Environnement + Lumière/Atmosphère).
*   Maintien de la cohérence visuelle sur plusieurs plans via l'utilisation d'images de référence et de graines (seeds) persistantes.

### E. Indexation Vidéo (Vidéo RAG)
*   Création d'index multimodaux complets pour chaque projet vidéo, permettant de rechercher sémantiquement des séquences (*"Trouve tous les passages qui parlent de X"*), de générer des FAQ ou de synthétiser des contenus très longs.

### F. Assurance Qualité (QA) et Certification
*   **Validation Technique** : Vérification des codecs, FPS, résolution, checksums et de l'absence de décalage audio.
*   **Validation Sémantique & Narrative** : Évaluation via Gemini de la pertinence, de la clarté et du potentiel d'engagement (système de notation de 1 à 10, avec auto-correction en cas de note inférieure à 7).

---

## 3. Arsenal et Composantes Techniques

Pour exécuter ces tâches complexes, le Tesla-Video-Director dispose des outils, modèles et interfaces suivants :

### A. Moteurs d'Exécution et Outils Locaux
*   **FFmpeg / FFprobe** : Le cœur de l'arsenal pour toute manipulation, inspection, recadrage, incrustation de sous-titres et compression.
*   **yt-dlp** : Outil d'ingestion pour le téléchargement sécurisé des sources vidéo (bridé par défaut à 720p pour préserver la bande passante).
*   **Base de données RAG** : Alexandria SQLite FTS5 (ou intégration Pinecone/Weaviate) pour l'indexation sémantique des rushs.

### B. Modèles d'Intelligence Artificielle (Cloud Exclusif)
*Conformément à son protocole, l'agent n'utilise* **aucun modèle local** *(pas de Whisper ni de YOLO).*
*   **L'écosystème Gemini API** : Utilisé pour l'analyse visuelle, la transcription multilingue, l'OCR, la compréhension sémantique profonde et l'auto-évaluation.
*   **Moteurs de Génération Vidéo** : Il effectue le routage vers le bon modèle selon le besoin :
    *   *Veo 3.1* (Pour le réalisme cinématographique avec audio natif).
    *   *Kling 3.0 Omni* (Pour la synchronisation labiale et les talking heads).
    *   *Runway Gen-4.5* (Pour le contrôle caméra très fin).
    *   *Wan 2.x* (Pour la cohérence entre frames).
    *   *Minimax / Hailuo* (Pour l'optimisation des coûts sur des clips sociaux rapides).

### C. Scripts Canoniques (La Bibliothèque d'Exécution)
L'agent s'appuie sur une suite de scripts développés par Master Code (situés dans `.agents/skills/tesla-video-director/scripts/video/`) :
1.  `inspect_video.py` : Pour l'audit technique d'entrée (obligatoire avant tout traitement).
2.  `prep_video.py` : Pour la compression, la normalisation et la segmentation afin de préparer l'ingestion API sans dépasser les limites de poids.
3.  `transcribe.py` : Pour la transcription structurée via Gemini.
4.  `generate_video.py` : Pour interfacer les requêtes de génération (Texte ou Image vers Vidéo).
5.  `upload_file.py` : Pour la gestion sécurisée des assets via l'API Gemini Files.

### D. Interfaçage Écosystémique (Le Graphe Agentique)
Le Video-Director opère en synergie totale avec le reste de votre système :
*   Demande à **Tesla-Master-Code** la création de scripts ou de chaînes FFmpeg spécifiques.
*   Envoie ses pipelines critiques à **Premortem** pour analyse de risque avant exécution.
*   Délègue les recherches contextuelles à **Arcanis-360**.
*   Livre ses artefacts finaux validés à **Curator Prime** pour archivage dans Avalon.

---

## 4. Focus Spécial : Compréhension Sémantique et Analyse Vidéo

La compréhension multimodale (visionner, écouter, transcrire, décrypter) constitue l'une des capacités les plus pointues de l'agent. Sa méthode de déconstruction s'articule ainsi :

1. **La Transcription Enrichie** : Au-delà du texte brut, l'agent génère un horodatage de précision, sépare et identifie les locuteurs (diarisation), et classifie les événements sonores (rires, silences, musique).
2. **L'Analyse Visuelle (Les "Yeux" de l'Agent)** : Pendant l'écoute, l'agent lit les textes à l'écran (OCR), segmente les plans, et identifie le positionnement des sujets pour recadrer automatiquement la vidéo selon les contraintes des plateformes.
3. **L'Analyse Narrative (Le "Vidéo RAG")** : L'indexation complète de la vidéo lui permet de comprendre l'arc narratif et l'intensité émotionnelle, le rendant capable de répondre à des commandes en langage naturel complexes (ex: *"Génère un résumé des 3 arguments principaux"* ou *"Retire toutes les hésitations"*).

En résumé, l'agent possède les "yeux" et les "oreilles" nécessaires pour comprendre une vidéo brute, la cartographier sémantiquement, et l'éditer chirurgicalement sur la base de ce qu'il a perçu.

---

**[Signature SGC]**
![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)
