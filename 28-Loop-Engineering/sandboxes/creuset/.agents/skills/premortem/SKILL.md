---
name: premortem
description: Skill de diagnostic prédictif d'échec (Premortem) pour stress-tester des plans de projet et des architectures techniques complexes selon la méthode de Gary Klein et Daniel Kahneman.
---

# SKILL : DIAGNOSTIC PREMORTEM (AVOCAT DU DIABLE)

Ce Skill implémente la méthode du **Premortem** (prospective hindsight), théorisée par le psychologue cognitif Gary Klein et recommandée par Daniel Kahneman, pour stress-tester les plans de projet et choix techniques de l'écosystème Bifrost/Tesla avant leur exécution.

---

## 1. Fondations Théoriques & Méthodologiques

* **Gary Klein (2007, Harvard Business Review)** : Le premortem consiste à se projeter mentalement dans le futur (ex: 6 mois après le lancement) et à postuler que le projet a **complètement et misérablement échoué**. À partir de ce fait acquis, l'équipe travaille à rebours pour identifier les causes de la catastrophe.
* **Daniel Kahneman (Biais de planification)** : Cette méthode est le remède le plus puissant contre l'illusion de validité et le biais d'optimisme. Elle libère la parole et légitime la recherche de failles en transformant la critique en un exercice narratif créatif.

---

## 2. Directives Système d'Analyse (Multi-Agents Éphémères)

Lorsqu'il est activé, l'agent Tesla ou le sous-agent `premortem-analyst` simule trois rôles distincts pour passer le plan au crible :

```
             [ PLAN / OBJECTIF INITIAL ]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  Postulat de l'Échec Absolu (T+) │
        └────────────────┬─────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │ Agent 1   │   │ Agent 2   │   │ Agent 3   │
   │ L'Avocat  │   │ L'Inspect-│   │ La Vigie  │
   │ du Diable │   │ eur Angles│   │ Signaux   │
   │ (Causes)  │   │  Morts    │   │ Faibles   │
   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ Rapport & Contre-Mesures (FTS5)  │
        └──────────────────────────────────┘
```

### A. Agent 1 : L'Avocat du Diable (Les Causes Root-Cause)
* **Mission** : Expliquer *comment* et *pourquoi* le désastre est arrivé.
* **Focus** : Les faiblesses techniques intrinsèques (ex: instabilité d'une bibliothèque, dépendances non vérifiées), les contraintes opérationnelles locales (MIDGARD), et les conflits logiques.

### B. Agent 2 : L'Inspecteur des Angles Morts (Les Hypothèses Invisibles)
* **Mission** : Exposer les suppositions non testées (les "assumptions") sur lesquelles repose le plan.
* **Focus** : Identifier les angles morts (ex: supposer que le démon LSP est toujours en ligne, supposer qu'un fichier Markdown ne dépassera jamais 10 000 lignes, etc.).

### C. Agent 3 : La Vigie des Signaux Faibles (Les Indicateurs Précurseurs)
* **Mission** : Lister les micro-événements, alertes silencieuses ou métriques dégradées qui annoncent la dérive dès le début de l'exécution.
* **Focus** : Temps de latence accrus, erreurs de parsing silencieuses, avertissements de compilation ignorés.

---

## 3. Protocole d'Invocation & Duplication Éphémère

Tesla doit instancier la capacité de diagnostic uniquement sur demande ou avant d'exécuter un `/goal` d'ingénierie lourd.

### Directive d'Initialisation du Sous-Agent `premortem-analyst` :
Le sous-agent est défini de façon éphémère (durée de la session) avec les paramètres suivants :
* **TypeName** : `self` ou type dédié configuré avec les instructions de l'Avocat du Diable.
* **Role** : `Premortem Risk Analyst`
* **Prompt d'initialisation** :
  ```markdown
  Tu es le sous-agent 'premortem-analyst', un expert en ingénierie de la résilience et en analyse prédictive d'échec sur la machine MIDGARD.
  Ton unique mission est d'étudier le plan technique fourni par Tesla, de postuler son échec total dans 3 mois, et de rédiger un audit d'échec sans complaisance en adoptant les rôles de l'Avocat du Diable, de l'Inspecteur des Angles Morts et de la Vigie des Signaux Faibles.
  Tu dois impérativement utiliser le template de rapport situé dans `.agents/skills/premortem/templates/premortem_report.md` et exporter ton analyse finale dans `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/`.
  ```

---

## 4. Protocole de Livraison & Gouvernance

À la fin de l'analyse, le rapport doit être écrit dans Obsidian Avalon sous la forme suivante :
* **Chemin** : `/home/lord-mahonheim/bifrost/tesla/OUTPUTS/premortem_[nom_du_plan].md`
* **En-tête YAML Standard** (obligatoire pour l'indexation par le second cerveau) :
  ```yaml
  ---
  type: reference
  tags: [securite/premortem, statut/valide]
  source: "[[Nom_Du_Plan_Original]]"
  date: AAAA-MM-JJ
  version: 1.0
  ---
  ```
