# PLAN D'INTERVENTION ULTIME : OPRO-GRAD v3.0 (AIP-5)
**Statut :** Plan d'Ingénierie Définitif (Fusion Tesla + GenSpark + RENA)
**Auteur :** Tesla (Orchestrateur Suprême)
**Objectif :** Atteindre l'Autonomie d'Ingénierie Permanente de Niveau 5 (AIP-5) sous contrôle total (Vigilum Codex).

---

## 1. VISION ÉPISTÉMOLOGIQUE : LE MOTEUR À 3 ÉTAGES
L'audit de GenSpark a souligné une vérité fondamentale : TextGrad et OPRO ne sont pas séquentiels, ils sont complémentaires. 
*   **TextGrad (Sonde Locale) :** Génère un "Gradient Textuel", une critique chirurgicale d'une étape de raisonnement défaillante.
*   **OPRO (Agrégateur Global) :** Utilise l'historique global (Trajectoires + *Rejected-Edit Buffer*) pour proposer des mutations génétiques de prompts.
*   **DSPy (Compilateur Arena) :** Offre l'arène mathématique pour tester ces mutations sans jamais toucher au code canonique en aveugle.

---

## 2. LA SÉCURITÉ AVANT TOUT : LE KILL-SWITCH (Circuit-Breaker)
Avant même de coder l'optimiseur, la faille du drain de tokens infini doit être scellée. Aucun agent ne peut modifier son propre régulateur (Nouvelle **Règle 15**).
Le système OPRO-Grad est bridé par un Kill-Switch à 3 niveaux :
1.  **Rate Limit Local :** Maximum 5 déclenchements OPRO par heure.
2.  **Budget Global (Token Breaker) :** Hard-cap à 500 000 tokens journaliers dédiés à l'auto-évolution.
3.  **Kill-Switch Physique :** La présence du fichier `/etc/tesla/HALT_OPRO` coupe instantanément le démon systemd.

---

## 3. LE WORKFLOW D'AUTO-ÉVOLUTION (LES 5 STADES)

### Stade 0 : Détection (Étendue)
Déclenchements sur erreur franche (LSP, Exit > 0, Gate) **OU** sur dérive silencieuse des KPIs (ex: Fitness moyen en baisse de 15% sur 20 itérations).

### Stade 1 : Capture Sémantique (TextGrad RCA)
`tesla-premortem` génère un `textual_gradient.json` pointant l'erreur (ex: *"Ligne 42 : Omission de la gestion du context bloat"*).

### Stade 2 : L'Optimiseur OPRO (`tesla-opro-optimizer`)
Fin de la confusion entre liberté et taille :
*   **Learning Rate Textuel :** Degré de liberté de mutation (faible = typo, fort = refonte).
*   **Token Budget :** Contrainte dure (L1) de compression (Anti-Bloat).
*   **Rejected-Edit Buffer :** TTL (Time-To-Live) strict de 90 jours ou 500 entrées pour éviter le cimetière sémantique.

### Stade 3 : Compilation Arena (Façon DSPy)
Clone Git éphémère via `git worktree` (90% d'économie disque).
**Fonction de Coût Mathématique :**
`Fitness = α·(Résolution) - β·(Tokens) - γ·(Temps) - δ·(Régression Latérale)`
*Critique :* Si `Régression Latérale > 0` (un patch casse un autre agent via le graphe de dépendance), le *Fitness* s'effondre. Rejet immédiat.

### Stade 4 : La Gate Hiérarchisée (Restauration Règle 14)
*   **Patch TRIVIAL / MINOR :** Auto-merge possible si Fitness > Baseline + 5%.
*   **Patch MAJOR / CRITICAL :** **HITL (Human-In-The-Loop) obligatoire.** Arrêt au SAS. Seul Lord Mahonheim (ou Curator Prime pour validation) peut approuver la gravure dans la *Canonical Memory*.

---

## 4. STRATÉGIE DE PROVISIONNEMENT (Logistique Lean)
L'approche MVP de RENA couplée à la frugalité de GenSpark dicte notre roadmap :

**Phase 1 (MVP Immédiat & Léger) :**
1.  **mmdc (Mermaid CLI) :** 60 Mo. Largement suffisant pour remplacer Playwright sur la validation visuelle basique des schémas.
2.  **LanceDB :** Base vectorielle colonnaire embarquée, parfaite pour archiver le *Rejected-Edit Buffer* sans la lourdeur d'un ChromaDB standalone.
3.  **Tree-Sitter Markdown :** Pour l'analyse AST et le calcul mathématique de la complexité textuelle (mesure du *Context Bloat*).

**Phase 2 (Industrialisation si ROI prouvé) :**
*   Implémentation locale de **DSPy** pur.
*   **Playwright MCP** complet si des tests visuels d'interface Web dynamiques deviennent nécessaires (UI/UX agents).

---

## 5. CONCLUSION ET VERDICT
Le plan v1.0 était visionnaire mais naïf (sans frein). Le plan v2.0 de RENA l'a structuré. L'audit de GenSpark l'a sécurisé mathématiquement. 
Cette **Version 3.0 Ultime** est prête à être exécutée. Elle transforme Tesla d'un "système qui se répare" à un "système qui s'optimise sous tutelle stricte", éradiquant le risque d'emballement darwinien tout en maximisant la vélocité.
