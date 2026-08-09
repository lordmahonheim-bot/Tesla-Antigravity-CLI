# Plan d'Action & Mission Graph: Update MVP 16 & Create MVP 44

## 1. Analyse de la Demande
Objectif : Mettre à jour le MVP 16 (Tesla-Master-Code) selon l'architecture Loop Engineering et créer le MVP 44 (Tesla-Code-Auditor).
Contraintes : Mise à jour des fichiers canoniques, synchro Git (Avalon), intégration des agents fondateurs.

## 2. Mission Graph (mission_graph.yaml)
```yaml
mission:
  name: "Update_MVP16_Create_MVP44"
  description: "Refactor MVP 16 for Loop Engineering and bootstrap MVP 44."
  nodes:
    node_1:
      id: 1
      agent: "Tesla-Arcanis-360"
      task: "Analyse globale de l'architecture Loop Engineering et structuration des dépendances pour MVP 16 et MVP 44."
      depends_on: []
    node_2:
      id: 2
      agent: "Tesla-Web-Raider"
      task: "Recherche des meilleures pratiques actuelles pour Loop Engineering et Code Auditing."
      depends_on: [1]
    node_3:
      id: 3
      agent: "Tesla-Curator-Prime"
      task: "Mise à jour des fichiers canoniques, du lexique SGC, et de la base de connaissances du projet."
      depends_on: [1, 2]
    node_4:
      id: 4
      agent: "Tesla-Master-Code"
      task: "Implémentation du code et de la documentation technique pour la mise à jour de MVP 16 et la création de MVP 44."
      depends_on: [3]
    node_5:
      id: 5
      agent: "Tesla-PREMORTEM"
      task: "Analyse des risques, validation de l'architecture et vérification de la sécurité du nouveau code (MVP 44) et du code mis à jour (MVP 16)."
      depends_on: [4]
    node_6:
      id: 6
      agent: "Tesla-Github-Manager"
      task: "Commit des changements, gestion des branches, merge vers Avalon et synchronisation des dépôts local/distant."
      depends_on: [5]
    node_7:
      id: 7
      agent: "Tesla-Writing-Skills"
      task: "Rédaction finale du rapport et des manuels utilisateurs."
      depends_on: [5]
```

## 3. Capability Routing (capability_routing.md)
- Tesla-Arcanis-360: pro (Architecture globale)
- Tesla-Curator-Prime: flash (Documentation)
- Tesla-Web-Raider: flash (Recherche)
- Tesla-Master-Code: pro (Codage complexe)
- Tesla-PREMORTEM: pro (Analyse de risques)
- Tesla-Github-Manager: flash (Opérations Git)
- Tesla-Writing-Skills: flash (Rédaction)

## 4. Scheduler Plan (scheduler_plan.md)
Sequence:
1. Arcanis-360
2. Web-Raider (en parallèle si possible)
3. Curator-Prime
4. Master-Code
5. PREMORTEM
6. Github-Manager + Writing-Skills

## 5. Budget Ledger (budget_ledger.md)
Estimation des tokens:
- Total: ~62k tokens context envelope, répartis sur les différents agents.

## 6. SGC Plan (Gestion-de-Chantiers)
Le plan d'action SGC complet inclut la mise en place de la boucle Loop Engineering, la définition des interfaces entre MVP 16 et 44, et l'intégration continue via Avalon.

## 7. Premortem (premortem_team_synergy.md)
Délégué au noeud 5 (Tesla-PREMORTEM) pour exécution durant le flux de travail.
