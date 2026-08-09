---
type: reference
tags: [securite/premortem, statut/valide]
source: "[[plan_stabilisation_cognitive]]"
date: 2026-06-28
version: 3.0
---

# RAPPORT D'AUDIT PREMORTEM : ANCRAGE MÉMORIEL PAR PROMPT-CACHING & EMBEDDINGS (LLAMA.CPP) - UPDATED
**Date de l'audit :** 2026-06-28  
**Analyste :** Tesla (sur Antigravity CLI)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)

---

## 1. Audit : Le Passage de Relais A-Cognitif (Le Point de Rupture)

### Le Problème de Transition
Lorsqu'un modèle (ex: Gemini Cloud) passe le relais à un autre (ex: GPT-OSS Local), le nouveau modèle démarre dans un état d'**amnésie contextuelle totale**. N'ayant pas participé aux interactions passées, il doit reconstruire sa compréhension à partir de logs textuels bruts. 

Cette reconstruction échoue systématiquement sur les modèles intermédiaires car :
1. **L'évaluation à froid (Cold Start)** de milliers de tokens d'historique sature la fenêtre de contexte et provoque des hallucinations.
2. **Le biais d'ordre de lecture** fait que le modèle s'accroche aux premières correspondances textuelles trouvées, même si elles sont obsolètes.
3. Il n'existe pas de **pont d'état interne** transmettant la dynamique cognitive de la session précédente.

### La Solution llama.cpp
L'utilisation de la suite `llama.cpp` permet d'implémenter deux mécanismes physiques de transfert de mémoire pour garantir qu'un modèle reprenant la main acquiert instantanément et sans effort le niveau de compréhension exact de son prédécesseur.

---

## 2. Plan d'Intervention : Le Passage de Relais par llama.cpp

### Mécanisme A : Partage physique de KV-Cache (Modèles de même architecture)
Pour les transitions entre modèles locaux partageant une architecture de tenseurs similaire (ex: Qwen-Coder-8B $\rightarrow$ Qwen-Coder-32B, ou bascule de quantification Q4_0 $\rightarrow$ Q8_0) :
1. **Sauvegarde de Session (`--session-file`)** : `llama.cpp` supporte la sauvegarde physique du Key-Value Cache (KV-Cache) dans un fichier binaire (ex: `memory/session_state.bin`).
2. **Passage de Relais à chaud** : À la fin de l'interaction, le modèle sortant écrit son KV-cache sur le disque. Le modèle entrant se charge en ré-important ce fichier.
3. **Effet** : Le nouveau modèle hérite de l'état d'activation neuronal exact de la conversation. Il n'a aucun calcul d'évaluation de prompt à effectuer, le premier token est généré instantanément, et la fidélité de la mémoire de discussion est absolue (0% de risque de dérive ou d'oubli).

### Mécanisme B : Indexation Vectorielle de Passage de Relais (Modèles Cloud vs Locaux)
Pour les transitions hybrides (ex: Gemini Cloud $\rightarrow$ GPT-OSS Local) où le KV-cache n'est pas transférable :
1. **Inférence d'Embeddings en Arrière-Plan** : Un micro-modèle d'embedding sur `llama.cpp` (ex: `nomic-embed-text`, 140 Mo RAM) tourne en tâche de fond sur `http://localhost:8082`.
2. **Vectorisation Atomique du Tour** : À chaque fin d'interaction, le modèle en cours résume le statut cognitif en 3 points (Ce qui est fait | L'état du workspace | La tâche suivante). Ce résumé est vectorisé par `llama.cpp` et stocké dans une table vectorielle locale.
3. **Rappel Sémantique d'Initialisation (RAG d'Amorçage)** : Au démarrage, le nouveau modèle exécute une recherche de similarité via le serveur d'embeddings local. Il extrait uniquement la dernière situation stabilisée et les faits pertinents, injectés en tête de son contexte. Le modèle s'aligne instantanément sans lire l'historique textuel géant.

---

## 3. Postulat de l'Échec Virtuel (T+3 Mois - Stress-Test)

> [!WARNING]
> Nous sommes le **2026-09-28**.
> Le système de transfert de mémoire basé sur `llama.cpp` a été déployé. C'est un **échec catastrophique**.
> Suite à des corruptions répétées de fichiers binaires de session et à des désalignements d'embeddings, l'agent Tesla a confondu des sessions différentes, ré-écrit des fichiers sains avec du code datant de deux mois, et est resté bloqué dans des boucles de raisonnement infinies.

### Reconstitution Narrative de la Catastrophe
1. **Étape 1 (Incompatibilité de KV-Cache) :** Lors d'une bascule de version de modèle (de Llama-3-8B à Llama-3.1-8B), l'agent a tenté de forcer le chargement du fichier de session `session_state.bin` généré par l'ancien modèle. L'incompatibilité des dimensions de tenseurs a provoqué un crash silencieux du backend C++ de `llama.cpp` (Segmentation Fault).
2. **Étape 2 (Régression sur le Fallback) :** Face au crash de l'importation de session, l'agent a basculé sur le mécanisme B (Embeddings). Cependant, le serveur d'embeddings local (`llama-server`) était indisponible suite à un conflit de port réseau. Le script a échoué silencieusement en renvoyant des vecteurs nuls.
3. **Étape 3 (Amnésie et boucle cognitive) :** Le nouveau modèle s'est amorcé sur des extraits vides. Suivant la directive d'amorçage mais ne trouvant aucune donnée récente, il s'est basé sur un ancien checkpoint d'indexation datant de juillet 2026. L'agent a cru que le projet GitHub n'était pas encore publié, a écrasé la production par du code obsolète, puis a sauvegardé ce nouvel état corrompu dans le fichier de session, verrouillant l'amnésie pour les sessions suivantes.

---

## 4. Analyse Tripartite des Risques (Gary Klein Model)

### A. L'Avocat du Diable (Causes Techniques & Factuelles)
*   [ ] **Facteur 1 : Instabilité du chargement binaire de session**
    Le format des fichiers `--session` de `llama.cpp` est très sensible aux variations de version du binaire compilé et des configurations du modèle (température, pénalité de répétition, taille de contexte). Un simple changement de paramètre rend le fichier binaire invalide ou provoque un plantage de segmentation.
*   [ ] **Facteur 2 : Risque de goulot d'étranglement réseau local (Port 8082)**
    Si le serveur d'embeddings local est tué ou bloqué par un pare-feu, le pont d'amorçage s'effondre.
*   [ ] **Facteur 3 : Pollution par embeddings obsolètes**
    Si la base vectorielle locale n'est pas purgée des résumés intermédiaires obsolètes, le RAG d'amorçage risque de remonter de vieilles fiches d'état sémantiquement proches mais chronologiquement dépassées.

### B. L'Inspecteur des Angles Morts (Hypothèses Cachées non Validées)
*   **Hypothèse non vérifiée 1 :** Nous avons supposé que le KV-Cache était interpolable entre des modèles différents (ex: de Qwen à Llama). C'est techniquement faux. Le partage physique de session est strictement limité aux modèles de même architecture et de mêmes dimensions.
*   **Hypothèse non vérifiée 2 :** Nous avons supposé que la recherche vectorielle remonterait toujours la "vérité présente". Or, la similarité cosinus mesure la ressemblance sémantique, pas la fraîcheur temporelle. Un vieil échec peut être sémantiquement plus proche de la requête qu'un succès récent, induisant le modèle en erreur.

### C. La Vigie des Signaux Faibles (Indicateurs Précurseurs)
1. **Signal 1 :** Segmentation faults ou erreurs de chargement de session signalés par `llama.cpp` dans les logs système.
2. **Signal 2 :** Score de similarité cosinus trop bas (< 0.70) lors de la recherche du dernier état d'amorçage, indiquant une rupture de la chaîne d'indexation.
3. **Signal 3 :** Augmentation de la latence de première réponse (Time to First Token) indiquant que le cache de prompt a été invalidé et que tout le contexte est réévalué.

---

## 5. Plan de Résilience & Checklist de Prévention

Pour neutraliser ces risques et garantir la fidélité de la mémoire universelle, les contre-mesures obligatoires suivantes sont appliquées :

| Risque Identifié | Action Préventive Obligatoire | Indicateur de Déclenchement |
| :--- | :--- | :--- |
| **Incompatibilité du KV-Cache** | Le script de chargement doit valider la signature MD5 du modèle et sa configuration avant d'importer le fichier binaire de session. Si inadéquation, fallback propre sur le mode RAG d'amorçage. | Signature du modèle modifiée. |
| **Biais temporel de recherche sémantique** | Coupler la recherche vectorielle à un filtre chronologique strict : la recherche d'amorçage doit être triée par `date_modified DESC` en plus de la similarité vectorielle. | `rank` vectoriel insuffisant. |
| **Crash du serveur d'embeddings** | Intégrer un fallback local léger en Python natif (ex: recherche hybride BM25 textuelle sans réseau) si l'API `llama-server` ne répond pas sous 2 secondes. | Timeout HTTP > 2000 ms. |

### Checklist de Sûreté Pré-Exécution :
- [ ] **Validation de l'état du serveur** : Avant d'initialiser l'agent, le CLI doit effectuer un ping sur `http://localhost:8082/v1/models` pour valider l'intégrité de la couche d'embeddings.
- [ ] **Sauvegarde de secours Markdown** : Même en cas d'utilisation du cache de session binaire, le statut textuel brut de clôture de session doit être écrit en clair dans `PROJECT_STATE.md` comme garantie ultime de secours.

---
*Rapport généré et validé localement sur MIDGARD par Tesla.*
