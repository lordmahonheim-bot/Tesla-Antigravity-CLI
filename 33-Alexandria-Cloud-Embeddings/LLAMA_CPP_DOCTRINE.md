# Doctrine llama.cpp — Usage strictement outillage éphémère

Sous la doctrine du Vigilum Codex et pour préserver la stabilité matérielle de MIDGARD (8 Go RAM, CPU pur) :

## 1. Prohibition Absolue d'Inférence Résidente
*   Il est formellement interdit de charger des modèles d'inférence en RAM à titre permanent.
*   L'exécution de démons persistants de type `llama-server` est interdite.
*   L'usage d'outils interactifs comme `llama-cli` en mode inférence est interdit.
*   L'importation de bibliothèques liant l'interpréteur Python à des runtimes d'inférence (telle que `llama-cpp-python`) est strictement interdite dans les scripts de production.

## 2. Périphérie d'Usage Autorisé (Outillage)
L'usage de la suite logicielle `llama.cpp` est restreint exclusivement aux tâches de préparation et d'optimisation de modèles :
*   Conversion de formats natifs (ex. HuggingFace) vers le format standardisé GGUF.
*   Quantification (compression de poids) vers des formats compressés hautement optimisés (types `Q4_K_M`, `Q5_K_M` ou `Q8_0`).
*   Découpage (splitting) ou fusion (merging) de fichiers GGUF.

## 3. Pattern d'Isolation et de Nettoyage Éphémère
Chaque tâche d'outillage doit se plier aux contraintes matérielles suivantes :
1.  **Vérification d'Espace Disque** : S'assurer que le système dispose d'au moins 8 Go d'espace libre sur la partition cible avant de démarrer.
2.  **Dossier Temporaire Dédié** : L'ensemble des opérations doit se dérouler dans un répertoire de travail jetable isolé sous `/tmp/llama-pack-XXXXXX` (généré via `mktemp -d`).
3.  **Appel Subprocess Hermétique** : L'outil `llama-quantize` doit être invoqué sous forme de processus externe éphémère via Python `subprocess.run` avec des limites de ressources explicites.
4.  **Validation Physique** : Après écriture du fichier quantifié final, son intégrité doit être attestée en vérifiant la présence du header magique de fichier GGUF (`0x46554747`, soit `GGUF` en ASCII).
5.  **Purge Inconditionnelle** : Une routine de nettoyage (type `trap EXIT` en bash ou bloc Python `finally`) doit détruire intégralement le dossier temporaire `/tmp/llama-pack-*` après exécution, que l'opération ait réussi ou échoué.

---
*Fiche de doctrine canonique certifiée sur MIDGARD par Tesla Curator Prime.*
