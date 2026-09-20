# Bridge Gemini → revue locale → Antigravity : implémentation corrigée

**2026-09-19 — remplace intégralement le prototype dangereux de ce document.**

L'ancien exemple `google.generativeai` + `gemini-1.5-pro` écrivait une réponse
non fiable dans un chemin `/tmp` fixe puis lançait `antigravity run` automatiquement.
Cela contredisait la revue humaine annoncée et ne démontrait aucune isolation.
Il a été retiré pour éviter sa réutilisation.

L'implémentation maintenue est désormais
[`tools/tesla_ai.py`](../../../tools/tesla_ai.py) :

- REST Gemini officiel, Python standard, sans navigateur ni SDK à installer ;
- `doctor` local, découverte `models`, puis `generate --allow-cloud` ;
- clé éphémère fournie par l'environnement, sans affichage ni paramètre d'URL ;
- entrée bornée depuis stdin ; aucune collecte automatique du dépôt ;
- artefacts Markdown privés, uniques, non exécutables ;
- erreurs API, quotas, réponses bloquées/tronquées : arrêt explicite ;
- **aucun subprocess, outil shell, appel AGY ni application automatique de patch**.

Lire le [guide TERMINATOR de référence](LIVRABLE_FINAL_AIStudio_Headless_Terminator.md)
pour la saisie du secret, la configuration des panneaux et la validation humaine.
Le passage à AGY est volontairement manuel tant que le binaire et ses capacités
n'ont pas été vérifiés sur MIDGARD. Le succès des tests hors ligne ne remplace pas
ce contrôle ni une validation Gemini réelle.
