# Arcanis Architecture Brief: MVP 16 & MVP 44

## Loop Engineering Architecture
L'architecture de la boucle d'ingénierie repose sur le duo MVP 16 et MVP 44, qui fonctionnent en synergie selon un paradigme **Actor-Gatekeeper**.

### MVP 16: Tesla-Master-Code (The Actor)
- **Rôle** : Création de code, implémentation des fonctionnalités dans un environnement isolé.
- **Responsabilités** : 
  - Produire le code initial.
  - Appliquer les auto-corrections basées sur les retours stricts du validateur (MVP 44).

### MVP 44: Tesla-Code-Auditor (The Gatekeeper/Validator)
- **Rôle** : Validation rigoureuse, linting, tests de sécurité.
- **Responsabilités** :
  - Auditer le code produit par MVP 16.
  - Rejeter le code non conforme (boucle Pyright/Smoke-tests).
  - Fournir des logs de feedback et des directives de correction claires à MVP 16.

## Interfaces & Dépendances
- **Interface de Communication** : Les deux agents communiquent via un échange asynchrone dans le SGC. MVP 16 pousse le code, MVP 44 retourne un `Feedback_Report`.
- **Dépendances** : 
  - **MVP 44** dépend de la production de code par **MVP 16**. 
  - **MVP 16** dépend du signal `Validation_Success` de **MVP 44** pour considérer sa tâche comme achevée (Loop Exit).
