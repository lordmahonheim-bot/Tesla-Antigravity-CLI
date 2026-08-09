---
type: premortem
tags: [securite/premortem, statut/valide]
source: "[[plan_intervention_tesla_arcanis-Updated.md]]"
date: 2026-06-30
version: 1.0
---

# 🕵️ RAPPORT DE DIAGNOSTIC PREMORTEM — TESLA ARCANIS
**Date :** 2026-06-30  
**Auteur :** Premortem Risk Analyst (Sous-Agent Tesla)  
**Destinataire :** Lord Mahonheim (Abdellah MOUHTAJ)  
**Postulat de départ :** Le projet Tesla Arcanis a lamentablement échoué après 3 mois d'utilisation.

---

## 1. Résumé Exécutif

Après une simulation prospective, le système Tesla Arcanis a été déclaré inopérant à la date du **2026-09-30**. 

L'échec ne provient pas de la qualité de ses analyses, mais d'une **asphyxie opérationnelle** :
1. **Asphyxie matérielle (RAM/CPU) :** plantages répétés de MIDGARD (8 Go RAM) lors des transcriptions locales (`whisper.cpp`) ou des requêtes vectorielles (ChromaDB en CPU-only).
2. **Asphyxie budgétaire (Tokens) :** dérive inflationniste des contextes d'enquête due à des boucles de validation infinies, rendant l'agent inutilisable au quotidien.
3. **Obsolescence des wrappers :** les scripts de scraping Webwright ont cassé suite aux changements de structures et aux barrières anti-bots des sites cibles.

---

## 2. Analyse de Substance (Les 3 Rôles)

### 🏛️ Rôle A : L'Avocat du Diable (Causes Root-Cause)

Le désastre s'explique par les failles techniques et physiques suivantes :

- **OOM (Out Of Memory) Crashs :** `whisper.cpp` avec le modèle `small` a saturé la RAM disponible de MIDGARD lorsqu'il tournait en parallèle avec d'autres services ou que la mémoire de swap était épuisée.
- **Boucles d'Auto-Correction Infinies :** À l'Étape 4 (Comité de lecture), l'agent s'est retrouvé bloqué dans des boucles de relecture infinies, ré-analysant continuellement ses propres rapports pour des détails mineurs, consommant des centaines de milliers de tokens sans produire de livrable.
- **Request-Review Bloquant :** Le protocole `request-review` asymétrique a été mal implémenté : l'agent a demandé des validations manuelles pour des écritures de fichiers temporaires ou des logs intermédiaires, provoquant de nombreuses interruptions de travail pour Lord Mahonheim.

### 🔍 Rôle B : L'Inspecteur des Angles Morts (Hypothèses Invisibles)

Le plan d'intervention reposait sur des suppositions erronées ou non testées :

- **L'illusion du CPU-Only rapide :** Supposer que le calcul vectoriel (ChromaDB local) et la transcription audio locale resteraient fluides sur MIDGARD sans accélération matérielle GPU.
- **La permanence des API d'Antigravity :** Supposer que l'API de sous-agents (`define_subagent` et `invoke_subagent`) resterait rétrocompatible au fil des mises à jour du CLI sans maintenance.
- **La docilité du Web :** Supposer que Webwright (Playwright) pourrait ingérer des pages complexes protégées par Cloudflare ou des captchas sans intervention humaine ni proxy.

### 📡 Rôle C : La Vigie des Signaux Faibles (Indicateurs Précurseurs)

Plusieurs alertes silencieuses ont annoncé la dérive bien avant la panne générale :

- **Dégradation du temps de réponse :** Le temps d'initialisation de l'agent Arcanis est passé de 5 secondes à plus de 45 secondes.
- **Mise sous pression de la RAM :** Des messages de type `Out of memory: Kill process` ou des ralentissements notables du système MIDGARD lors des exécutions d'investigation.
- **Troncatures de contexte silencieuses :** La signature d'Arcanis a commencé à disparaître de la fin des rapports car l'historique de conversation dépassait la fenêtre de contexte maximale du modèle.
- **Avertissements Pyright (LSP) ignorés** lors des modifications des scripts d'infrastructure (`search_router.py`), créant des bugs d'import silencieux.

---

## 3. Contre-Mesures et Verrous de Résilience

Pour immuniser le Plan d'Intervention Ultime contre ces failles, les verrous techniques suivants sont intégrés :

| Risque identifié | Niveau | Contre-mesure intégrée |
|---|---|---|
| **Saturation RAM (OOM)** | 🔴 Élevé | - Limitation de `whisper.cpp` à l'utilisation exclusive du modèle `base` (ou `tiny`) au lieu de `small`.  <br>- Interdiction stricte de charger en mémoire brute des fichiers > 500 Ko (utilisation de chunks). |
| **Boucles de relecture infinies** | 🟡 Moyen | - Limitation stricte des itérations d'auto-critique à **2 passes maximum**.  <br>- Si le rapport n'est pas validé après la 2ème passe, Arcanis doit s'arrêter et lister les points de divergence sous forme de "Questions ouvertes". |
| **Obsolescence de Webwright** | 🟡 Moyen | - Fallback automatique vers `read_url_content` (natif AGY) si Playwright échoue.  <br>- Journalisation propre des pannes de scraping dans `logs/webwright_errors.log`. |
| **Fragmentation de l'écosystème** | 🟡 Moyen | - Tesla Arcanis est défini comme un **profil spécialisé de Tesla** (et non un agent autonome). Il utilise le même répertoire de configuration `.agents/`. |

---
*Rapport Premortem validé par la cellule de sécurité Bifrost.*

Signé / Fait par : Tesla sur Antigravity CLI  
Main rendue à Mahonheim
