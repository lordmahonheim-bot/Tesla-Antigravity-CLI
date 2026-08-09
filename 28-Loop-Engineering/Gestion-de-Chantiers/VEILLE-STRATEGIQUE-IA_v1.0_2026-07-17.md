# Cahier des Charges : Veille Stratégique IA

## 1. Contexte
Lord Mahonheim a découvert de manière réactive, via des réseaux sociaux tiers, une information stratégique concernant l'évolution de "NotebookLM" vers "Gemini Notebook". Il est nécessaire de repasser à l'offensive et d'anticiper l'information.

## 2. Objectif Principal
Déployer une boucle de veille stratégique automatisée, asynchrone et qualifiée, portant sur l'actualité de l'Intelligence Artificielle, avec une priorité absolue sur l'écosystème **Gemini** et **Antigravity CLI**.

## 3. Périmètre
- Annonces officielles, fuites (leaks), et évolutions techniques majeures (nouvelles fonctionnalités, rebranding, deprecation).
- Cibles prioritaires : Google Gemini (API, LLM, Notebook, écosystème) et Antigravity CLI (Mises à jour, nouvelles implémentations).
- Cibles secondaires : Avancées majeures en Agentic AI ou Local LLMs ayant un impact sur la doctrine Tesla.

## 4. Dépendances & Outils
- Commande d'exécution : Invocation à la demande via `invoke_subagent` (Agent `tesla-arcanis-360`).
- Outil d'extraction : Wrapper `agent-reach` (pour Reddit, GitHub, blogs officiels).

## 5. Livrables Attendus
- Un rapport analytique structuré (Explication pédagogique, Fact-Checking, Stratégie et analyse SWOT).
- Le rapport doit se concentrer sur les nouveautés depuis la dernière exécution.

## 6. Budget Cognitif (Tokens)
À optimiser. Invoquer l'agent `tesla-arcanis-360` avec le modèle le plus adapté à l'analyse SWOT (idéalement `pro`).

## 7. Critères d'Acceptation
- Exécution "à la demande" ("on-demand") sur requête de l'opérateur.
- Couverture ciblée : Sources officielles, GitHub, Reddit.

## 8. Phases d'Exécution
1. Cadrage strict validé (À la demande, sources officielles + Reddit/GitHub, rapport SWOT).
2. Invocation de l'agent `tesla-arcanis-360` avec le prompt de recherche.
3. Restitution du rapport certifié à l'opérateur.
4. Sauvegarde de la date de dernière exécution pour la prochaine itération.

## 9. Analyse des Risques et Mitigation
- **Risque :** Surcharge cognitive et bruit (trop d'articles inutiles).
- **Mitigation :** Instructions strictes dans le prompt pour n'isoler que les faits (Fact-Checking) et refuser les rumeurs non fondées.

## 10. Journal de Bord
- **2026-07-17 :** Déclaration de l'ouverture du chantier par Lord Mahonheim suite à la découverte du rebranding Gemini Notebook. Création du cahier des charges.

## 11. Clôture
- Statut actuel : 🟢 Ouvert
- Date de clôture : N/A
