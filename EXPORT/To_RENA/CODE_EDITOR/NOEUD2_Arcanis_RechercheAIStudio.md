# Rapport d'Analyse Deep Research : Google AI Studio & Firebase Studio (NŒUD 2)

## 1. Google AI Studio : Capacités de Prototypage pour Développeurs
Google AI Studio se positionne comme un "playground" ou bac à sable orienté développeur, optimisé pour réduire drastiquement le temps entre l'idée et l'intégration de code.

*   **Prompt Engineering Visuel & Tests :** Interface permettant d'ajuster dynamiquement le *temperature*, *top-p*, et de structurer des prompts (few-shot, instructions système).
*   **"Vibe Coding" & UI Generation :** Capacités récentes de prototypage visuel permettant de générer des interfaces à partir de maquettes, mockups ou captures d'écran, accélérant la création de proof-of-concepts.
*   **Génération d'API (Get Code) :** Transition fluide du bac à sable vers le code de production avec génération automatique de requêtes API et snippets de code dans plusieurs langages (Python, JS, Go, etc.).
*   **Multimodalité native :** Test direct des modèles Gemini sur des images, vidéos, et documents de manière intégrée.

## 2. Transition Firebase Studio (Sunset 22 Mars 2027)
Google rationalise son écosystème d'outillage IA. Firebase Studio, qui a servi de plateforme expérimentale, sera décommissionné au profit de deux axes :
*   **Google AI Studio :** Devient le centre névralgique pour le prototypage rapide et l'ingénierie de prompt en ligne. Les services Firestore/Auth y ont été intégrés.
*   **Google Antigravity :** Devient la solution de référence pour les workflows "code-first", multi-agents et autonomes.

**Impact développeur :** Plus aucune création de workspace Firebase Studio n'est permise (depuis juin 2026). Une migration des données (prompts, configurations) est impérative avant mars 2027. Les services cloud sous-jacents de Firebase, eux, continuent.

## 3. Risques de Vendor Lock-in
L'adoption profonde de Google AI Studio expose à plusieurs formes de dépendances :
*   **Couplage API / Modèle :** Les workflows optimisés spécifiquement pour le comportement et le format de réponse de Gemini sont difficiles à porter vers OpenAI ou Anthropic sans réécrire l'orchestration.
*   **Lock-in d'infrastructure :** L'intégration native avec Vertex AI et l'écosystème Google Cloud (facturation, CI/CD, stockage vectoriel) rend la sortie de l'écosystème coûteuse et techniquement complexe.
*   **Risque opérationnel :** Une dépendance exclusive expose aux changements unilatéraux de tarification, quotas ou dépréciation de modèles.

**Mitigation recommandée :** Implémenter des couches d'abstraction (interfaces agnostiques), utiliser des frameworks modulaires et conteneuriser (Docker) le cœur de la logique d'application.

## 4. Extraction pour le Plan d'Intervention (Profil MIDGARD)
Pour la configuration matérielle restreinte (8 Go RAM, HDD) et l'intégration avec Antigravity CLI :
1.  **Usage de Google AI Studio :** Doit être cantonné au rôle de **Sandbox externe (navigateur)** pour l'expérimentation rapide. Il ne remplace pas l'éditeur de code local.
2.  **Séparation des préoccupations :** Antigravity CLI s'occupera des workflows complexes. L'éditeur de code local devra être extrêmement léger (Neovim/Helix ou VS Code hyper-optimisé) pour ne pas concurrencer Chrome (nécessaire pour AI Studio) et le daemon AGY sur la RAM.
3.  **Architecture Agnostique :** Le plan devra inclure des scripts ou une structure de code (via l'éditeur local) permettant d'abstraire les appels à Gemini, protégeant ainsi le projet contre le vendor lock-in induit par la facilité d'usage d'AI Studio.
