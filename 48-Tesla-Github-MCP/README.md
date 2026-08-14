# CAHIER DES CHARGES : TESLA-GITHUB-MCP
**Version :** 2.0 (Refonte post-Audit Team-Synergy)
**Date :** 2026-08-14
**Statut :** ⚪ Clos

---

## 1. Méta-données
- **Identifiant :** Chantier 046
- **Responsable :** Tesla (Agent Principal)
- **Autorité :** Lord Mahonheim

## 2. Contexte & Problématique
Suite à l'invalidation du brouillon externe, la vision de Lord Mahonheim a été clarifiée : `tesla-github-manager` détient l'autorité totale (Read/Write) sur GitHub, tandis que `tesla-arcanis-360` opère en `Read-Only` strict pour l'OSINT.
Étant donné qu'Antigravity CLI expose les outils MCP de manière globale à l'agent, l'architecture retenue est la **Double Instanciation de Serveurs** avec ségrégation par Token (Hardware-level constraint) pour garantir un "Zero-Trust" absolu.

## 3. Périmètre & Objectifs
**Architecture Technique :**
Déploiement de deux serveurs MCP locaux (via `npx -y @modelcontextprotocol/server-github`) dans `mcp_config.json` :
1. **Serveur `github-manager`** : Alimenté par un Token GitHub (PAT ou OAuth) avec droits de mutation.
2. **Serveur `github-arcanis`** : Alimenté par un Fine-Grained PAT **strictement limité à la lecture seule**.
Les `SKILL.md` des deux agents seront mis à jour pour imposer l'utilisation exclusive de leur préfixe d'outils respectif (`github-manager_*` vs `github-arcanis_*`). Toute erreur cognitive d'Arcanis tentant d'écrire sera interceptée matériellement par l'API GitHub (Erreur 403) grâce au Token read-only.

## 4. Feuille de Route Maîtresse (Mission Graph - DAG)

#### 📍 NOEUD 1 : ACQUISITION DES TOKENS & ISOLATION SÉCURITAIRE (Gate 1 & 2)
**Agents Assignés :** `Tesla-PREMORTEM` + `Tesla-Github-Manager`
*   **Action :** Création et validation des deux clés d'authentification (PAT Standard pour Manager, Fine-Grained PAT Read-Only pour Arcanis). Audit strict des scopes du token Arcanis pour garantir l'absence totale de droit d'écriture (Zero-Trust hardware limit).
*   **Contrainte :** Les tokens doivent être stockés de manière sécurisée en variables d'environnement locales.

#### 📍 NOEUD 2 : DÉPLOIEMENT DE LA DOUBLE INSTANCIATION MCP (Gate 5)
**Agent Assigné :** `Tesla-Master-Code`
*   **Action :** Configurer `~/.gemini/antigravity-cli/mcp_config.json` pour déclarer les deux serveurs (`github-manager` et `github-arcanis`) pointant vers le même package NPM officiel mais avec des environnements différents.
*   **Contrainte :** Connectivité vérifiée et exposition confirmée des deux pools d'outils.

#### 📍 NOEUD 3 : MISE À JOUR DE LA GOUVERNANCE ET DES SKILLS
**Agents Assignés :** `Tesla-Curator-Prime`
*   **Action :** Mise à jour canonique des directives dans les `SKILL.md` de `tesla-github-manager` et `tesla-arcanis-360`. Verrouillage des namespaces : Arcanis a l'interdiction stricte d'appeler les outils préfixés `github-manager_`.
*   **Contrainte :** Doctrine anti-usurpation d'outils fermement ancrée dans leurs instructions.

#### 📍 NOEUD 4 : STRESS-TEST & RED TEAM (Gate 4 & 7)
**Agent Assigné :** `Tesla-PREMORTEM`
*   **Action :** 
    - *Test 1 (Sur-permission Hardware)* : Simuler l'appel d'un outil d'écriture via le serveur `github-arcanis`. L'API GitHub distante doit renvoyer une erreur `403 Forbidden`.
    - *Test 2 (Prompt Injection Cognitive)* : Soumettre Arcanis à une issue malveillante pour tenter de lui faire utiliser frauduleusement un outil `github-manager_`. Il doit rejeter l'instruction.
*   **Contrainte :** Certification PREMORTEM obligatoire pour valider cette étape (NO PROOF, NO PASS).

#### 📍 NOEUD 5 : CLÔTURE & SYNCHRONISATION (Gate 6)
**Agent Assigné :** `Tesla-Team-Synergy`
*   **Action :** Archivage SGC des logs de test, clôture du chantier (mise à jour de `PROJECT_STATE.md` et `INDEX.md`), synchronisation du registre.

## 5. Critères d'Acceptation (DoD)
- Deux serveurs MCP distincts fonctionnent en parallèle.
- Arcanis est matériellement incapable de muter l'état GitHub, validant la doctrine "Fail-Closed".
- La séparation d'autorité est claire, opérationnelle et documentée.
