# Rapport Comparatif : Headroom vs LeanCTX dans l'Écosystème Tesla × Antigravity

## 1. Diagnostic de l'Existant & Fiches d'Identité

Nous avons analysé les deux approches de réduction et d'optimisation de contexte pour les LLM : **Headroom** et **LeanCTX**. Bien que partageant l'objectif commun d'économie de tokens, elles opèrent à des niveaux totalement distincts du cycle d'exécution.

### A. Headroom : Le Proxy de Compression Réversible
* **Niveau d'action** : Couche réseau / Middleware API (entre l'agent et le fournisseur de LLM).
* **Fonctionnement** : Compresse le texte envoyé et stocke la version brute localement. Si le LLM détecte qu'une information cruciale a été tronquée par la compression, il exécute un outil spécifique pour réclamer le fragment brut manquant.
* **Point fort** : Compression réversible et dynamique (CCR).

### B. LeanCTX : Le Moteur de Contexte Déterministe Local
* **Niveau d'action** : Couche d'ingestion / Préparateur de prompts (entre le workspace local et l'agent).
* **Fonctionnement** : Analyse le code local via un parseur syntaxique (AST via Tree-sitter) pour n'envoyer que la structure ou les signatures de fonctions. Il gère également le cache de session, la sécurité des accès fichiers (`PathJail`) et s'intègre via le protocole standard **MCP**.
* **Point fort** : Intégration native MCP, compression structurelle stable pour le prompt-caching.

---

## 2. Analyse Comparative selon nos Critères

| Critère d'Évaluation | Solution A : **Headroom** | Solution B : **LeanCTX** |
| :--- | :--- | :--- |
| **Performance (Vitesse & CPU)** | **Moyenne** : Surcharge CPU locale pour la compression et gestion du cache d'expansion en temps réel. | **Excellente** : Parsing AST (Tree-sitter) en C extrêmement rapide, sans latence. |
| **Sécurité & Gouvernance** | **Basse** : N'inclut pas de contrôle d'accès sur l'environnement local. | **Haute** : Intègre des règles strictes comme `PathJail` pour confiner l'agent. |
| **Économie de Tokens** | **60 % à 95 %** (via compression brute de texte). | **60 % à 90 %** (via élagage structurel et prompt caching). |
| **Compatibilité Antigravity** | **Complexe** : Nécessite de détourner le client d'API interne d'Antigravity vers un proxy tiers. | **NATIVE** : S'intègre comme serveur MCP déclarable dans `mcp_config.json`. |

---

## 3. Confrontation Technique & Intégration avec Antigravity

### Le problème d'intégration de Headroom
Antigravity CLI (`agy`) est un logiciel packagé avec ses propres appels client gérés en interne vers Google Gemini. Intercepter ces requêtes pour insérer le proxy Headroom nécessite :
1. De rediriger les endpoints d'API (ce qui n'est pas toujours exposé ou configurable).
2. D'exposer au modèle Gemini l'outil (Tool) de récupération de fragments originaux (`CCR`), ce qui implique de modifier le système de déclaration d'outils d'Antigravity.
*C'est une intégration lourde, intrusive et sujette aux cassures lors des mises à jour d'Antigravity.*

### La simplicité d'intégration de LeanCTX
LeanCTX est conçu dès le départ pour fonctionner comme un serveur **MCP (Model Context Protocol)**. Antigravity CLI supportant nativement les serveurs MCP :
1. Nous déclarons le serveur `lean-ctx` dans [mcp_config.json](file:///home/lord-mahonheim/.gemini/antigravity-cli/mcp_config.json).
2. L'agent Tesla peut interroger directement les outils de LeanCTX pour lire des fichiers compressés, inspecter l'arborescence ou vérifier ses limites d'accès.
3. Les prompts générés par LeanCTX étant stables au niveau de l'octet (byte-stable), ils exploitent au maximum le **Prompt Caching** natif de Gemini (facturation divisée par 4 sur les parties de prompt répétées).

---

## 4. Verdict Stratégique de Tesla

**VERDICT : LEANCTX EST LE GAGNANT UNIQUE ET ABSOLU (GO POUR LEANCTX / NO-GO POUR HEADROOM)**

### Justification :
* **Headroom** est un outil taillé pour des applications personnalisées avec accès total au code source du client d'API. Dans notre cadre d'utilisation d'un agent CLI commercial packagé (`agy`), son intégration est trop complexe, instable et n'apporte aucun gain supérieur à LeanCTX.
* **LeanCTX** offre une synergie parfaite avec notre doctrine de gouvernance locale :
  1. Il respecte notre architecture en s'installant comme un serveur **MCP**.
  2. Il renforce notre **sécurité** via `PathJail` (confinement d'accès aux fichiers du workspace).
  3. Il optimise la **performance sémantique** en évitant à Gemini de se noyer dans du code brut verbeux.
  4. Il garantit une **économie de tokens** optimale grâce à la stabilité de son cache.

---
*Livrable enregistré localement pour Obsidian Avalon dans [OUTPUTS/analyse_headroom_vs_leanctx.md](file:///home/lord-mahonheim/bifrost/tesla/OUTPUTS/analyse_headroom_vs_leanctx.md).*
