# SIA-TESLA : Conception Technique du Wrapper LSP et Intégration Loop Engineering

## 1. Objectif du Document
Ce document, produit par le Nœud N4 (`tesla-master-code`), établit la conception technique théorique du Wrapper LSP et son intégration au sein de la boucle *Loop Engineering* (ACT-VERIFY-LEARN-REPEAT). Il s'inscrit dans l'architecture SIA (Self-Improving AI) définie par N2. L'objectif est d'implémenter le "Self-Healing" et la boucle d'évolution sans sur-ingénierie.

## 2. Conception Théorique du Wrapper LSP

Le Wrapper LSP (Language Server Protocol) agit comme le composant "Fitness Function" dynamique pour le code généré par l'Agent Cible.

### 2.1. Rôles et Responsabilités
- **Interception :** Analyse statique systématique du code généré avant toute exécution ou commit (respect de la Règle 3 Anti-Hallucination & Self-Healing).
- **Normalisation :** Traduction des diagnostics complexes du serveur LSP (erreurs de syntaxe, typage, linting) en un format JSON déterministe standardisé.
- **Télémétrie :** Transmission des logs de diagnostic au composant d'Évaluation (Improvement Agent).

### 2.2. Architecture Interne du Wrapper
- **Interface d'Entrée :** Reçoit le code source généré (via l'édition de fichier dans le workspace).
- **Moteur (Core) :** Connecteur léger au LSP natif via l'outil `karellen-lsp-mcp` (actuellement disponible sur MIDGARD).
- **Interface de Sortie (Feedback Loop) :** 
  - Si `SUCCESS` : Renvoie un signal de validation à l'Orchestrateur.
  - Si `FAIL` : Fournit le contexte de l'erreur au format structuré pour déclencher le cycle de Self-Healing.

## 3. Intégration au Loop Engineering (ACT-VERIFY-LEARN-REPEAT)

L'intégration au `tesla-loop-orchestrator` s'articule autour des quatre phases canoniques.

### 3.1. Phase ACT (Exécution)
L'Agent Cible (`tesla-master-code`) produit une implémentation ou une modification du code source.

### 3.2. Phase VERIFY (Évaluation par le Wrapper LSP)
Le Wrapper LSP analyse la production.
- **Boucle de Self-Healing (Courte) :** Si des erreurs sont détectées, le Wrapper les renvoie directement à l'Agent Cible pour correction immédiate (budget d'essais défini, ex: 3 retries).
- **Escalade :** Si l'Agent Cible échoue à corriger après l'épuisement du budget, la boucle courte est interrompue. Le log complet de la trajectoire (tentatives + erreurs LSP persistantes) est transmis à l'Agent Évaluateur.

### 3.3. Phase LEARN (Amélioration du Harness)
Intervention de l'Agent Évaluateur et du Meta-Agent.
- **Diagnostic :** L'Évaluateur identifie pourquoi l'Agent Cible a échoué (ex: mauvaise compréhension de l'API, syntaxe dépréciée).
- **Patching (Meta-Agent) :** Le Meta-Agent génère une "leçon" structurelle. Plutôt que de corriger le code cible, il modifie le *Harness* opérationnel (ex: ajout d'une consigne anti-répétition dans le `SKILL.md` ou mise à jour de la base de données de connaissances vectorielles).

### 3.4. Phase REPEAT (Validation & Persistance)
- **Oversight Gate :** Le patch du Harness est soumis en tant que "Pull Request Locale" ou artefact pour validation humaine ou arbitrage par un "Gatekeeper" strict (ex: `tesla-code-auditor`).
- **Application :** Une fois validé, le patch modifie le contexte persistant (Reflective Prompt Evolution), immunisant les futures exécutions de l'Agent contre cette classe d'erreur.

## 4. Audit de Faisabilité (État de l'art Local)

### 4.1. Forces (Ce qui est réalisable immédiatement)
- Le tooling `karellen-lsp-mcp` offre déjà l'infrastructure nécessaire pour extraire les erreurs déterministes.
- Le Self-Healing (Boucle Courte) est trivial à orchestrer en incrémentant un compteur de tentatives dans l'agent de contrôle.
- Les documents de type `SKILL.md` (Skills) sont des cibles idéales pour graver les optimisations de prompts.

### 4.2. Contraintes et Points de Vigilance
- **Parsing des Logs :** Convertir l'erreur brute en cause racine sémantique demande un prompt d'Évaluation précis pour ne pas dériver.
- **Surcharge Contextuelle :** Ajouter trop de règles dans le *Harness* (`SKILL.md`) risque de diluer l'attention de l'Agent Cible. Un mécanisme de compression et d'archivage des leçons (Garbage Collection sémantique) sera nécessaire à moyen terme.
- **Sécurité (Oversight) :** La modification automatique de `SKILL.md` par le Meta-Agent est à haut risque de divergence. L'humain doit impérativement rester dans la boucle de validation finale.

## 5. Conclusion
L'architecture SIA proposée est mature et en parfait alignement avec le Vigilum Codex. Elle valorise le Low-Code, se repose sur des outils déterministes existants et construit une résilience systémique tout en sécurisant la prise de décision par l'interposition systématique de la validation humaine avant toute persistance définitive.
