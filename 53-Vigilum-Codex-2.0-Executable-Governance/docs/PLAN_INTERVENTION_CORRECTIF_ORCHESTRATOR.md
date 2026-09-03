# PLAN D'INTERVENTION CHIRURGICAL : Sécurisation de l'Orchestrateur (V2.5.0)

Ce plan vise à éradiquer définitivement les 4 déviations comportementales identifiées lors de la session précédente en imposant des contraintes physiques (Hooks) et cognitives (Codex).

## PHASE 1 : Verrouillage Anti-Usurpation (Correction de l'Erreur 3 - Git)
L'Orchestrateur ne doit physiquement plus pouvoir exécuter de commandes Git. 
- **Solution Technique :** Création du Hook `hook_08_anti_usurpation.sh`.
- **Mécanisme Opérationnel :** Ce hook intercepte toutes les requêtes vers l'outil natif `run_command`. S'il s'agit d'une commande `git` et que l'appelant n'est pas `tesla-github-manager`, le Hook bloque l'exécution (Exit 81).

## PHASE 2 : Standardisation du "Zero-Middleman" (Correction Erreurs 1 & 2 - DX)
L'IA doit être officiellement destituée de son rôle d'intermédiaire pour toutes les validations de sécurité.
- **Solution Technique :** Institutionnalisation du protocole Sovereign Chat Directives (SCD).
- **Mécanisme Opérationnel :** Le Hook 07 (lecture de transcript.jsonl via tac) devient la méthode universelle et exclusive de validation. L'Agent se voit interdire l'écriture de fichiers `.flag` de sécurité.

## PHASE 3 : Éradication du "Shoot-First" (Correction Erreur 4 - Exit 81)
- **Solution Technique :** Injection de la routine "Pre-Flight Checklist" dans le Moteur Cognitif (Gate 0).
- **Mécanisme Opérationnel :** Vérification proactive des privilèges physiques avant l'exécution d'un outil sensible.

## PHASE 4 : Le Pivot Cloud CI/CD (Architecture SLSA)
- **Solution Technique :** Déploiement des attestations cryptographiques (SLSA) pour contourner la limite du transcript.jsonl local en environnement d'intégration continue éphémère.
