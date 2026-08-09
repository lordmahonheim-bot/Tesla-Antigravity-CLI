# Audit de Convergence : Agent-Reach × Arcanis × Curator Prime

**Date :** 2026-07-07  
**Auditeur :** Tesla (couche AGENTS)  
**Périmètre :** Évaluation structurelle des trois Skills et recommandation d'architecture.  
**Méthode :** Lecture croisée des SKILL.md sources + analyse des dépendances effectives sur MIDGARD.

---

## 1. Diagnostic — Cartographie Factuelle

### 1.1 Inventaire Physique des Composants

| Critère | Agent-Reach | Tesla Arcanis | Tesla Curator Prime |
| :--- | :--- | :--- | :--- |
| **Fichier** | [SKILL.md](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/agent-reach/SKILL.md) (82 lignes, 4 Ko) | [SKILL.md](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-arcanis/SKILL.md) (48 lignes, 3 Ko) | [SKILL.md](file:///home/lord-mahonheim/bifrost/tesla/.agents/skills/tesla-curator-prime/SKILL.md) (210 lignes, 10 Ko) |
| **Sous-dossiers** | `references/` (6 fichiers : social, search, dev, career, video, web — ~17 Ko total) | Aucun | Aucun |
| **Dépendances externes** | Wrapper Python (`tools/agent_reach_wrapper.py` ✅ présent), Exa MCP, Jina Reader, `bili-cli`, `yt-dlp`, `gh`, OpenCLI | `ripgrep`, `jq`, `SQLite`, web search natif | 10 scripts Python spécifiés (non implémentés), Context7 MCP, GitHub MCP, Browser/Playwright |
| **Taille totale** | ~21 Ko (Skill + références) | ~3 Ko | ~10 Ko |

### 1.2 Nature Fonctionnelle (Ce que fait chaque composant)

| Composant | Nature | Rôle Cognitif | Produit-il un livrable certifié ? |
| :--- | :--- | :--- | :--- |
| **Agent-Reach** | Routeur d'acquisition multi-plateformes | **Aucun.** Il route des commandes CLI vers des backends. | ❌ Non. Il retourne des données brutes. |
| **Tesla Arcanis** | Analyste de Deep Research | **Élevé.** Planification, hypothèses H0/H1, comité de lecture, synthèse. | ✅ Oui. Rapport scellé (SHA256). |
| **Tesla Curator Prime** | Chief Knowledge Officer (CKO) | **Maximal.** Fact-checking, certification, indexation, Knowledge Graph. | ✅ Oui. Rapport certifié (score de confiance). |

### 1.3 Chevauchements Détectés

| Zone de recouvrement | Agent-Reach | Arcanis | Curator Prime |
| :--- | :--- | :--- | :--- |
| Recherche web | ✅ Exa, Jina | ✅ `search_web` | ✅ Web Search, Browser |
| Scraping de pages | ✅ Wrapper Python, `curl` | ❌ (non spécifié) | ✅ Browser/Playwright |
| Accès GitHub | ✅ `gh CLI` | ❌ | ✅ GitHub MCP |
| Synthèse / Analyse | ❌ | ✅ Pipeline 5 étapes | ✅ Pipeline 11 étapes |
| Certification | ❌ | ✅ Sceau Arcanis | ✅ Rapport certifié CKO |

> [!WARNING]
> **Fait critique :** Le `AGENTS.md` de gouvernance ne mentionne aucun des trois composants par leur nom. Seuls les termes génériques « Deep Research → ARCANIS.md » et « Extraction sémantique → agent-reach (Skill) » apparaissent dans la table de délégation. Curator Prime n'est pas dans la table. Cela signifie que la politique de délégation formelle est **incomplète**.

---

## 2. Analyse — Les Trois Questions Critiques

### 2.1 Agent-Reach est-il un Agent ou une Capacité ?

**Verdict : C'est une capacité (un routeur I/O), pas un agent.**

Preuves :
- Son SKILL.md déclare explicitement dans la section `NOT for` : *« 本 skill 只负责从互联网获取内容 »* — il ne fait que récupérer du contenu depuis Internet.
- Il ne possède **aucune boucle de raisonnement** (pas de planification, pas d'hypothèses, pas de validation).
- Il ne produit **aucun livrable structuré** (pas de format de rapport, pas de certification, pas de sceau).
- Il est fondamentalement un **multiplexeur de commandes CLI** : il choisit quel backend invoquer (Exa, Jina, OpenCLI, bili-cli, yt-dlp) en fonction de la plateforme cible.

Sa valeur réside dans sa **connaissance procédurale** (quelle commande, quelle API, quel fallback pour chaque plateforme) — pas dans une capacité d'analyse.

### 2.2 Où se situe la frontière entre Arcanis et Curator Prime ?

Le code source des SKILL.md révèle une séparation nette :

```
┌──────────────────────────────────┐    ┌──────────────────────────────────┐
│         TESLA ARCANIS            │    │      TESLA CURATOR PRIME         │
│                                  │    │                                  │
│  Entrée : Question / Hypothèse   │    │  Entrée : Données brutes         │
│                                  │    │          ou rapport Arcanis       │
│  Pipeline :                      │    │                                  │
│  1. Planification                │    │  Pipeline :                      │
│  2. Collecte                     │    │  1. Discovery                    │
│  3. Hypothèses (H0/H1)          │    │  2. Evidence Collection          │
│  4. Comité de lecture            │    │  3. Parsing                      │
│  5. Synthèse                     │    │  4. Fact-Checking                │
│                                  │    │  5. Source Qualification          │
│  Sortie : Rapport scellé SHA256  │    │  6. Comparative Analysis         │
│           (investigation)        │    │  7. Hypothesis Testing           │
│                                  │    │  8. Knowledge Synthesis          │
│                                  │    │  9. Peer Review                  │
│                                  │    │ 10. Certification                │
│                                  │    │ 11. Indexation (Alexandria)      │
│                                  │    │                                  │
│                                  │    │  Sortie : Rapport certifié CKO   │
│                                  │    │           (vérité archivée)       │
└──────────────────────────────────┘    └──────────────────────────────────┘
```

**Observation clé :** Les étapes 1-2 d'Arcanis (Planification + Collecte) et les étapes 1-2 de Curator Prime (Discovery + Evidence Collection) **font le même type de travail**. C'est exactement là qu'Agent-Reach s'insère comme organe d'acquisition partagé.

### 2.3 Les deux options d'intégration sont-elles équivalentes ?

**Non.** L'analyse des pipelines révèle une asymétrie structurelle :

#### Option A — Intégration dans Arcanis

| Critère | Évaluation |
| :--- | :--- |
| Cohérence sémantique | ✅ Arcanis « collecte » déjà (étape 2). Agent-Reach renforce cette étape. |
| Charge cognitive | ✅ Arcanis reste léger (5 étapes + routeur). Le SKILL.md passerait de 48 lignes à ~130 (absorbant les références). |
| Risque de bloat | ⚠️ Modéré. Les 6 fichiers `references/` (~17 Ko) alourdissent le skill, mais restent dans un sous-dossier isolé. |
| Pipeline résultant | Arcanis planifie → Agent-Reach collecte → Arcanis analyse → Arcanis synthétise. **Chaîne linéaire propre.** |
| Autonomie de Curator Prime | ✅ Préservée. Curator Prime reçoit des livrables Arcanis déjà analysés. |

#### Option B — Intégration dans Curator Prime

| Critère | Évaluation |
| :--- | :--- |
| Cohérence sémantique | ⚠️ Partielle. Curator Prime fait du « Discovery » (étape 1), mais son identité est celle d'un CKO, pas d'un collecteur. |
| Charge cognitive | ❌ Curator Prime est déjà le skill le plus lourd (210 lignes, 10 Ko, 10 scripts spécifiés, 11 étapes). L'ajout des 6 références d'Agent-Reach le porterait à ~27 Ko. |
| Risque de bloat | 🔴 Élevé. Mélange acquisition Internet + parsing documentaire + certification + indexation. Trop de responsabilités. |
| Pipeline résultant | Curator Prime collecte → Curator Prime parse → Curator Prime vérifie → Curator Prime certifie → Curator Prime indexe. **Monolithique.** |
| Principe SRP | ❌ Violation du Single Responsibility Principle. Le CKO ne devrait pas être son propre fournisseur de matière première. |

---

## 3. Verdict

### 3.1 Sur la promotion d'Agent-Reach au rang d'agent d'élite

> **Verdict : REFUSÉ.**

Promouvoir Agent-Reach serait une erreur architecturale. Les faits sont sans ambiguïté :
- Il ne raisonne pas.
- Il ne certifie pas.
- Il ne produit aucun livrable autonome.
- Il est un **organe d'acquisition**, analogue à un bus I/O dans un processeur. Un bus I/O n'est pas un cœur de calcul.

### 3.2 Sur l'intégration dans Curator Prime (Option B)

> **Verdict : DÉCONSEILLÉ.** Score : 6/10.

Curator Prime est déjà le composant le plus complexe de l'écosystème (11 étapes, 10 outils spécifiés). Lui ajouter la responsabilité d'acquisition Internet violerait le principe de séparation des responsabilités et le rendrait difficile à maintenir. De plus, son identité de « gardien de la vérité » entre en contradiction avec le rôle de « chasseur de données brutes ».

### 3.3 Sur l'intégration dans Tesla Arcanis (Option A)

> **Verdict : RECOMMANDÉ.** Score : 9/10.

L'intégration est naturelle et cohérente. Arcanis a déjà une étape « Collecte » dans son pipeline qui manque d'outillage concret (il ne spécifie que `ripgrep`, `jq`, `SQLite` et `search_web` — des outils locaux). Agent-Reach comble exactement cette lacune en apportant :
- 15 plateformes routées.
- Un wrapper Python de fallback.
- Des références procédurales par catégorie.

L'architecture cible résultante serait :

```
                    ┌─────────────────────────────┐
                    │     TESLA ARCANIS-360        │
                    │   (Deep Research + OSINT)    │
                    │                              │
                    │  1. PLANIFICATION             │
                    │      │                       │
                    │      ▼                       │
                    │  2. COLLECTE ◄── Agent-Reach │
                    │     (routeur multi-plateformes)│
                    │      │                       │
                    │      ▼                       │
                    │  3. HYPOTHÈSES (H0/H1)       │
                    │      │                       │
                    │      ▼                       │
                    │  4. COMITÉ DE LECTURE         │
                    │      │                       │
                    │      ▼                       │
                    │  5. SYNTHÈSE                 │
                    │      │                       │
                    │  Sortie : Rapport scellé     │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │    TESLA CURATOR PRIME       │
                    │        (CKO)                │
                    │                              │
                    │  Fact-Checking               │
                    │  Certification               │
                    │  Indexation → Alexandria     │
                    │  Archivage → Avalon          │
                    └─────────────────────────────┘
```

### 3.4 Points d'Attention pour l'Implémentation

> [!IMPORTANT]
> Si l'Option A est retenue, les actions suivantes seront nécessaires :

1. **Fusion physique :** Intégrer le contenu d'`agent-reach/SKILL.md` dans `tesla-arcanis/SKILL.md` comme sous-section « Moteur d'Acquisition Internet » à l'étape 2 (Collecte). Déplacer le dossier `references/` dans `tesla-arcanis/references/`.
2. **Mise à jour de la gouvernance :** Modifier la table de délégation dans [AGENTS.md](file:///home/lord-mahonheim/bifrost/tesla/.agents/AGENTS.md) pour retirer la ligne `Extraction sémantique → agent-reach (Skill)` et la remplacer par `Extraction sémantique → Arcanis (intégré)`.
3. **Mise à jour du trigger system :** La description du skill Arcanis dans les métadonnées Antigravity devra absorber les triggers multilingues d'Agent-Reach (recherche, plateforme, URL).
4. **Préservation du wrapper :** Le fichier `tools/agent_reach_wrapper.py` reste à sa place dans le répertoire `tools/` — il n'est pas spécifique au skill, c'est un utilitaire de l'écosystème.
5. **Retrait du skill autonome :** Supprimer le dossier `agent-reach/` de `.agents/skills/` une fois la fusion validée.
6. **Curator Prime — Discovery :** L'étape 1 (Discovery) de Curator Prime devra être reformulée pour clarifier qu'elle reçoit ses sources *depuis Arcanis* et non par exploration directe, sauf pour les documents locaux (filesystem).

---

*Audit réalisé sur les fichiers sources au 2026-07-07. Aucune hypothèse présentée comme fait. Tout raisonnement est traçable aux lignes sources citées.*
