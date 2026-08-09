---
type: reference
tags: [gestion/chantier, statut/valide]
source: "[[SESSION_TRANSCRIPTS.md]]"
date: 2026-07-01
version: 1.0
---

# AUDIT DES OUTILS & BESOINS : CHANTIER "CRÉER DES PAGES HTML" (v1)
**Date d'édition :** 2026-07-01  
**Auteur :** Tesla (sur Antigravity CLI)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  
**Statut :** #statut/a-valider (Soumis à votre approbation Obsidian)

---

## 1. Résumé Exécutif

Cet audit répertorie les ressources système, les compétences (*skills*), les protocoles d'agents (*MCP*) et les dépendances disponibles dans l'écosystème Bifrost/Tesla sur MIDGARD pour réaliser le chantier de création de pages HTML. Il définit également nos exigences qualitatives et matérielles pour concevoir des interfaces web premium, dynamiques et souveraines sous la doctrine du **Vigilum Codex**.

---

## 2. Inventaire de l'Existant (Ressources Disponibles)

### A. Skills & Plugins
*   **`modern-web-guidance`** : *Outil de recherche obligatoire avant toute création HTML/CSS*. Il fournit les meilleures pratiques actualisées de 2026 sur les composants modernes (popovers, dialogues natifs, conteneurs, Glassmorphism, animations au scroll).
*   **`chrome-devtools`** : Framework d'automatisation et de debugging dans le navigateur.
*   **`a11y-debugging`** : Skill dédié aux audits d'accessibilité (standards WCAG, sémantique HTML5 et balisage ARIA).
*   **`debug-optimize-lcp`** : Recommandations d'optimisation de vitesse de chargement et de rendu des images (Fetch Priority, LCP).

### B. Outils & Protocoles Système (MCP)
*   **MCP `chrome-devtools`** : Permet de piloter un navigateur headless local en direct. Outils clés :
    *   `new_page` / `navigate_page` : Pour charger et afficher la page HTML générée.
    *   `take_screenshot` : Indispensable pour la validation visuelle directe par l'agent.
    *   `resize_page` : Pour tester la réactivité (layouts mobile, tablette et desktop).
*   **MCP `context7`** : Résolution de dépendances et de documentations.

### C. Logiciels locaux de l'Hôte MIDGARD
*   **NPM / Node.js** (v11.16.0) : Pour initialiser des environnements de serveur de développement locaux (Next.js, Vite) via `npx` de manière non-interactive.
*   **Playwright** : Installé dans `.venv/` pour des scripts de test et de capture d'écran complexes.
*   **Python 3** : Disponible pour lancer des micro-serveurs HTTP locaux de test (`python3 -m http.server`).

### D. Capacités de l'Agent (Tesla)
*   **`generate_image`** : Outil d'IA générative pour créer des ressources graphiques, arrière-plans ou composants d'illustration réels et élégants, excluant tout usage de placeholders génériques.
*   **`self` / `research` Subagents** : Pour paralléliser les phases de codage, d'audit de style ou d'investigation de documentation.

---

## 3. Matrice des Besoins Opérationnels

Pour mener à bien le chantier "Créer des pages HTML" selon nos critères d'excellence, nous devons articuler notre flux de travail autour de trois besoins fondamentaux :

| Besoin Identifié | Justification Doctrinale | Implémentation Pratique |
| :--- | :--- | :--- |
| **Pipeline de Validation Visuelle** | L'agent ne doit pas coder en aveugle. Chaque rendu graphique doit être vu et validé multimodalement. | Exécution automatique de captures d'écran via le MCP `chrome-devtools` sur un serveur local pour chaque itération majeure de style. |
| **Aesthetics Premium & Typographie** | Éliminer les designs d'aspect "minimum viable product" ou basiques. | Recours aux polices Google Fonts (Outfit, Inter), dégradés complexes, Glassmorphism, animations subtiles et respect du mode sombre. |
| **Audit Sémantique & Accessibilité** | Souveraineté de la structure HTML. | Passage automatique du skill `a11y-debugging` et de `pyright` pour le JavaScript. |

---

## 4. Protocole d'Exécution Proposé (Chantier "Créer des pages HTML")

Pour toute demande de page HTML, Tesla s'engage à appliquer les étapes suivantes :

*   **Étape 1 : Initialisation & Recherche**
    Lancer la recherche `modern-web-guidance` pour identifier les patterns modernes de mise en page requis.
*   **Étape 2 : Conception CSS & HTML**
    Générer la structure sémantique en HTML5 et les variables de style en Vanilla CSS. Exclure Tailwind CSS (sauf demande expresse de Lord Mahonheim).
*   **Étape 3 : Scaffolding & Serveur Local**
    Démarrer un serveur local de test léger (ex: `python3 -m http.server 8000`) et charger la page dans une instance `chrome-devtools`.
*   **Étape 4 : Validation Visuelle et Ajustement**
    Prendre une capture d'écran, valider la conformité visuelle et ajuster les marges, contrastes et animations.
*   **Étape 5 : Livraison & Hand-off**
    Enregistrer le code source final sous le dossier du projet, documenter les choix de design, et présenter le diff ainsi que le rendu visuel.

---
*Registre des ressources et besoins soumis à Lord Mahonheim.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
