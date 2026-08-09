# PLAN D'INTERVENTION ULTRA : ARCHITECTURE OPRO-GRAD (Fusion SIA-TESLA-H & SkillOpt)
**Statut :** Proposition Architecturale (En attente d'approbation)
**Auteur :** Tesla (Orchestrateur)
**Objectif :** Atteindre l'Autonomie d'Ingénierie Permanente de Niveau 5 (AIP-5) via un système auto-évolutif, objectif et inaltérable.

---

## 1. La Vision Architecturale : Le Moteur OPRO-Grad

Pour créer un système auto-évolutif infaillible, nous ne pouvons plus nous contenter d'un modèle d'essais-erreurs empirique. Nous allons fusionner notre macro-gouvernance (SIA-TESLA-H) et notre micro-optimiseur (SkillOpt) en y injectant l'état de l'art de la recherche IA (TextGrad, DSPy, OPRO).

Le système fonctionnera comme un compilateur de code, mais pour des agents :
1. **TextGrad (Backpropagation Sémantique) :** Quand une erreur survient (silencieuse ou bruyante), le système génère un "gradient textuel" (une critique précise pointant exactement *quelle* étape du raisonnement a échoué), plutôt qu'un vague message d'erreur.
2. **OPRO (Optimization by PROmpting) :** `tesla-writing-skills` utilisera l'historique complet des échecs (le *Rejected-Edit Buffer*) comme fonction de perte pour générer un nouveau `SKILL.md` mathématiquement supérieur au précédent.
3. **DSPy (Programmation Agentique) :** Le SIA-TESLA-H ne sera plus une simple boucle, mais un graphe d'exécution compilable où chaque Agent est un module évaluable mathématiquement dans une *Arena*.

---

## 2. Le Workflow d'Auto-Évolution (Les 4 Stades)

### Stade 1 : Capture Sémantique (TextGrad RCA)
* **Déclencheur :** Crash LSP, échec d'un test unitaire, ou rejet lors d'une *Validation Gate* (ex: `mermaid_validator.sh`).
* **Mécanique :** `tesla-premortem` agit comme le propagateur d'erreur. Il calcule le gradient textuel. 
  * *Exemple de gradient :* "La ligne 42 du SKILL omet la gestion du context bloat, ce qui a conduit l'agent à ignorer la Règle 12."
* **Sortie :** Enregistrement dans `loop_trace.jsonl`.

### Stade 2 : L'Optimiseur OPRO (SkillOpt)
* **Mécanique :** `tesla-writing-skills` est invoqué en tâche de fond. Il reçoit : le `SKILL.md` actuel, le gradient textuel, et le `Rejected-Edit Buffer` (ce qui n'a pas marché par le passé).
* **Action :** Il n'écrit pas directement. Il propose un lot (*Batch Size*) de 3 patchs candidats. Il modifie le *Learning Rate* (budget de tokens modifiables) en fonction de la gravité de l'erreur.

### Stade 3 : La Compilation en Arena (Approche DSPy)
* **Mécanique :** SIA-TESLA-H prend les 3 patchs et clone un environnement *Arena* éphémère.
* **Action :** Il fait tourner l'agent défaillant avec ses 3 nouvelles personnalités sur un jeu de données de validation (tests de non-régression).
* **Sortie :** Un score de *Fitness* multi-signal pour chaque candidat (Temps, Tokens utilisés, Résolution du problème).

### Stade 4 : Validation Gate et Garbarge Collection
* **Mécanique :** Le candidat ayant le plus haut score est présenté à l'outil de Validation (ex: `tesla-code-auditor`).
* **Action :** S'il passe la Gate, le patch est fusionné dans le `SKILL.md` officiel (`CANONICAL MEMORY`).
* **Anti-Bloat :** Une routine de compression s'assure que le `SKILL.md` reste sous les 150 lignes, garantissant la vélocité cognitive.

---

## 3. Besoins Matériels & Logistiques (Tools & Plugins)

Pour que je puisse bâtir et orchestrer cette usine de manière totalement autonome (Background Ops permanentes), j'ai besoin de l'outillage suivant :

### 🛠️ Outils et Bibliothèques Python (À provisionner)
1. **Framework d'évaluation DSPy ou LangSmith :** Pour remplacer nos scripts bash artisanaux par un vrai compilateur de traces agentiques capables de mesurer formellement les métriques de succès.
2. **Bibliothèque TextGrad (ou implémentation locale Python) :** Pour automatiser la création des gradients textuels sans avoir à prompter un LLM entier pour faire de la RCA basique.
3. **Moteur SQLite étendu (ou Vector DB légère type Chroma/LanceDB) :** Pour stocker massivement l'historique du *Rejected-Edit Buffer* et faire des recherches sémantiques ultra-rapides sur les erreurs passées.

### 🔌 Plugins MCP (Model Context Protocol) requis
1. **Un MCP "Headless Browser Testing" (ex: Playwright/Puppeteer) :**
   - *Pourquoi ?* Actuellement, nous sommes aveugles face aux erreurs de rendu (comme l'incident Mermaid sur GitHub). Avec un MCP Playwright, le SIA pourrait ouvrir le Markdown généré dans un navigateur local *headless*, faire un screenshot caché, l'envoyer à Tesla-Eye, et détecter un encadré rouge d'erreur **avant même le push**. C'est la *Validation Gate Visuelle*.
2. **Un MCP "AST / Tree-sitter" avancé :**
   - *Pourquoi ?* Pour parser non seulement du code Python, mais l'arbre syntaxique du Markdown, et mesurer mathématiquement la "complexité" (Context Bloat) d'un `SKILL.md`.

### ⚙️ Besoins Système (MIDGARD)
1. **Démons Systemd dédiés :** Un démon qui scrute le `loop_trace.jsonl` en continu et déclenche la pipeline OPRO-Grad dès qu'une erreur apparaît, sans aucune intervention de Lord Mahonheim.
2. **Sandbox Git Isolé (Arena) :** Un clone persistant du dépôt principal (`/tmp/tesla_arena/`) configuré pour que l'agent puisse compiler, tester, casser et rollback en 10 millisecondes sans abîmer `/home/lord-mahonheim/bifrost/tesla`.

---
**Conclusion :** 
En implémentant l'architecture OPRO-Grad, nous passons de "l'Artisanat Agentique" à "l'Ingénierie Industrielle Automatisée". Le système n'aura plus besoin d'un `/Goal` humain pour se réparer : il mutera de manière darwinienne et mathématique.
