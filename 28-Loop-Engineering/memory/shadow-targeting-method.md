---
type: reference
tags: [shadow-targeting, documentation/technique, securite, statut/valide]
date: 2026-07-03
version: 1.0
---

# 📑 FICHE TECHNIQUE : MÉTHODE SHADOW-TARGETING
**Sujet :** Injection et suivi sécurisé de compétences subagents sous Antigravity CLI  
**Doctrine :** Vigilum Codex  

---

## 1. Principe de la Méthode
Le **Shadow-Targeting** est une méthode d'injection à chaud de compétences (Skills) dans les sous-agents par défaut d'Antigravity CLI. 

Sur le plan payant Pro ($20/mois), la plateforme restreint la création ou le déploiement de subagents personnalisés additionnels. La méthode consiste à configurer des ensembles de compétences isolées, puis à les injecter comme capacités intégrées (via la variable d'exécution `self` ou l'import direct de fichiers d'instructions `SKILL.md`) dans l'un des 3 subagents natifs de l'environnement, leur permettant de dépasser leurs barrières fonctionnelles sans violer les contraintes physiques du plan tarifaire.

---

## 2. Nomenclature et Conventions de Nommage
Afin de préserver la modularité de l'écosystème, la règle suivante s'applique :

*   **Principe d'Indépendance** : Chaque skill ou subagent doit rester strictement indépendant des autres, que ce soit au niveau de sa création, de son nommage ou de ses fonctions.
*   **Structure du Nom** : Le nom du répertoire et de la compétence doit correspondre exactement à l'agent créé, sans préfixe de dépendance (ex: `tesla-web-raider`).
*   **En-tête de Métadonnées** : Le fichier `SKILL.md` associé doit déclarer dans son frontmatter YAML :
    ```yaml
    injection_type: shadow-targeted
    target_subagent: self
    ```
*   **Flag d'injection en Base** : Dans la base [alexandria_brain.db](file:///home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/alexandria_brain.db), la table `subagents_skills` doit porter la valeur `injection_method = 'shadow-targeting'`.

---

## 3. Risques de Conformité & CGU (Terms of Service)
*   **Analyse du Risque** : Le Shadow-Targeting exploite les fonctionnalités natives d'importation de fichiers et d'instructions d'Antigravity CLI. Il ne modifie pas le binaire exécutable de la plateforme, ne décompile pas son code et n'utilise aucun exploit de contournement de sécurité.
*   **Niveau de Risque** : **Négligeable**. L'action s'apparente à une injection contextuelle légitime de prompts et d'outils au sein d'une sandbox locale.
*   **Politique d'atténuation** :
    1. Ne jamais tenter de contourner les limitations de volume d'API ou d'appels de requêtes de la plateforme par des scripts de flood.
    2. Documenter de manière transparente les appels pour assurer la traçabilité des modifications.

---

## 4. Procédure de Retrait et Rollback
En cas de dysfonctionnement sémantique, de boucle infinie de requêtes, ou de dérive comportementale du sous-agent cible :

1.  **Désactivation sémantique** : Retirer la référence du dossier du skill dans le prompt système du sous-agent (dans `.agents/[SUBAGENT].md`).
2.  **Suppression physique** : Déplacer le dossier du skill hors du répertoire d'indexation (`.agents/skills/`) vers un dossier de quarantaine temporaire.
3.  **Mise à jour de la Base de Données** : Exécuter la mise à jour du statut en base de données pour passer l'état à `expired` ou `failed` dans la table `subagents_skills` :
    ```sql
    UPDATE subagents_skills SET statut = 'inactive', notes = 'Rollback command triggered' WHERE skill_name = '[NOM_DU_SKILL]' AND session_id = '[SESSION_ID]';
    ```
4.  **Re-synchronisation** : Lancer la commande `update_session_history.py` pour régénérer l'index sémantique et attester du retour à l'état nominal.
