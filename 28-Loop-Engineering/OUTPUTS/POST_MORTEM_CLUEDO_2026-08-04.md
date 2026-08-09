# 🛡️ POST-MORTEM & AUDIT : Chantier Cluedo-Grands_Détectives-2023

![Status](https://img.shields.io/badge/Status-POST%20MORTEM-yellow) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red)

**Date d'Audit :** 2026-08-04  
**Auditeur :** Tesla (Operational Governance Layer)  
**Cible :** Chantier 48 (Manuel Interactif Cluedo MVP)

---

## 1. Contexte de l'Audit (Directive `/Goal`)
Conformément à la gouvernance d'excellence du *Vigilum Codex* et à l'exécution du cycle *ACT-VERIFY-LEARN*, ce document dresse l'inventaire exhaustif et sans concession de toutes les failles, erreurs d'architecture, et bugs rencontrés durant le développement et le déploiement du MVP Cluedo. 

Pour chaque anomalie, la cause racine a été isolée et une solution systémique a été déployée.

---

## 2. Inventaire des Frictions Architecturales (UI/CSS/Logique)

### 2.1. Effondrement Gravitationnel 3D (Cartes Suspects)
- **Symptôme :** Lors du survol ou clic, les cartes des suspects tournaient sur elles-mêmes mais "glissaient" vers le bas, sortant de leur conteneur.
- **Cause Racine :** Rupture de la physique spatiale CSS. Les faces `.front` et `.back` n'étaient pas verrouillées dans le même espace dimensionnel (absence de `position: absolute` stricte et de limites 100%).
- **Solution Déployée :** Application stricte de `position: absolute; top: 0; left: 0; width: 100%; height: 100%;` sur les deux faces. Maintien du `transform-style: preserve-3d` sur le parent pour verrouiller l'axe Y. **Stabilité parfaite obtenue.**

### 2.2. Fracture de la Matrice d'Impression (A4 Print)
- **Symptôme :** L'export PDF des "Carnets de Détective" via navigateur (Ctrl+P) était esthétiquement détruit (coupures en plein milieu des carnets, marges aléatoires, perte des arrière-plans).
- **Cause Racine :** Le moteur de rendu d'impression des navigateurs ignore le CSS web par défaut. Absence de directives `@media print`.
- **Solution Déployée :** Création d'une "Print Matrix" isolée. Forçage de `@page { size: A4; margin: 0; }`. Utilisation de `page-break-inside: avoid` pour empêcher la scission des blocs. Activation forcée des couleurs via `-webkit-print-color-adjust: exact`. **Résultat : Exactement 2 carnets millimétrés par page A4.**

### 2.3. Résidus de Code Brut dans la Modale (Passages Secrets)
- **Symptôme :** Des balises HTML (ex: `<br>`, `<strong>`) ou des bruits de code s'affichaient sous forme de texte brut dans la description des pièces d'angle.
- **Cause Racine :** Le script JavaScript injectait le contenu via la propriété `.textContent`, qui neutralise et affiche les balises littéralement, au lieu de `.innerHTML`.
- **Solution Déployée :** Refactoring de la logique d'injection JS pour utiliser `.innerHTML` et sanitisation des blocs de description, permettant un rendu esthétique et coloré du texte des passages secrets.

---

## 3. Inventaire des Fractures Sémantiques (Lore & Règles)

### 3.1. Hérésie Topographique (Tunnels Secrets)
- **Symptôme :** La matrice HTML indiquait que le passage secret de la Cuisine menait au Salon.
- **Cause Racine :** Hallucination basée sur de vagues souvenirs ou des versions altérées du jeu.
- **Solution Déployée :** Délégation au sous-agent de lire le manuel PDF originel. Rectification chirurgicale des axes : Cuisine ↔ Bureau et Salon ↔ Jardin d'Hiver.

### 3.2. Obsolescence des Règles de Jeu (Premier Joueur)
- **Symptôme :** Le manuel interactif stipulait que "Mademoiselle Rose commence toujours".
- **Cause Racine :** Vestige des éditions rétro de Cluedo.
- **Solution Déployée :** Alignement sur le manuel Hasbro 2023 (F6420). Purge de la mention et remplacement par "Le premier joueur est désigné au hasard via le lancer d'un dé à 6 faces". Intégration de la mécanique de la "Loupe Rouge".

---

## 4. Inventaire des Frictions de Déploiement (GitHub & Réseau)

### 4.1. Lien Cassé par l'Encodage Unicode (NFD vs NFC)
- **Symptôme :** Le lien du PDF généré renvoyait une erreur 404 sur GitHub.
- **Cause Racine :** L'export PDF local contenait le caractère `é` encodé en NFD (accent combiné Mac/Linux) et des espaces (`Cluedo - Manuel Intéractif.pdf`). GitHub exige une normalisation stricte pour la résolution des URL web.
- **Solution Déployée :** Renommage forcé de l'asset en standard Web-Safe (`Cluedo-Manuel-Interactif.pdf`) via l'agent `tesla-github-manager` et validation par double-commit.

### 4.2. Quiproquo d'Asset et Limite de Rendu Natif GitHub (PDF.js)
- **Symptôme :** L'utilisateur souhaitait consulter les règles complètes (23 Mo) directement sur GitHub, mais le rendu web natif ne se déclenchait pas.
- **Cause Racine :** GitHub possède une limite stricte de 100 Mo pour le rendu, mais son moteur (PDF.js) échoue silencieusement ou time-out sur des fichiers vectoriels complexes ou lourds (comme le scan HQ de 23 Mo).
- **Solution Déployée :** L'utilisateur a généré une version compressée ("resized") du manuel. L'agent `tesla-github-manager` a exécuté l'écrasement de l'ancien fichier lourd par la version allégée, forçant la réussite du moteur de prévisualisation GitHub.

---

## 5. Faille de Gouvernance Systémique (L'Erreur de Tesla)

### 5.1. Extrapolation Taxonomique (Troncature)
- **Symptôme :** Le chantier Cluedo a failli écraser le chantier 46 (Tesla-Eye) et effacer le 47 (Deluge) de la base de registre `liste_projets_antigravity_BASE.md`.
- **Cause Racine :** L'outil de lecture a tronqué la fin du fichier. Au lieu d'utiliser `ContentOffset` ou `tail`, l'Agent a deviné l'identifiant, violant la doctrine d'Anti-Extrapolation (Règle 15) et corrompant temporairement le Journal de Suivi (Règle 21).
- **Solution Déployée :** Détection humaine, auto-correction immédiate de l'arbre taxonomique (Cluedo placé en Position 48). **Ordre `/Learn` assimilé : interdiction formelle de supposer la fin d'un registre sans une lecture déterministe (via `tail`).**

---
*Fin du rapport. Ces leçons sont désormais gravées dans la mémoire d'Antigravity CLI pour prévenir toute récidive.*
