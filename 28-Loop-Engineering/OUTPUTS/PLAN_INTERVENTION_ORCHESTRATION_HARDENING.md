# 🛡️ PLAN D'INTERVENTION & SOLUTION DÉFINITIVE : VIGILUM GATEWAY V2.1

**Objet :** Résolution définitive des crashs d'orchestration en mode `/goal` 
**Fondation :** Synthèse comparative des approches Apodex, ChatGPT, RENA et Tesla V2
**Doctrine :** Low-Code, Optimisation de l'existant, Séparation des Responsabilités (Vigilum Codex)

---

## 1. Philosophie du Design Cible

La solution retenue est la **Vigilum Gateway V2**, servant de colonne vertébrale opérationnelle. Elle est enrichie des mécanismes techniques de **RENA** (PIC, TRPB, GSP) et s'ancre dans la configuration et la politique autonome d'**Apodex**. L'horizon conceptuel de l'Execution Broker (**ChatGPT**) est conservé comme guide de conception (Artefacts) sans imposer de refonte logicielle lourde.

**L'objectif :** Obtenir des sessions `/goal` réellement autonomes, sans blocages sandbox, sans faux timeouts et sans exiger d'Emergency Overrides de la part de l'Agent Principal.

---

## 2. Le Tronc Commun d'Orchestration (Les 4 Piliers)

1. **Interdiction d'ask_permission & Pré-autorisation (Mode /goal)**  
   Les espaces de travail (tels que `/MVP-GITHUB/` et `/OUTPUTS/`) doivent être formellement déclarés comme autorisés. Le recours à `ask_permission` est proscrit en mode autonome.
2. **Le Broker par Artefacts (Délégation d'Exécution)**  
   Les sous-agents deviennent des entités de "Calcul + Génération d'Artefacts". Si une action excède leurs droits, ils ne crashent pas mais produisent une "Requête d'Exécution" (Artefact) que l'Orchestrateur (Tesla) validera et appliquera.
3. **Pre-Flight Tool Verification (Tool Registry Pre-Binding - TRPB)**  
   Avant toute invocation, Tesla lit le manifest des dépendances (le `SKILL.md`) du sous-agent. Si un outil critique manque, l'invocation est annulée, évitant ainsi les boucles infinies de *Self-Healing*.
4. **Graceful Shutdown Protocol (GSP) & Checkpoints**  
   Le timeout rigide est remplacé par un *Two-Phase Kill*. Un `[CHECKPOINT CONTRACT]` oblige le sous-agent à signaler son état. Une *Grace Period* de 15 secondes permet de collecter les succès sur le fil.

---

## 3. Plan d'Action Concret & Opérationnel

Ce plan séquence les actions exactes à réaliser pour déployer la Vigilum Gateway V2.1.

### Phase 1 : Mise à jour de la Gouvernance Fondatrice
*(Alignement des textes sacrés de Tesla)*

- **Mise à jour de `AGENTS.md` :**
  - **Ajout de la RÈGLE N°4.1 :** Interdiction stricte d'`ask_permission` en `/goal` et obligation pour l'Orchestrateur de jouer la Pre-Flight Checklist (Permission Inheritance Chain - PIC).
  - **Ajout de la RÈGLE N°7.1 :** Implémentation du *Graceful Shutdown Protocol* (Grace Period de 15 secondes pour réception de checkpoint).
  - **Ajout de la RÈGLE N°7.2 :** Délégation d'exécution par Artefact (Broker Pattern) pour les opérations hors-périmètre.
- **Mise à jour de `FORCE_TOOLING.md` :**
  - Ajout des contraintes de capacités : `tool_dependencies`, mode de permission requis, et Circuit Breaker de retry.
- **Nouveau Standard `SKILL.md` :**
  - Refonte du template pour exiger les blocs YAML `tool_dependencies` et `permission_context`.

### Phase 2 : Configuration du Système & Mode /goal
*(L'approche Low-Code par Apodex)*

- **Sécurisation du Workspace Antigravity :**
  - Vérifier que les chemins `/home/lord-mahonheim/bifrost/tesla/`, `/MVP-GITHUB/`, et `/OUTPUTS/` sont explicitement déclarés en politique `Allow` par défaut.
- **Création du Fichier de Politique Autonome :**
  - Rédiger `AUTONOMOUS_EXECUTION_POLICY.md` détaillant le profil `/goal` (limites, exceptions absolues comme `git push` sans validation humaine, etc.).

### Phase 3 : Déploiement des Mécanismes d'Exécution
*(L'intégration du Broker et des mécaniques RENA)*

- **Standardisation de l'Artefact d'Exécution :**
  - Définir le format YAML/JSON que les sous-agents devront utiliser pour soumettre leurs `execution_requests` dans `OUTPUTS/`.
- **Enrichissement Progressif des Skills (TRPB) :**
  - Mettre à jour les `SKILL.md` existants (notamment `tesla-github-manager`, `tesla-master-code`, `tesla-arcanis-360`) pour inclure leurs dépendances d'outils.
- **Mise en place de la Logique Timeout de l'Orchestrateur :**
  - Intégrer la logique de *Two-Phase Kill* mental dans le pipeline de l'Agent Principal lorsqu'il orchestre des sous-agents.
- **Horizon Exploratoire :**
  - Poser les bases d'une table `subagent_health` dans la mémoire SQLite pour évaluer la résilience à long terme.

---

**Statut du Document :** Plan finalisé. En attente du "GO" de Lord Mahonheim pour exécuter la Phase 1 (Mise à jour de la Gouvernance).
