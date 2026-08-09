## Goal Description
Rectifier l'architecture d'intégration hybride de FreeCut (TVD NextLevel) suite à l'audit brutal de Tesla-PREMORTEM (Nœud N4). L'objectif est d'éliminer les risques critiques de désynchronisation A/V (délire temporel Gemini) et de corruption de structure GOP (FFmpeg keyframes) avant de lancer l'écriture du code par Tesla-Master-Code.

## User Review Required
> [!IMPORTANT]
> Le ré-encodage systématique (H.264/AAC) imposé par l'audit Premortem va nécessairement augmenter le temps de rendu CPU par rapport à un simple `stream copy`. Validez-vous ce compromis "Temps d'exécution vs Qualité/Stabilité" ?
> [!WARNING]
> Le système de *chunking* (découpage de l'audio en blocs de 10 minutes maximum) nécessitera d'appeler l'API Gemini plusieurs fois pour les vidéos longues. Validez-vous cet impact potentiel sur la Token-Economy et les quotas ?

## Open Questions
- Faut-il configurer la taille des chunks audio (actuellement proposée à 10 minutes) de manière dynamique en fonction du quota API restant ?

## Proposed Changes
Les modifications d'architecture cibleront les composants définis lors de la phase N3.

---

### Extracteur Audio (Chunking Node)
L'extracteur audio (3.1) doit être modifié pour fragmenter l'audio avant l'envoi afin de limiter les hallucinations de timecodes sur de longues durées.
#### [MODIFY] Audio Extraction Logic
- Introduction d'une fonction de chunking FFmpeg : `ffmpeg -i input.mp4 -f segment -segment_time 600 -c copy audio_chunk_%03d.m4a`.
- Extraction prioritaire en basse qualité (16kHz, mono) pour alléger le payload API.

---

### Moteur de Transcription Sémantique (QA Post-JSON)
Le générateur JSON (3.2) doit intégrer une passe de Quality Assurance (QA) stricte pour valider la réalité physique des timecodes renvoyés par Gemini.
#### [MODIFY] Transcription Node
- Ajout d'une logique de validation temporelle : La vérification que `end_time - start_time` correspond physiquement à la durée de l'audio envoyé.
- Rejet immédiat, log d'alerte et déclenchement d'un *Retry* ciblé en cas de dérive temporelle ou de durations négatives.

---

### Rendu Final FFmpeg (Re-Encoding & ffconcat)
L'étape de rendu final (3.4) abandonne le `stream copy` instable pour les coupes libres.
#### [MODIFY] Render Node
- Basculement imposé sur le ré-encodage logiciel : `-c:v libx264 -c:a aac`.
- Implémentation systématique du format texte `ffconcat` (`-f concat -i cuts.txt`) au lieu de la concaténation par `filter_complex` pour éviter l'engorgement du shell.
- *Optionnel* : Ajout d'un crossfade imperceptible (20ms) entre les cuts générés pour lisser les raccords potentiellement asynchrones.

## Verification Plan

### Automated Tests
- Exécuter un PoC `freecut_gemini_transcriber.py` avec une vidéo de test de 15 min.
- Vérifier que l'extracteur produit bien 2 chunks.
- Vérifier que la fonction QA post-JSON lève une erreur si on injecte volontairement un timecode aberrant (ex: `end_time` > durée du chunk).

### Manual Verification
- Visualiser le résultat final d'un export vidéo pour valider l'absence totale de *freeze* d'image aux points de coupe (vérification de la résolution du risque GOP).
- Confirmer la synchronisation labiale parfaite sur les différents segments montés.
