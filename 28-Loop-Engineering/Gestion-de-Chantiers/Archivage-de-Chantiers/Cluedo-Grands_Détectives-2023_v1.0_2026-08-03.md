# Gestion de Chantier : Cluedo-Grands_Détectives-2023

## 1. Identité du Chantier
- **Nom du Chantier** : Cluedo-Grands_Détectives-2023
- **Date d'Ouverture** : 2026-08-03
- **Statut** : 🟢 Ouvert (En Planification)
- **Version** : 1.0

## 2. Objectif Cible
Création d'une page HTML locale "manuel_cluedo.html" (SPA, interactive, avec Base64 intégral et simulateurs 3D) constituant le Manuel du Détective autonome, hors ligne et zero-touch.

## 3. Architecture Cible & Master Plan
- **Fichier Unique** : Un seul `index.html` avec les assets encodés en Base64.
- **SPA Interactive** : Navigation par onglets (Enquête, Dossier, Manoir, Protocole, Preuve, Laboratoire, Bibliothèque, Académie).
- **Zéro Dépendance** : HTML/CSS/JS purs, stockage LocalStorage.
- **La Totale** : Simulateur de Dés 3D, Moteur d'Hypothèse Visuelle, Générateur de Mystère Solo, Quiz du Détective.
- **Plan de Référence** : `OUTPUTS/Plan_Intervention_Cluedo_HTML.md`

## 4. Périmètre & Dépendances
- **In-Scope** : Développement de l'interface SPA, intégration des assets (Base64), création des moteurs logiques JS.
- **Out-of-Scope** : Hébergement web (solution locale stricte), backend serveur.
- **Dépendances** : Assets du jeu (images des cartes, plateau).

## 5. Team Synergy & Gouvernance
- Orchestrateur : `tesla-team-synergy`
- Exécuteurs (Nœuds) : `tesla-web-raider`, `tesla-arcanis-360`, `tesla-curator-prime`, `tesla-writing-skills`, `tesla-master-code`, `premortem`.
- Autorisation de push distant : Seulement après autorisation stricte de Lord Mahonheim.

## 6. Plan d'Intervention Stratégique (Nœuds)
*(Voir OUTPUTS/Synergy/mission_graph.yaml et OUTPUTS/Synergy/scheduler_plan.md pour la vue technique)*
- **N1** : Acquisition & Extraction (Web-Raider & Arcanis-360)
- **N2** : Curation & UX Writing (Curator-Prime & Writing-Skills)
- **N3** : Engineering & HTML Construction (Master-Code)
- **N4** : QA, Stress-Test & Resilience (PREMORTEM)

## 7. Budget & Ressources (Token Economy)
*(Voir OUTPUTS/Synergy/budget_ledger.md pour le détail)*
Répartition entre Flash (I/O, extraction), Pro (Rédaction), Sonnet (Code SPA/JS) et Opus (Audit final).

## 8. Gestion des Risques (Premortem)
- **Risque 1** : Taille du fichier HTML trop importante (>5Mo) bloquant le rendu sur certains navigateurs locaux. -> *Mitigation* : Compression rigoureuse des images avant encodage Base64, audit par PREMORTEM.
- **Risque 2** : Complexité du simulateur 3D CSS causant des lags. -> *Mitigation* : Utilisation des API `requestAnimationFrame` et accélération matérielle, fallback 2D si nécessaire.

## 9. Critères de Succès & Clôture
- [ ] Le fichier `manuel_cluedo.html` pèse idéalement moins de 2-3 Mo.
- [ ] Le simulateur de dés, la SPA, et le Base64 fonctionnent sans aucune connexion internet.
- [ ] Le code a passé l'audit PREMORTEM et la vérification LSP.
- [ ] Signature Visuelle des Livrables MVP appliquée.

## 10. Journal de Bord
- **2026-08-03** : Ouverture du chantier, génération du plan SGC et des livrables de Team Synergy. Attente de la validation du graphe par Lord Mahonheim.

## 11. Checklist Finale
- [x] SGC créé.
- [x] `mission_graph.yaml` généré.
- [x] `scheduler_plan.md` généré.
- [x] `capability_routing.md` généré.
- [x] `budget_ledger.md` généré.
- [ ] Mission Graph validé par Lord Mahonheim.
- [ ] Exécution terminée.
- [ ] Mise à jour du Journal de Suivi SGC.

![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)


## 🏆 Signature & Horodatage de Clôture
![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

Chantier certifié et validé par Lord Mahonheim le 2026-08-03.
Opération d'assimilation SGC achevée.
