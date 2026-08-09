# Live Web Data: OpenCut & FreeCut

**Date de collecte :** 2026-07-19
**Source :** Opérations Internet (Recherche automatisée Webwright / Google / Reddit / GitHub)

---

## 1. OpenCut

### Présentation Générale
OpenCut est un éditeur vidéo open-source conçu comme une alternative axée sur la confidentialité à CapCut. Actuellement en cours de refonte majeure, il abandonne son architecture web initiale pour un cœur haute performance en **Rust**, multi-plateforme.

### Capacités d'Automatisation (Idéal pour TVD)
L'orientation récente du projet se concentre fortement sur les workflows développeurs et l'automatisation "headless" :
* **Mode Headless :** Conçu pour le rendu automatisé et les pipelines CI/CD, permettant de générer ou de traiter des vidéos sans interface graphique.
* **Editor API :** Interface programmatique permettant de contrôler les opérations de montage (ajout de clips, textes, découpe) via le code.
* **Intégration MCP (Model Context Protocol) :** Permet aux agents IA (comme Claude ou Tesla) de manipuler la timeline, les ressources et le moteur de rendu de manière programmatique.
* **Scripting natif :** Onglet dédié dans l'éditeur pour l'automatisation intra-application.

### Dépôts GitHub
* **Principal :** [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) - La nouvelle version réécrite incluant l'API et le serveur MCP.
* **Classique :** [OpenCut-app/opencut-classic](https://github.com/OpenCut-app/opencut-classic) - Version originelle maintenue pour la stabilité.
* **Communauté :** [JXUE0/opencut-controller](https://github.com/JXUE0/opencut-controller) (Serveur MCP pilotant le navigateur via Playwright).

### Retours Communautaires (Reddit)
* **Confidentialité :** Très apprécié (r/foss, r/opensource) pour son traitement local évitant l'upload sur le cloud (contrairement à CapCut).
* **Développement :** Considéré comme très prometteur, bien que certains utilisateurs signalent des instabilités liées à la jeunesse de la refonte en Rust.

---

## 2. FreeCut

### Présentation Générale
FreeCut (parfois discuté sous le nom de "WannaCut") est un éditeur vidéo open-source et **entièrement basé sur le navigateur**. Il ne nécessite aucune installation ni serveur distant : tout s'exécute côté client.

### Capacités Techniques
* **Technologies Web Modernes :** Utilise intensivement **WebGPU, WebCodecs et la File System Access API**.
* **Local-First :** Pas d'upload de fichiers, édition de vidéos multipistes directement depuis le disque dur local vers le navigateur.
* **Stack :** React, TypeScript, Rust, Tauri.

### Dépôts GitHub & Variantes
* **Éditeur Navigateur (Principal) :** Plusieurs itérations par des développeurs indépendants (ex: Walter Low). C'est le projet le plus en vue.
* **Scripts d'Automatisation :** Le nom "FreeCut" est aussi parfois utilisé par de petits dépôts proposant des scripts Python/FFmpeg de suppression automatique des silences (auto-cut).

### Retours Communautaires (Reddit)
* **Performance :** Impressionne la communauté développeur (r/reactjs, r/tauri) par sa capacité à repousser les limites des technologies web pour du montage lourd.
* **Usage :** Comparé à des éditeurs lourds (DaVinci, Kdenlive) comme une alternative "légère", idéale pour du montage rapide, sans friction d'installation.

---
**Conclusion Stratégique pour TVD (Tesla-Video-Director) :**
- **OpenCut** offre le pipeline d'intégration le plus puissant pour des agents IA grâce à son API Editor et son intégration MCP native. C'est le candidat idéal pour du montage piloté par IA (Headless).
- **FreeCut** représente le summum du montage "local-first" dans le navigateur, très pertinent pour des interfaces de révision manuelles immédiates.
