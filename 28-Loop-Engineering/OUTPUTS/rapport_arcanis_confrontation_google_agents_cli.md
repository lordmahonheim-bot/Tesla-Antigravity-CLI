---
type: reference
tags: [engineering/agents-cli, statut/valide, methode/confrontation-audit]
source: "[[Alexandria::google_agents_cli_confrontation_2026]]"
date: 2026-06-30
version: 1.0
author: "Tesla Arcanis"
certification: "Arcanis_Seal_v3"
---

# Rapport de Confrontation : Architecture Synergique d'Intégration d'Antigravity CLI & Google Agents CLI
## Analyse Documentaire Critique et Plan d'Intégration Consolidé sous la Doctrine du Vigilum Codex

---

## 1. Introduction et Démarche de Confrontation

Sous les directives rigoureuses de la doctrine du **Vigilum Codex**, une confrontation systématique a été menée entre le plan/rapport initial d'intégration (v1.0) et le rapport d'audit correctif d'Arcanis (contenant 12 anomalies documentées). L'objectif est double :
1. Assurer une **discipline de vérité absolue** en purgeant les approximations techniques, terminologiques ou de marqueurs tiers.
2. Établir une **architecture d'intégration consolidée** pour l'écosystème **MIDGARD** (Linux, CPU-only, 8 Go RAM) exploitant **Antigravity CLI** (`agy`) et **Google Agents CLI** (`agents-cli`).

Cette confrontation se base sur les faits vérifiés et remplace toute hypothèse non validée par des données factuelles issues de l'état de l'art technologique à la date de juin 2026.

---

## 2. Analyse de Substance : Diagnostic des 12 Anomalies

L'analyse minutieuse du document d'audit permet d'extraire les anomalies suivantes, classées par ordre de gravité décroissante. Chaque fiche identifie la faille conceptuelle de la v1.0 et établit la rectification factuelle correspondante.

### Tableau Récapitulatif des Écarts et Rectifications

| # | Gravité | Section | Description de l'Anomalie | Fait Rectifié (Doctrine du Vigilum Codex) |
|---|---|---|---|---|
| **1** | **CRITIQUE** | §2 | Framework Karpathy incomplet : 3 piliers au lieu de 5. | Karpathy définit 5 piliers. Ajout de **Diff Review** (revue d'architecture) et **Quality Taste** (conception sobre). |
| **2** | **CRITIQUE** | §3.C | Attribution erronée de l'anti-bloat de 70%+ à `agy`. | Le filtrage à 70%+ provient de **RTK (Rust Token Killer)**. Le filtrage natif d'Antigravity est de 20-40%. |
| **3** | **CRITIQUE** | §4 | Omission de la fermeture d'Antigravity CLI (closed-source). | Antigravity CLI est **closed-source** pour les individuels depuis le 18 juin 2026. Gemini CLI open-source est arrêté. |
| **4** | **MAJEURE** | §2.C | Dénaturation du raccourci `ctrl+k` (verrou de déploiement). | `ctrl+k` est l'approbation générale de toute action de sous-agent. Navigation via `alt+j`. |
| **5** | **MAJEURE** | §1 | Omission du nom exact du binaire d'Antigravity. | Le nom exact du binaire est **`agy`**, non « antigravity ». |
| **6** | **MAJEURE** | §3.A | Présentation du sandboxing comme actif et natif par défaut. | Sandbox désactivé par défaut (`enableTerminalSandbox: false`). Utilise `nsjail` sur Linux. |
| **7** | **MAJEURE** | §1, §4 | Présentation d'Antigravity comme basé uniquement sur Gemini. | Antigravity est **multi-modèle** (8 modèles dont Claude 4.6). Le lock-in se déplace vers la plateforme. |
| **8** | **MAJEURE** | §1 | Commande `npx skills add` tronquée et inopérante. | La syntaxe correcte est `npx -y skills add https://github.com/google/agents-cli -y --all -g`. |
| **9** | **MINEURE** | §1 | Non-nomination des 7 compétences (skills) ADK injectées. | Les compétences sont identifiées nominalement (de `adk-code` à `workflow`). |
| **10** | **MINEURE** | §2.A | Référence non sourcée au template `agentic_rag`. | Les templates officiels sont générés dynamiquement par `agents-cli scaffold create`. |
| **11** | **MINEURE** | §1 | Confusion terminologique de l'écosystème cloud Google. | Distinction claire entre **Agent Platform**, **Agent Runtime** et **Vertex AI Agent Engine**. |
| **12** | **MINEURE** | §3.C.3 | Intégration non signalée de composants propres à MIDGARD. | Le RAG Alexandria (k=60, SQLite FTS5) est spécifique à MIDGARD, pas au produit général. |

---

### Analyse Détaillée des Rectifications Clés

#### 1. Le Framework de l'Agentic Engineering de Karpathy (Anomalie 1)
La v1.0 tronquait le cadre méthodologique défini par Andrej Karpathy (Sequoia Ascent 2026) à trois piliers. Le cadre complet en comporte cinq, indispensables pour structurer le développement d'agents sous la gouvernance locale :
*   **Spec Design** : Spécifier formellement le comportement et les interfaces de l'agent (fichiers YAML et `DESIGN_SPEC.md`) en amont de toute phase de code.
*   **Diff Review [NOUVEAU]** : Procéder à une relecture fine de chaque modification proposée pour en valider la cohérence architecturale (via l'Artifact Review Panel et `ctrl+r`), empêchant les régressions logiques et limitant la surconsommation de tokens.
*   **Eval Loops** : Tester l'agent à l'aide de cas d'évaluation standardisés (20 à 50 cas) pour mesurer objectivement ses performances de manière continue.
*   **Quality Taste [NOUVEAU]** : Juger de la sobriété et de l'élégance architecturale du code produit par l'agent. Le code fonctionnel ne doit pas être inutilement complexe (*bloat*). Les compétences humaines se déplacent vers le goût en design système.
*   **Security Oversight** : Confiner les droits d'exécution et sécuriser la manipulation des données sensibles.

#### 2. L'Origine Réelle de l'Anti-Bloat à 70%+ : RTK en Rust (Anomalie 2)
La v1.0 prêtait à Antigravity CLI un filtrage de bruit de terminal permettant d'économiser 70%+ de tokens. L'analyse critique montre que le filtrage natif d'Antigravity CLI (compression de barres de progression, suppressions de logs mineurs) n'économise que 20% à 40%. Pour atteindre le taux d'anti-bloat de 70% à 90% par commande interceptée, l'intégration de **RTK (Rust Token Killer)**, proxy en Rust indépendant et open-source, est indispensable. Son installation et sa liaison avec Antigravity via `rtk init -g --gemini` constituent un verrou d'efficacité majeur pour MIDGARD.

#### 3. Fermeture Intellectuelle et Logique de Lock-in d'Antigravity (Anomalies 3 & 7)
Le 18 juin 2026, l'accès individuel au projet open-source Gemini CLI (Apache 2.0, 104K+ étoiles) a été interrompu par Google. Le successeur, Antigravity CLI (`agy`), est proposé sous forme de binaire fermé (*closed-source*) pour les utilisateurs individuels (seuls les clients entreprise conservent une version source). Cette transition aggrave le *Vendor Lock-in* car il est désormais impossible d'auditer le code source du binaire local.
De plus, bien que le binaire `agy` expose un catalogue multi-modèle (incluant Claude Sonnet/Opus 4.6 et GPT-OSS 120B), ce choix technique ne brise pas le lock-in : il le déplace du modèle brut vers la plateforme d'orchestration de Google (ADK, Agent Runtime, GCP).

#### 4. Fonctionnement du Verrou Local d'Approbation (Anomalie 4)
Le raccourci clavier `ctrl+k` n'est pas exclusif aux actions de déploiement de l'agent. Dans l'architecture d'Antigravity CLI, `ctrl+k` valide de manière globale n'importe quelle action de sous-agent en attente (exécution d'un outil MCP, commande bash, modification de fichier). La navigation d'un sous-agent bloqué à un autre s'effectue quant à elle par le raccourci `alt+j`.

#### 5. Précisions Opérationnelles (Anomalies 5, 6, 8, 9, 10, 11, 12)
*   **Sandbox** : L'isolation par sandbox au niveau de l'OS (utilisant `nsjail` sur Linux) est désactivée par défaut dans `agy` (`enableTerminalSandbox: false`). Elle doit faire l'objet d'une activation manuelle explicite.
*   **Setup d'ADK** : La commande d'injection de compétences ADK est `npx -y skills add https://github.com/google/agents-cli -y --all -g`. Elle permet d'importer précisément 7 compétences (`google-agents-cli-adk-code`, `google-agents-cli-deploy`, `google-agents-cli-eval`, `google-agents-cli-observability`, `google-agents-cli-publish`, `google-agents-cli-scaffold`, `google-agents-cli-workflow`).
*   **Composants Cloud** : Distinction nette entre l'**Agent Platform** (cadre global Gemini Enterprise), l'**Agent Runtime** (le service managé et sécurisé gérant l'état, les sessions et la mémoire long-terme) et le **Vertex AI Agent Engine** (le point d'accès pour le déploiement Cloud Run).

---

## 3. Plan Consolidé d'Intégration d'Antigravity CLI & Google Agents CLI sur MIDGARD

Ce plan technique, adapté aux contraintes de **MIDGARD** (Linux, CPU-only, 8 Go RAM), intègre l'ensemble des corrections factuelles pour garantir une gouvernance robuste et une sobriété de consommation de tokens.

```mermaid
graph TD
    subgraph Local [Environnement Local MIDGARD - CPU / 8Go]
        Agy[Antigravity CLI - agy] -->|nsjail Sandbox opt-in| Bash[Bash Shell]
        RTK[Rust Token Killer - RTK Proxy] -->|Compresse 70-90%| Agy
        Alex[Alexandria RAG - SQLite FTS5] -->|Indexation Skills| Agy
        Python[Python/Regex Evals - Lvl 1] -->|Validation Commit 0 Token| Agy
        Agy -->|ctrl+r| Panel[Artifact Review Panel]
        Agy -->|ctrl+k| Approve[Validation Humaine]
    end
    subgraph Cloud [Google Cloud Platform - Vertex AI]
        Engine[Vertex AI Agent Engine] -->|Exécution Distante| API[Gemini API / Claude / GPT]
        Runtime[Agent Runtime - Sessions/Mémoire] --> Engine
    end
    Approve -->|gcloud auth| Engine
    Agy -->|npx skills add| ADK[7 Skills ADK]
```

### Étape 1 : Initialisation et Prérequis Système
1.  **Vérification des versions logicielles locales** :
    ```bash
    uv --version          # Doit être >= 0.4
    node --version        # Doit être >= 18 (pour le moteur npx)
    agy --version         # Doit être >= 1.0.2
    ```
2.  **Configuration de l'authentification** :
    L'authentification s'effectue via `agy auth login` ou par la déclaration dans le shell de la variable `ANTIGRAVITY_TOKEN`. La validité de la connexion est vérifiée à l'aide de la commande `agy auth status`.

### Étape 2 : Injection Sécurisée des Compétences ADK
1.  **Exécution du setup global de l'ADK** :
    ```bash
    uvx google-agents-cli setup
    ```
2.  **Lancement de la commande d'injection complète des 7 compétences** :
    ```bash
    npx -y skills add https://github.com/google/agents-cli -y --all -g
    ```
    Cette commande déploie les compétences nominatives d'ADK de `google-agents-cli-adk-code` à `google-agents-cli-workflow` dans le dossier local `~/.agents/skills/`.

### Étape 3 : Durcissement de la Sécurité Locale (Sandbox nsjail)
1.  **Activation de l'isolation système** :
    Le paramètre `enableTerminalSandbox` doit être forcé à `true` dans le fichier de configuration global d'Antigravity CLI. Sur MIDGARD, cette activation s'appuie sur le moteur d'isolation `nsjail` sous Linux pour confiner les droits d'écriture et réseau.
2.  **Politique d'autorisation asymétrique** :
    Configurer le paramètre `toolPermission` à `proceed-in-sandbox`. Les sous-agents s'exécutent automatiquement dans les limites du sandbox, mais toute tentative de contournement ou commande sensible (ex: `rm`, `mv`, `gcloud`, `agents-cli deploy`) requiert l'approbation explicite de Lord Mahonheim via le raccourci `ctrl+k` (et navigation via `alt+j`).

### Étape 4 : Déploiement du Proxy RTK (Anti-Bloat)
1.  **Installation de Rust Token Killer** :
    ```bash
    curl -fsSL https://rtk-ai.app/install.sh | bash
    ```
2.  **Liaison globale et initialisation** :
    ```bash
    rtk init -g --gemini
    ```
    Le proxy RTK intercepte de manière transparente les appels et compresse à hauteur de 70-90% les sorties des outils d'infrastructure (les barres de progression `pip`, les sorties d'historiques git, les traces de compilation CPU), protégeant le budget de tokens de MIDGARD.

### Étape 5 : Cadre d'Évaluation Hybride (Économie de Tokens & CPU)
Pour pallier l'absence de GPU sur MIDGARD rendant impossible l'exécution d'un juge LLM local, le workflow de test est scindé en deux niveaux :
1.  **Évaluations Locales (Niveau 1 — Déterministe)** :
    Implémentation de scripts Python d'évaluation légers effectuant des assertions strictes (conformité de structures JSON, vérification de types, présence de métadonnées, validation regex de motifs critiques).
    *Coût : 0 token API. Exécution locale instantanée.*
2.  **Évaluations Distantes (Niveau 2 — LLM-as-a-Judge)** :
    Appel à un modèle distant Gemini ou Claude via `agents-cli eval run` pour juger de la cohérence sémantique des réponses sur un échantillon réduit de 20 cas d'usage. Ce niveau est déclenché exclusivement lors des jalons de publication majeurs.

### Étape 6 : Préservation de l'Indépendance (Anti Lock-in)
Puisque le binaire `agy` est closed-source pour l'utilisation individuelle et que l'Agent Runtime de destination est propriétaire, les développements locaux doivent rester portables :
1.  **Spécification de Design Déclarative** :
    Chaque agent doit posséder un fichier de spécification `DESIGN_SPEC.md` indépendant de la syntaxe ADK, décrivant les entrées/sorties et les fonctions de l'agent.
2.  **Indexation locale des Skills** :
    Chaque compétence ADK ou script d'outils est documenté sous forme de fiche miroir Markdown normalisée dans le dossier d'index d'Alexandria `/home/lord-mahonheim/bifrost/tesla/Avalon/03-Resources/`. Alexandria (RRF k=60, SQLite FTS5) permet à l'assistant de retrouver les syntaxes locales sans consommer de tokens d'entrée distants par des scans de documentation verbeux.

---
### ⚖️ SCEAU DE CERTIFICATION (IMMUABLE)

> **Arcanis.** Enquête planifiée. Hypothèses testées. Sources croisées. Livrable certifié.  
> — Validé par Arcanis. Archive de référence.  
> `SHA256:66946b31cea210a70832f06f6ffeb3abfc5726f7999dcd0ca05e8632d5e7332d`

Signé / Fait par : Tesla sur Antigravity CLI
Main rendue à Mahonheim
