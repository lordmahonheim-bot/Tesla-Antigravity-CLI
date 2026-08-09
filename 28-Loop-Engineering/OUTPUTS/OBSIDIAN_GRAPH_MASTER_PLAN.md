---
role: Documentation
status: canonical
title: Obsidian Graph Master Plan
version: 1.0
---

![Status](https://img.shields.io/badge/Status-ACTIVE-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red)

# PLAN DE MAÎTRISE DU GRAPH VIEW (AVALON)

**Objectif :** Transformer le Graph View d'Obsidian d'une simple visualisation esthétique ("Hairball") en un outil analytique et de navigation puissant, selon les doctrines MANUS, GenSpark et RENA.

---

## 1. LE FILTRAGE DU BRUIT (Anti-Hairball)

La première étape pour un graphe exploitable est d'exclure les éléments non sémantiques. Dans le coffre Avalon, le plugin Copilot a créé une "usurpation sémantique" en générant de faux nœuds de connaissances.

**Actions (Paramètres Natifs > Filtres) :**
- **Requête d'exclusion stricte** : `-path:"copilot" -path:"99-System/Templates"`
- **Orphelins (Orphans)** : Désactiver lors du travail quotidien. (À réactiver une fois par semaine pour le rituel de nettoyage).
- **Existing files only** : Activer (évite les fantômes).
- **Attachments** : Désactiver (allège drastiquement la charge CPU).

---

## 2. LA PHYSIQUE DU GRAPHE (Équilibre Dynamique)

Pour désengorger la sous-grappe `Index_Canonical` et donner de l'air aux nœuds, configurez les forces (Forces) comme suit :

- **Center force** : `0.30` (Diminue la gravité centrale pour étaler le graphe).
- **Repel force** : `15.00` (Force de Coulomb élevée pour séparer les clusters).
- **Link force** : `0.50` (Tension des liens moyenne).
- **Link distance** : `250` (Longueur des "ressorts" très longue pour aérer).

---

## 3. COLORATION SÉMANTIQUE (Groupes)

Créez ces groupes visuels dans l'ordre strict de priorité :

1. **Gouvernance (Rouge Vif)** : `tag:#canonical OR path:"memory"`
2. **Action / Projets (Orange)** : `path:"01-Projects"`
3. **Zettelkasten Permanent (Vert)** : `tag:#permanent`
4. **MOCs - Maps of Content (Bleu)** : `tag:#moc`
5. **Notes Ephémères (Gris)** : `tag:#fleeting`

---

## 4. CHANGEMENT DE PARADIGME : LE LOCAL GRAPH

**Le Global Graph est un outil de diagnostic (mensuel). Le Local Graph est l'outil de production (quotidien).**

- Ouvrez le `Local Graph` en permanence dans un volet latéral (Side-Pane).
- **Profondeur (Depth)** : `2`. (Affiche les voisins de vos voisins).
- Cela permet de garder le focus sur la topologie immédiate de la pensée en cours de rédaction, sans être noyé par le reste du coffre.

---

## 5. LA RÈGLE DES 2 LIENS ET LES MOCs

Pour briser la structure en étoile (hub-and-spoke) et tisser un vrai réseau :
- Chaque note *doit* pointer vers son index/MOC (ex: `[[Index_Canonical]]`).
- Chaque note *devrait* pointer de manière transversale vers au moins une note sœur (ex: `AGENTS.md` ➔ `ENGINE.md`).

---

## 6. L'ARSENAL TECHNOLOGIQUE (Plugins Recommandés)

Pour aller au-delà de l'esthétique native et entrer dans l'analytique :

- **Graph Analysis** : À installer pour mesurer la "Betweenness Centrality" et trouver les notes "Ponts" entre vos projets et la théorie.
- **Breadcrumbs** : Pour superposer une hiérarchie stricte (Parent/Enfant) sur la base de données plate, permettant un export structurel clair.
- **Bookmarks (Natif)** : Sauvegardez la configuration ci-dessus sous le nom `Graph — Vue Maître Avalon` (Ctrl+Shift+B).

---

*Livrable généré par l'Organe Cognitif Tesla.*
*Savoir assimilé : MANUS, GenSpark, RENA.*
