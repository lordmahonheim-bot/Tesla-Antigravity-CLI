---
type: reference
tags: [technique/web, statut/valide]
source: "[[SESSION_TRANSCRIPTS.md]]"
date: 2026-07-01
version: 1.0
---

# GUIDE DES BONNES PRATIQUES & RÈGLES DE SYNTAXE HTML (v1)
**Date d'édition :** 2026-07-01  
**Auteur :** Tesla (sur Antigravity CLI)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  
**Statut :** #statut/valide (Validé pour indexation autonome)

---

## 1. Structure Sémantique Obligatoire (HTML5)

Chaque page HTML créée dans l'écosystème Bifrost doit s'appuyer sur une structure strictement sémantique pour optimiser le SEO, la clarté et l'accessibilité (A11y).

### Squelette Standard de Référence :
```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="[Description claire et concise de la page pour le SEO]">
  <title>[Titre unique et descriptif] - Écosystème Bifrost</title>
  
  <!-- Fonts Premium -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
  
  <!-- CSS Stylesheet principal -->
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

  <!-- En-tête Global -->
  <header>
    <nav aria-label="Navigation principale">
      <a href="/" class="logo">Bifrost</a>
      <ul>
        <li><a href="#chantiers">Chantiers</a></li>
        <li><a href="#status">Status</a></li>
      </ul>
    </nav>
  </header>

  <!-- Zone de Contenu Principal (Single h1 unique par page) -->
  <main id="main-content">
    <article>
      <header>
        <h1>[Titre Principal Unique]</h1>
        <p class="subtitle">[Texte d'introduction descriptif]</p>
      </header>
      
      <section id="features" aria-labelledby="section-title">
        <h2 id="section-title">Fonctionnalités Clés</h2>
        <div class="grid-container">
          <!-- Composants et Cards -->
        </div>
      </section>
    </article>
  </main>

  <!-- Pied de page -->
  <footer>
    <p>&copy; 2026 Écosystème Bifrost. Géré sous la gouvernance du Vigilum Codex.</p>
  </footer>

  <!-- Scripts JavaScript (Modulaires) -->
  <script type="module" src="js/app.js"></script>
</body>
</html>
```

---

## 2. Règles de Syntaxe et Standards de Code

### A. Règles Relatives au HTML
1.  **Sémantique d'abord** : Proscrire l'usage abusif de `<div>` pour tout ce qui relève de la navigation (`<nav>`), de l'en-tête (`<header>`), du pied de page (`<footer>`), des sections thématiques (`<section>`) ou des conteneurs d'éléments autonomes (`<article>`).
2.  **Identifiants uniques pour les tests** : Chaque élément interactif (boutons de soumission, champs de formulaires, liens d'onglets) doit comporter un attribut `id` unique et descriptif pour faciliter l'injection de scripts de test (Playwright) et de métadonnées.
3.  **Attributs ALT obligatoires** : Toute image doit avoir un attribut `alt` descriptif. Si l'image est purement décorative, utiliser `alt=""` pour que les lecteurs d'écran l'ignorent.
4.  **Boutons vs Liens** :
    *   Utiliser `<a>` uniquement pour la navigation vers une URL ou une ancre.
    *   Utiliser `<button>` pour déclencher des actions logiques (ouvertures de modals, soumissions de formulaires, modifications d'état).

### B. Règles Relatives au CSS (Vanilla CSS Moderne)
1.  **Variables CSS obligatoires** : Centraliser le design system (couleurs HSL, polices, espacements) à la racine `:root` de la feuille de style.
2.  **Mode Sombre (Dark Mode) Natif** : Prioriser l'intégration d'un mode sombre natif et harmonieux.
3.  **Layouts Flexbox et Grid** : Proscrire l'utilisation de floats pour le positionnement. Utiliser `display: grid` pour les structures bidimensionnelles complexes et `display: flex` pour l'alignement unidimensionnel.
4.  **Verrouillage des effets premium** :
    *   *Glassmorphism* : Utiliser `backdrop-filter: blur(10px)` couplé à une transparence HSL.
    *   *Transition* : Utiliser des transitions douces pour les hovers : `transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`.
5.  **Utilisation de sélecteurs avancés** : Préférer l'utilisation de sélecteurs modernes comme `:has()` pour styliser des parents d'éléments invalides, ou `:user-valid` pour la validation de formulaires en direct.

### C. Règles Relatives au JavaScript
1.  **Modularité** : Charger systématiquement le JS avec `type="module"` pour isoler le scope global.
2.  **Web APIs natives** : Exploiter les fonctionnalités modernes natives du navigateur (comme l'API Popover pour les menus déroulants et modals, ou `localStorage` pour les persistances légères) pour éviter les dépendances lourdes (jQuery, Bootstrap).
3.  **Gestion d'état explicite** : Structurer le code autour d'un objet d'état unique et de fonctions pures pour modifier le DOM afin de faciliter le diagnostic de bugs.

---

## 3. Checklist de Sûreté & Accessibilité (A11y)

Avant de déclarer une page HTML opérationnelle, l'agent ou le développeur doit s'assurer que :
- [ ] La structure respecte la hiérarchie des headings (`h1` -> `h2` -> `h3` -> aucun saut hiérarchique).
- [ ] Tous les contrastes de couleurs respectent les standards WCAG AA (utilisabilité sur fond sombre).
- [ ] Les éléments interactifs sont navigables au clavier (touches Tab, Entrée, Espace).
- [ ] Le code CSS est valide et ne contient aucune valeur hardcodée non centralisée dans `:root`.
- [ ] Aucune ressource ou script tiers non documenté ou non souverain (ex : trackers externes) n'est importé.

---
*Guide technique des bonnes pratiques HTML validé et indexé par Tesla.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
