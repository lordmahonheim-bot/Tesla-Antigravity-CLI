# Feuille de Route Tesla × Vigilum Codex — Court & Moyen Terme (v1.0)

* * *
## **Doctrine :** Vigilum Codex · **Constitution :** SOUL v3.0 · **Gouvernance :** AGENTS v4 / FORCE\_TOOLING v1.0
## **Analyste :** Tesla (Gemini sur Antigravity CLI) · **Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)
## **Date :** 2026-07-25 · **Version :** 1.0 (Draft)
> **Principe cardinal de cette feuille de route**  
> Court terme = **consolider, sécuriser, finir ce qui est en vol**. Moyen terme = **étendre, distribuer, monétiser**.  
> Aucune capacité n'entre si elle ne renforce pas l'architecture (Doctrine VC #3 : _Cohérence avant expansion_).  
> Chaque brique suit le cycle de vie FORCE\_TOOLING : `Draft → Experimental → Validated → Stable → Deprecated → Archived`.
* * *
## 0\. Boussole d'alignement
Chaque projet de cette roadmap est rattaché à **une branche Vigilum Codex** et sert **un principe SOUL** :

| Branche Vigilum Codex | Principe SOUL dominant | Ce que ça produit |
| ---| ---| --- |
| Performance Humaine | Mahonheim First | Runbooks, standards transmissibles |
| Intelligence Stratégique | Proof First | Veille, mémoire, analyse gouvernée |
| Opérations IA Gouvernées | Security First / Action First | Skills, Agents, plugins, MCP maîtrisés |

**Règle de tri :** un chantier qui ne rentre dans aucune branche ne rentre pas dans la roadmap.

* * *
# 🔵 COURT TERME (0–3 mois) — Consolidation & Étanchéité
> Objectif : passer l'écosystème actuel de _« ça tourne »_ à _« c'est stable, gouverné, prouvé »_. On ne crée presque rien de neuf ; on **verrouille et on finit**.
## CT-1 · Finaliser les chantiers en vol
**Branche :** Opérations IA Gouvernées · **Statut visé :** Experimental → Validated
*   **`tesla-video-director`** : terminer la refonte v2 (moteur AREngine — 13 blocs, 6 règles transverses). Sortie : `SKILL.md` canonique + smoke-test.
*   **`tesla-team-synergy`** (Mission Orchestrator) : livrer le triptyque _Mission Graph +_ [_PLAN.md_](http://PLAN.md) _+ Capability Scoring_ pour que l'orchestration multi-agents devienne réellement opérable.
*   **Skills référencés mais non consolidés** dans la table de délégation AGENTS : `tesla-curator-prime`, `tesla-code-auditor`, `tesla-loop-orchestrator`. Décider pour chacun : **construire, geler ou archiver**. Pas de skill fantôme dans la doctrine.
## CT-2 · Vigilum Gateway V2.1 — durcir la porte d'entrée des Skills
**Branche :** Opérations IA Gouvernées · **Principe :** Security First

Formaliser et **rendre obligatoire** pour toute skill (nouvelle ou existante) le contrat d'injection déclaré dans FORCE\_TOOLING §5 :
*   `tool_dependencies` (dépendances d'outils explicites)
*   mode de permission requis (`interactive` vs `goal`)
*   circuit breaker de retry (max 3 tentatives self-healing)

Livrable : un **linter de conformité de skill** (`validate_skill.py`) qui refuse toute skill non conforme à la Gateway. C'est le prolongement naturel de `validate_note.py`.
## CT-3 · Harmonisation de la Source de Vérité (`/memory`)
**Branche :** Intelligence Stratégique · **Principe :** Proof First

Appliquer le Protocole §14 d'AGENTS de façon **automatisée** au lieu de manuelle. Aujourd'hui la synchro des 10 fichiers canoniques (`PROJECT_STATE`, `SESSION_LOG`, `liste_projets_antigravity_BASE`, `AGENTS`, `GEMINI`, `ENGINE`, `FORCE_TOOLING`, `SOUL`, `TESLA.json`, `settings.json`) repose sur la discipline.
Livrable : script `sync_source_of_truth.py` + hook de fin de session qui **détecte les dérives** entre ces fichiers et l'état réel de l'écosystème, et bloque la clôture si désynchronisé.
## CT-4 · Registre des Politiques (Policy Registry)
**Branche :** Opérations IA Gouvernées · **Principe :** Security First

FORCE\_TOOLING §7 liste 8 politiques (Discovery, Selection, Routing, Skill, MCP, Tool, Memory, Security) mais elles ne sont pas encore **versionnées indépendamment**.
Livrable : dossier `policies/` avec un fichier versionné par politique + un `INDEX.md` de registre. Chaque skill référence la version de politique qu'elle respecte. C'est la colonne vertébrale de gouvernance qui manque.
## CT-5 · MVP GitHub public — preuve de capacité
**Branche :** Performance Humaine (portfolio) + Opérations IA Gouvernées · **Principe :** Mahonheim First

Le dépôt `Tesla-Antigravity-CLI` est publié mais doit devenir **une vitrine de gouvernance**, pas de code brut (cf. MY\_COMPANY §14 : _preuve de capacité à concevoir/documenter/gouverner_).
*   Documenter le protocole **Shadow-Targeting** en field-note publique anglaise (méthodo « Test → Stabilize → Document » de MY\_BRANDING).
*   Publier `tesla-github-manager` v3.0.0 comme skill-vitrine (OpenSSF Scorecard ≥ 8/10 déjà en place).
*   Vérifier le rituel de double commit/push (AGENTS §12) avant toute synchro.
> ⚠️ **Rappel gouvernance :** tout push distant reste soumis à ton autorisation explicite préalable (AGENTS §7 / FORCE\_TOOLING §10). Aucune exception, même en `/goal`.
## CT-6 · Argus Core — premier moteur de veille opérationnel
**Branche :** Intelligence Stratégique · **Principe :** Action First

Activer le système local de collecte RSS/articles déjà nommé dans MY\_COMPANY §14. C'est la brique la plus simple de la couche veille et elle alimente directement Alexandria.
Livrable : ingestion RSS → normalisation → indexation FTS5/Vectorielle dans `alexandria_brain.db`. Réutilise l'ETL existant.

* * *
# 🟡 MOYEN TERME (3–9 mois) — Expansion, Distribution, Monétisation
> Objectif : sortir du sanctuaire personnel vers les cercles externes (MY\_COMPANY §9-10 : _de l'intérieur vers l'extérieur_). On construit du neuf, mais uniquement sur une base consolidée.
## MT-1 · T.A.H.O Nexus — veille stratégique automatisée
**Branche :** Intelligence Stratégique · **Statut visé :** Draft → Experimental

Le niveau au-dessus d'Argus Core : transformer l'actualité en **information structurée, analysée, exploitable**.
Composants : pipeline de filtrage → analyse (résumé + signaux faibles) → fiches de décision. S'appuie sur `tesla-arcanis-360` (Deep Research) pour l'enrichissement et sur `premortem` pour le stress-test des conclusions.
## MT-2 · Akasha Weave — moteur cognitif externe
**Branche :** Intelligence Stratégique · **Statut visé :** Draft

Le système le plus ambitieux : transformer des flux d'informations brutes en **intelligence stratégique exploitable**, en surcouche de TASLB/Alexandria.
À cadrer par un **chantier SGC dédié** (cahier des charges 11 sections) avant toute ligne de code. Dépend de MT-1 (T.A.H.O nourrit Akasha).
## MT-3 · Couche de distribution & présence publique
**Branche :** Performance Humaine · **Principe :** Mahonheim First
*   **`tesla-reddit-commander`** : opérationnaliser la publication gouvernée (déjà dans la table de délégation).
*   **`tesla-writing-skills`** : industrialiser la production de contenus publics (manifestes, articles, field-notes) avec TDD de compétences.
*   Transformer chaque runbook stabilisé en **field-note publique** — la signature de ton positionnement (MY\_BRANDING).
## MT-4 · Orchestration distribuée & délestage cloud (Jules)
**Branche :** Opérations IA Gouvernées · **Principe :** Simplicity First

Concrétiser le routeur d'orchestration multi-agents (Projet #13) : déporter le calcul UI/HTML lourd vers **Jules** pour préserver la bande passante de MIDGARD.
Livrable : contrat d'interface Jules ↔ Antigravity + boucle de validation asynchrone (self-healing, délestage sémantique).
## MT-5 · Packaging & Plugins — de l'interne au réutilisable
**Branche :** Opérations IA Gouvernées
*   **Alexandria-as-MCP** : exposer le second cerveau (recherche hybride RRF) comme serveur MCP réutilisable, versionné, documenté.
*   **Memory-as-MCP** : exposer la MLT (graphe sémantique) comme interface stable.
*   **Pipeline** **`llama.cpp`** : opérationnaliser l'usage validé (packaging/quantification GGUF pour publications externes) — **sans jamais faire d'inférence locale** (prohibition entérinée, Projet #14).
## MT-6 · Modèle de maturité & première offre
**Branche :** Performance Humaine + toutes · **Principe :** Proof First

Installer un **tableau de maturité** de tout l'écosystème sur le cycle FORCE\_TOOLING (combien de skills en Stable vs Experimental). C'est le prérequis avant de vendre.
Puis cadrer la **première offre monétisable** (MY\_COMPANY §15-16) : le plus mûr est _« Mise en place de workflows IA gouvernés »_ — car c'est exactement ce que l'écosystème Tesla démontre déjà.

* * *
# 🗺️ Synthèse séquentielle

| Horizon | Priorité | Chantier | Branche VC | Statut cible |
| ---| ---| ---| ---| --- |
| Court | P0 | CT-1 Finir chantiers en vol | Ops IA | Validated |
| Court | P0 | CT-2 Vigilum Gateway V2.1 | Ops IA | Stable |
| Court | P1 | CT-3 Sync Source de Vérité | Intel. Strat. | Stable |
| Court | P1 | CT-4 Policy Registry | Ops IA | Validated |
| Court | P2 | CT-5 MVP GitHub vitrine | Perf. Humaine | Stable |
| Court | P2 | CT-6 Argus Core | Intel. Strat. | Experimental |
| Moyen | P1 | MT-1 T.A.H.O Nexus | Intel. Strat. | Experimental |
| Moyen | P2 | MT-2 Akasha Weave | Intel. Strat. | Draft |
| Moyen | P1 | MT-3 Distribution publique | Perf. Humaine | Experimental |
| Moyen | P2 | MT-4 Orchestration + Jules | Ops IA | Experimental |
| Moyen | P2 | MT-5 Packaging MCP / llama.cpp | Ops IA | Validated |
| Moyen | P1 | MT-6 Maturité & 1ère offre | Toutes | Validated |

* * *
## Distinction de rigueur (SOUL §5)
*   **Faits vérifiés :** l'inventaire, les doctrines et les statuts proviennent de tes fichiers canoniques (`liste_projets_antigravity_BASE`, `AGENTS`, `SOUL`, `FORCE_TOOLING`, `MY_COMPANY`, `shadow-targeting-method`).
*   **Raisonnement :** la priorisation (consolider avant d'étendre) découle de la Doctrine VC #3 et du cycle de vie FORCE\_TOOLING §6.
*   **Hypothèses :** les horizons temporels (0-3 / 3-9 mois) et les statuts cibles sont proposés, à valider par toi. `tesla-curator-prime`, `tesla-code-auditor`, `tesla-loop-orchestrator` sont supposés non consolidés (référencés dans AGENTS mais absents de l'inventaire visible) — à confirmer.

* * *
_Feuille de route en statut Draft. Aucune capacité n'a été créée, modifiée ou publiée. La main te revient pour arbitrage et ouverture des chantiers SGC correspondants._
`MAIN_RENDUE_A_MAHONHEIM=1`