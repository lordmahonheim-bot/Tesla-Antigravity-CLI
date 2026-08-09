# Plan d'Intervention Optimal : SIA-TESLA (Self-Improving AI)
**Statut :** Version Opérationnelle et Définitive
**Auteur :** Tesla (Agent Principal / Orchestrateur)
**Fondation :** Vigilum Codex & Architecture Gateway V2.1

---

## 1. Diagnostic Exécutif et Synthèse de l'Architecture
Suite à l'exécution complète du DAG (Nœuds N1 à N5), l'architecture **SIA-TESLA** est validée. Elle repose sur l'état de l'art 2026 : l'amélioration continue ne se fait **pas** par la modification des poids des modèles (weights), mais par l'optimisation itérative du **Harness** (prompts, mémoire, orchestration, outils).

### Le Paradigme à 3 Piliers
1. **L'Agent Cible (Exécuteur) :** Exécute le code et génère des traces/logs LSP.
2. **L'Agent Évaluateur (Fitness Function) :** Analyse les erreurs répétées et les goulots d'étranglement.
3. **Le Méta-Agent (Optimiseur) :** Conçoit des patchs pour modifier le comportement (ex: mise à jour du `SKILL.md`) et éviter la récidive.

---

## 2. Corrections et Durcissement (Garde-Fous Premortem)
L'audit N5 (`premortem`) a révélé des failles critiques (Semantic Bloat et Token Drain). Ce plan d'intervention corrige formellement l'architecture initiale en y intégrant les mitigations absolues suivantes :

### 2.1. Bouclier Anti-Semantic Bloat (RPN 60)
**Problème :** L'ajout continu de règles dans `SKILL.md` provoque une surcharge cognitive (Instruction Neglect).
**Solution Opérationnelle :** Implémentation d'un **Semantic Garbage Collector**.
- Le Méta-Agent a **l'interdiction absolue** d'ajouter purement et simplement une nouvelle règle à la fin d'un `SKILL.md`.
- Il doit obligatoirement **refactoriser et condenser** le document entier pour y intégrer la nouvelle leçon tout en respectant une limite stricte de tokens (ex: max 150 lignes par `SKILL.md`).

### 2.2. Sandboxing Obligatoire (RPN 48)
**Problème :** Un patch "halluciné" du Méta-Agent peut détruire les compétences de l'Agent Cible.
**Solution Opérationnelle :** Validation Empirique avant l'Oversight Gate.
- Aucun patch de Harness ne sera présenté à Lord Mahonheim ou au `tesla-code-auditor` sans avoir réussi un cycle de Test-Driven Development (TDD) dans un environnement de bac à sable local (Creuset).

### 2.3. Circuit Breaker Global (RPN 30)
**Problème :** Boucle infinie de "Self-Healing" via le LSP causant une hémorragie financière (Token-Economy Drain).
**Solution Opérationnelle :** Double verrou de résilience.
- Verrou local (déjà existant) : `max_retries: 3` dans les frontmatters.
- Verrou global : Imposition d'un "Token Budget Cap" au niveau de `tesla-loop-orchestrator` qui déclenche un **Hard Kill** si la consommation dépasse un seuil par tâche, remettant la main à l'opérateur humain.

---

## 3. Plan d'Intervention Opérationnel (Phasage Low-Code)
L'implémentation respectera la doctrine de Mahonheim : pragmatisme, pas de réinvention de la roue, utilisation des outils existants (`karellen-lsp-mcp`, `Tree-sitter`).

### Phase 1 : Câblage de la Télémétrie et du Self-Healing Court
- **Action :** Intégrer formellement `karellen-lsp-mcp` comme arbitre déterministe de la boucle ACT-VERIFY.
- **Livrable :** Script ou routine standardisée permettant à `tesla-master-code` d'intercepter les erreurs LSP formatées en JSON et de s'auto-corriger (max 3 itérations).

### Phase 2 : Déploiement de la Boucle d'Apprentissage (Long Loop)
- **Action :** Définir un protocole où l'échec de la Phase 1 déclenche l'appel au couple Évaluateur/Méta-Agent.
- **Livrable :** Mise à jour du `SKILL.md` de `tesla-loop-orchestrator` pour inclure la phase **LEARN** (Génération d'un patch de Harness au format *Pull Request Locale* ou *Artefact Broker*).

### Phase 3 : Déploiement du Semantic Garbage Collector
- **Action :** Créer une routine d'optimisation de `SKILL.md` (via LLM) qui condense les leçons apprises.
- **Livrable :** Ajout de la contrainte de refactorisation dans la charte de rédaction des Méta-Agents. L'Auditeur (`tesla-code-auditor`) rejettera tout `SKILL.md` dépassant la taille maximale autorisée.

---

## 4. Conclusion
Ce plan d'intervention ferme toutes les vulnérabilités identifiées. Le paradigme SIA-TESLA est prêt à être implémenté de manière incrémentale. L'auto-amélioration au sein de MIDGARD sera stricte, économique, pragmatique et **totalement sous le contrôle de l'Oversight Gate de Lord Mahonheim**.
