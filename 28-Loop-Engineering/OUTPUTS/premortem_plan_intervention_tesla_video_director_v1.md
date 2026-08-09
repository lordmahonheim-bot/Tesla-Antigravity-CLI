---
type: reference
tags: [securite/premortem, statut/a-valider]
source: "[[plan_intervention_tesla_video_director_v1]]"
date: 2026-07-03
version: 1.0
---

# RAPPORT D'AUDIT PREMORTEM : PLAN INTERVENTION TESLA-VIDEO-DIRECTOR
**Date de l'audit :** 2026-07-03  
**Analyste :** premortem-analyst (Sous-Agent Tesla)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)

---

## 1. Postulat de l'Échec Virtuel (T+3 Mois)

> [!WARNING]
> Nous sommes le **3 octobre 2026**. 
> Le plan **tesla-video-director** a été déployé il y a trois mois. C'est aujourd'hui un **échec total et catastrophique**. 
> Les processus de fond de l'agent plantent de manière récurrente sur MIDGARD, la partition `/tmp/` a saturé le disque dur, les quotas d'API ont explosé avec des coûts prohibitifs, et les vidéos générées sont régulièrement tronquées ou corrompues.
> 
> Voici la reconstitution historique objective des causes et mécanismes de ce naufrage technique.

---

## 2. Reconstitution Narrative de la Catastrophe

L'implémentation initiale de la skill `tesla-video-director` s'est déroulée sans incident technique apparent. Le smoke-test de 3 secondes a fonctionné de manière nominale. Cependant, la dérive s'est installée dès l'instant où le sous-agent a été sollicité pour traiter des volumes de données réels (transcription et découpage de films longs de plus d'une heure).

*   **Étape 1 (Débordement Mémoire)** : MoviePy chargeant les frames vidéo sous forme de tableaux NumPy volumineux en RAM, l'absence de fermeture systématique des descripteurs de fichiers (`.close()`) dans les scripts de pipeline a provoqué une fuite mémoire silencieuse. Lors du traitement séquentiel de clips, MIDGARD a déclenché le `OOM Killer` (Out Of Memory) d'Linux, tuant le processus de l'agent.
*   **Étape 2 (Saturation Disque)** : Les découpages successifs de vidéos et les pistes audio extraites n'ont pas fait l'objet d'une routine de nettoyage automatique. Les répertoires temporaires se sont accumulés jusqu'à saturer le disque local, bloquant l'indexation Alexandria et le fonctionnement du second cerveau.
*   **Étape 3 (Rupture d'API & Blocages de Sécurité)** : Les blocages de sécurité géographiques liés au Video-to-Video dans l'EEE ont forcé le sous-agent à basculer de manière non contrôlée sur des requêtes alternatives, générant des milliers de requêtes en boucle de retry et provoquant le bannissement temporaire de nos clés API (erreurs HTTP 429 et quota épuisé).
*   **Étape 4 (Rupture de Confiance)** : L'accumulation d'erreurs silencieuses sans journalisation adéquate a fini par convaincre Lord Mahonheim de désactiver définitivement le sous-agent.

---

## 3. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)
*   [ ] **Facteur 1 : Fuite Mémoire NumPy/MoviePy** : Manque de libération explicite des ressources (context managers absents) lors de la manipulation des objets `VideoFileClip` et `AudioFileClip`.
*   [ ] **Facteur 2 : Accumulation d'assets orphelins** : Aucun script ou tâche cron de nettoyage n'a été planifié pour purger les fichiers temporaires (`.mp4`, `.wav`, `.png` intermédiaires).
*   [ ] **Facteur 3 : Instabilité de l'API de transcription Groq (Whisper-1)** : Absence de gestion résiliente des limites de taux de requêtes (Rate Limits RPM/TPM), bloquant les scripts sur les fichiers audio volumineux segmentés en rafale.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)
*   **Hypothèse non vérifiée 1 :** Nous avons supposé que l'Opérateur n'enverrait que des vidéos aux ratios standard (`16:9` ou `9:16`). En réalité, des vidéos capturées avec des caméras ou écrans exotiques font planter la génération d'Omni Flash ou déforment l'image finale.
*   **Hypothèse non vérifiée 2 :** Nous pensions que `yt-dlp` fonctionnerait indéfiniment en local sans mise à jour. En réalité, les changements fréquents de protocoles des plateformes de streaming nécessitent des mises à jour constantes de `yt-dlp`, sans quoi les téléchargements de streams échouent en renvoyant des exceptions Python non capturées.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)
1. **Signal 1 :** Augmentation du temps de rendu de 20 % d'une session à l'autre, signalant une fragmentation de la swap ou des processus zombies `ffmpeg` non tués.
2. **Signal 2 :** Apparition d'avertissements de dépréciation (Deprecation Warnings) dans le journal d'exécution lors de l'import du package `google-genai` après des mises à jour automatiques du SDK.
3. **Signal 3 :** Taux d'utilisation de l'espace disque de `/tmp/` augmentant de manière exponentielle de plus de 10 Go par semaine.

---

## 4. Plan de Résilience & Checklist de Prévention

Pour éviter que ce scénario catastrophe ne se produise dans le monde réel, les contre-mesures obligatoires suivantes doivent être appliquées au plan initial :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement (Seuil) |
| :--- | :--- | :--- |
| Fuite mémoire MoviePy | Encapsuler obligatoirement l'utilisation des clips dans des blocs `with` (context manager) et forcer le garbage collection. | Toujours actif |
| Accumulation disque | Implémenter un script de nettoyage de fin de tâche `clean_tmp.py` qui s'exécute de manière idempotente. | Après chaque tâche |
| Rate Limits Groq | Ajouter un algorithme de backoff exponentiel avec gigue (jitter) pour toutes les requêtes de transcription Whisper. | Code HTTP 429 |
| Obsolescence `yt-dlp` | Planifier une vérification et mise à jour automatique régulière de la dépendance (`pip install -U yt-dlp`). | Hebdomadaire |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Mesure 1 :** Validation stricte des ratios vidéo d'entrée avant envoi à Omni Flash.
- [ ] **Mesure 2 :** Limite stricte de la taille brute des vidéos locales à 500 Mo pour l'analyse, forçant la compression ffmpeg préalable.
- [ ] **Mesure 3 :** Présence d'un bloc de capture d'exceptions global dans `generate_video.py` empêchant le plantage silencieux.

---
*Rapport généré et validé localement sur MIDGARD par Tesla.*
---
SHA256: e8a01643a996a38642d9aea348e9a038e53c7e4bea94f01618a076922b84a707
