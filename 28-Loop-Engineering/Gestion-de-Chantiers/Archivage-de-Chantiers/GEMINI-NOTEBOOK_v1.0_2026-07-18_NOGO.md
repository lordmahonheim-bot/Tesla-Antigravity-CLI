# Cahier des Charges : Gemini Notebook (Chantier 017)

## 1. Contexte
Les précédents brouillons documentaires présentaient des failles (dispersion, capacités fantômes comme le PIIScrubber non implémenté, absence de gouvernance). L'intervention vise à clarifier et systématiser l'usage de Gemini Notebook en tant que fonderie externe (Cloud Computer).

## 2. Objectif Principal
Déployer l'architecture "Human Data Bus" et implémenter les garde-fous nécessaires pour tirer le maximum de Gemini Notebook (traitement analytique, distillation de gros corpus) sans compromettre la sécurité et la souveraineté des données de MIDGARD.

## 3. Périmètre
- Définition du Gate de Triage amont (Classification : données publiques vs sensibles).
- Mise en place du module de sécurité local `PIIScrubber` (Filtrage obligatoire pour les données sensibles uniquement).
- Fusion et consolidation documentaire (Création de `GEMINI_NOTEBOOK.md` canonique).
- Standardisation des modèles de carnets et implémentation du Gate de Vérification / Fact-Checking aval anti-hallucination.
- Intégration stricte dans `FORCE_TOOLING.md` et `AGENTS.md`.
- **Interdiction Formelle :** L'usage de Webwright / Playwright ou toute automatisation navigateur vers Gemini Notebook est strictement proscrit.

## 4. Dépendances & Outils
- Scripts Python (à développer pour `PIIScrubber`).
- Sous-agents : `tesla-arcanis-360` (pour le Cloud Computer) et `tesla-curator-prime` (pour la distillation).
- Alexandria (pour l'injection finale certifiée).

## 5. Livrables Attendus
1. Fichier de doctrine canonique `GEMINI_NOTEBOOK.md`.
2. Script de sécurité `PIIScrubber`.
3. Checklists `Human-in-the-Loop` et modèles de carnets.
4. Mises à jour des registres de gouvernance (`FORCE_TOOLING.md`, `AGENTS.md`).

## 6. Budget Cognitif (Tokens)
Opérations de développement de scripts (légères) et de refactorisation documentaire (Curator Prime). L'usage de Gemini Notebook déchargera MIDGARD des calculs lourds futurs.

## 7. Critères d'Acceptation & Clôture
- Le triage est fonctionnel (les corpus publics contournent le scrubber, les locaux y passent obligatoirement).
- Le `PIIScrubber` passe 100% de la suite de tests sans aucun faux négatif (critère bloquant).
- Le Gate de Fact-Checking humain est imposé avant toute injection d'un distillat dans Alexandria.
- L'enregistrement dans `FORCE_TOOLING.md` n'intervient **qu'après** la validation complète du PIIScrubber (zéro capacité fantôme).

## 8. Phases d'Exécution
1. Développement des garde-fous locaux (Triage amont + Code et Test du `PIIScrubber`).
2. Création des standards opératoires et du Gate de Vérification aval.
3. Consolidation documentaire et Gouvernance (Création du `GEMINI_NOTEBOOK.md` canonique et certification finale dans `FORCE_TOOLING.md`).

## 9. Analyse des Risques et Mitigation
- **Risque de Fuite :** Fuite de données locales vers les serveurs cloud de Google.
  - **Mitigation :** Triage amont systématique et passage par le `PIIScrubber` pour tout ce qui n'est pas publiquement classifié.
- **Risque d'Hallucination :** Injection de fausses données (hallucinations du cloud) dans Alexandria.
  - **Mitigation :** Gate de Vérification aval (Fact-Checking humain) obligatoire avant chaque injection. Le Human Data Bus n'est pas aveugle.
- **Risque de Dérive :** Tentatives d'automatisation d'interface.
  - **Mitigation :** Interdiction explicite de Webwright/Playwright dans la doctrine.

## 10. Journal de Bord
- **2026-07-18 :** Audit des documents initiaux par `tesla-curator-prime`. Rédaction du Plan d'Intervention et création de ce cahier des charges.

## 11. Clôture
- Statut actuel : 🟢 Ouvert
- Date de clôture : N/A
