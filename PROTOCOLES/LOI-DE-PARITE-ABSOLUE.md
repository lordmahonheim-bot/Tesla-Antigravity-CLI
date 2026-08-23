# PROTOCOLE CANONIQUE — LOI DE PARITÉ ABSOLUE

**Version:** 2.0.0
**Statut:** Canonical
**Ancrage:** Gravure sur Marbre — Phase 3.5 (Audit Post-Mission)
**Écosystème:** Tesla / Bifrost / MIDGARD
**Doctrine:** Vigilum Codex
**Principe cardinal:** **No Proof, No Parity, No Publish.**

---

## 0. Objet

La Loi de Parité Absolue est un **audit post-mission déterministe** de cohérence globale. Elle garantit que tout ajout, déploiement, modification ou retrait d'un composant de l'infrastructure opérationnelle — Skill, Agent, MCP, Script, Outil, Capability — trouve son reflet **synchrone, exact et bidirectionnel** dans l'ensemble de l'architecture canonique.

> **Postulat de double existence :**
> - Capacité **déployée mais absente de la mémoire** → **Amnésie** (l'orchestration devient aveugle aux cycles suivants).
> - Capacité **mémorisée mais absente de l'exécution** → **Fantôme** (la mémoire croit en une ressource inexistante).
> - L'un comme l'autre sont des **Context Collapse** et valent **BLOCK**.

### Périmètre d'application

Ce protocole s'applique à la toute fin de chaque mission ayant produit une mutation d'un composant Tesla, dans la Phase 3.5 du protocole Gravure sur Marbre. Il constitue l'ultime verrou de cohérence avant la publication (Phase 4) ou le scellement (Phase 7).

Il ne doit **pas** être utilisé comme substitut à la validation technique (Phase 2) ni à l'assimilation canonique (Phase 3.1-3.4).

---

## 1. Principes non négociables

| # | Principe | Définition |
|---|---|---|
| P1 | **No Proof, No Pass** | Une occurrence textuelle, un code de retour nul, un message de succès ou une affirmation d'agent ne constituent jamais, seuls, une preuve de parité. |
| P2 | **Producer ≠ Validator** | L'agent qui produit une mutation ne peut pas être considéré comme preuve indépendante de cette même mutation. L'Orchestrateur Principal exécute l'audit lui-même. |
| P3 | **Unknown ≠ Pass** | Un état indéterminé n'est jamais assimilé à un succès. |
| P4 | **L'absence d'erreur n'est pas le succès** | `exit 0` d'un grep multi-fichiers ou `git push` ne constituent pas une preuve. |
| P5 | **No Self-Evidence** | Le même acteur ne doit jamais : modifier + fabriquer la preuve + se déclarer validateur. |
| P6 | **Parité bidirectionnelle** | L'audit vérifie dans les deux sens : Exécution → Mémoire (anti-amnésie) ET Mémoire → Exécution (anti-fantôme). |
| P7 | **Fail Closed** | Toute ambiguïté provoque un arrêt contrôlé. |

---

## 2. Déclencheur et Timing

### Condition d'activation

Le protocole s'active **EXCLUSIVEMENT** lorsque :

1. Tous les sous-agents d'élite assignés ont émis un Checkpoint `status: SUCCESS` ou `PARTIAL` (et non une simple affirmation orale) ;
2. La Phase 3 (Assimilation — Matrice d'Impact + Routage + Réconciliation) est `PASS` ;
3. Le `BASELINE_FINGERPRINT` capturé en début de mission a été re-vérifié (**Stale State Check**). Si l'état a bougé hors contrat → `STALE_STATE` → BLOCK + RELOAD avant même l'audit.

### Séquence interdite

Exécuter cet audit sur un état intermédiaire (avant la confirmation des checkpoints) produit une fausse parité. Cette exécution prématurée est une violation de gouvernance.

### Sortie de cette Phase

Un audit `PASS` autorise exclusivement la Phase 4 (Public Staging) ou la Phase 7 (Seal) selon le `closure_type` du contrat. Tout autre enchaînement est interdit.

---

## 3. Périmètre Cible et Matrice d'Impact

L'audit croise obligatoirement deux strates. Le sous-ensemble exact de fichiers à inspecter est déterminé par le **type canonique du composant** via la matrice ci-dessous. Un fichier non applicable doit être marqué **N/A avec justification** dans l'Evidence Ledger.

### Strate 1 — Registres d'Exécution (Manifestes)

| Clé | Fichier (sous `$TESLA_ROOT`) | Rôle |
|-----|------------------------------|------|
| `TESLA_JSON` | `.agents/TESLA.json` | Registre de déclaration des capacités |
| `SETTINGS_JSON` | `.agents/settings.json` | Permissions et outils |
| `AGENTS_MD` | `.agents/AGENTS.md` | Table de délégation et de routage |
| `ENGINE_MD` | `memory/ENGINE.md` | Moteurs cognitifs et organes sensoriels |
| `FORCE_TOOLING_MD` | `memory/FORCE_TOOLING.md` | Policy Registry et Lifecycle des capacités |

### Strate 2 — Conscience Mémorielle (Journaux)

| Clé | Fichier (sous `$TESLA_ROOT/memory`) | Rôle |
|-----|-------------------------------------|------|
| `PROJECT_STATE` | `PROJECT_STATE.md` | Ancrage à court terme |
| `SESSION_LOG` | `SESSION_LOG.md` | Historique chronologique |
| `PROJECTS_BASE` | `liste_projets_antigravity_BASE.md` | Taxonomie canonique |

### Matrice de couplage obligatoire

| Type de composant | Strate 1 (Exécution) | Strate 2 (Mémoire) |
|-------------------|----------------------|---------------------|
| **Skill** | `TESLA_JSON` + `SETTINGS_JSON` + `AGENTS_MD` (si routé) | `PROJECT_STATE` + `SESSION_LOG` + `PROJECTS_BASE` |
| **Agent / Sous-agent** | `TESLA_JSON` + `AGENTS_MD` + `SETTINGS_JSON` | `PROJECT_STATE` + `SESSION_LOG` + `PROJECTS_BASE` |
| **Organe sensoriel / Moteur cognitif** | `ENGINE_MD` + `FORCE_TOOLING_MD` + `TESLA_JSON` | `PROJECT_STATE` + `SESSION_LOG` |
| **MCP Server** | `SETTINGS_JSON` + `TESLA_JSON` + `AGENTS_MD` | `PROJECT_STATE` + `SESSION_LOG` |
| **Script / Capability** | `TESLA_JSON` (si enregistré) + `SETTINGS_JSON` | `SESSION_LOG` + `PROJECT_STATE` (si récurrent) |
| **Modification architecturale** | Tous les fichiers Strate 1 (inspection complète) | `PROJECT_STATE` + `SESSION_LOG` + `PROJECTS_BASE` |
| **Fix / Maintenance** | `TESLA_JSON` / `SETTINGS_JSON` (fichiers touchés) | `SESSION_LOG` (obligatoire) + `PROJECT_STATE` (si état change) |

> **Règle absolue :** `PROJECT_STATE` est TOUJOURS une cible obligatoire, sans exception, quelle que soit la nature du déploiement.
> 
> Tout pilier de la Gate 5 non listé dans le couplage courant (ex: `SOUL.md`, `knowledge_graph.json`, `Alexandria DB`, `TELEGRAM_SYNAPSE.md`, `OUTPUTS/`, `Skills Registry`) est par défaut considéré comme **N/A** et doit être explicitement documenté avec sa justification dans l'Evidence Ledger pour respecter l'exhaustivité des 14 piliers. Une case oubliée = BLOCK automatique.

---

## 4. Niveaux de Vérification

Chaque cible est vérifiée selon quatre niveaux progressifs. Un niveau inférieur ne peut pas remplacer un niveau supérieur lorsqu'il est requis.

| Niveau | Nom | Description | Exemple |
|--------|-----|-------------|---------|
| 1 | **PRESENCE** | L'artefact attendu existe physiquement | `test -f $fichier` |
| 2 | **STRUCTURE** | Les structures et champs obligatoires existent | `jq -e .` pour les JSON |
| 3 | **SEMANTICS** | Les valeurs correspondent à l'identifiant canonique exact | `grep -F -w` (Markdown), `jq --arg id` (JSON) |
| 4 | **STATE** | L'état déclaré correspond à l'état opérationnel réel | Vérification croisée des valeurs |

---

## 5. Mécanisme de Vérification Déterministe

### 5.1 Pré-condition : Vérification des Chemins

Avant toute inspection, l'Orchestrateur vérifie que les fichiers cibles sont accessibles à leur emplacement déclaré. Un fichier absent déclenche un `MISSING` → BLOCK immédiat, et non un faux PASS par chemin manqué silencieux.

```bash
for F in "${FICHIERS_CIBLES[@]}"; do
  [ -f "$F" ] || echo "FICHIER INTROUVABLE : $F — BLOCK"
done
```

`TESLA_ROOT` est résolu dynamiquement selon la cascade suivante (première correspondance retenue) :

1. Variable d'environnement `$TESLA_ROOT` si définie et pointant vers un répertoire existant.
2. Argument `--root` passé explicitement au script.
3. Répertoire courant (`$PWD`) si celui-ci contient les sous-dossiers `.agents/` et `memory/`.
4. `git rev-parse --show-toplevel` si le CWD se trouve dans un dépôt Git contenant `.agents/`.
5. **Échec** (exit 66) si aucune méthode ne résout un chemin valide.

### 5.2 Capture du State Fingerprint

```bash
PARITY_FINGERPRINT=$(cat \
  "$TESLA_ROOT/memory/PROJECT_STATE.md" \
  "$TESLA_ROOT/memory/SESSION_LOG.md" \
  "$TESLA_ROOT/memory/liste_projets_antigravity_BASE.md" \
  | sha256sum | cut -d' ' -f1)
```

Ce fingerprint est comparé au `BASELINE_FINGERPRINT` de début de mission. Divergence = `STALE_STATE` (exit 2).

### 5.3 Vérification par Fichier (Obligation Absolue)

**INTERDICTION FORMELLE :** L'usage d'un `grep` multi-fichiers unique comme preuve de parité est prohibé. Il retourne une sortie agrégée (exit 0 si un seul fichier matche) qui ne distingue pas les fichiers muets des fichiers actifs. La vérification **DOIT** être exécutée **fichier par fichier**.

#### Identifiant canonique

Tout composant est audité sous son identifiant canonique exact (ex : `tesla-master-code`, `mcp-telegram`), passé en argument. La correspondance est **littérale** :

- **Markdown :** `grep -F -w -- "$ID" "$fichier"` (mot entier, pas d'interprétation regex)
- **JSON :** `jq -e --arg id "$ID" '<chemin-structurel>[] | select(.id == $id)'` avec repli `grep -F -w`

> `-i` est **proscrit** : il fait matcher `bar` dans `embarras`.
> `-E` est **proscrit** sur un identifiant non validé : `.`, `*`, `[` deviennent des métacaractères.

#### Pseudo-code de référence

Pour **chaque** fichier cible `f` de la matrice :
```bash
test -f "$f" || { verdict "MISSING" "$f"; continue; }
case "$f" in
  *.json) jq -e . "$f" >/dev/null || { verdict "INVALID_JSON" "$f"; continue; } ;;
esac
grep -F -w -q -- "$ID" "$f" && verdict "PASS" "$f" || verdict "BLOCKED" "$f"
```

Le code de sortie global est `0` **si et seulement si** chaque fichier obligatoire a reçu le verdict `PASS`. Tout `MISSING`, `INVALID_JSON` ou `BLOCKED` impose un code non nul.

### 5.4 Détection bidirectionnelle (anti-fantôme)

**Sens 1 — Exécution → Mémoire (anti-amnésie) :**
Chaque ID enregistré dans `TESLA_JSON` doit apparaître dans la strate mémoire. Ce sens est couvert par le pseudo-code de §5.3.

**Sens 2 — Mémoire → Exécution (anti-fantôme) :**
Tout ID répertorié dans `PROJECT_STATE.md` / `PROJECTS_BASE.md` doit exister dans `TESLA_JSON` (à l'exception explicite des éléments marqués `[ARCHIVÉ]` / `[DÉPRÉCIÉ]`).

Pseudo-code du sens inverse :
```bash
# Extraire les IDs déclarés dans TESLA.json (structure réelle)
declared_ids=$(jq -r '.modules.registered[]?' "$TESLA_ROOT/.agents/TESLA.json" | sort -u)

# Pour chaque fichier mémoriel, vérifier que l'ID audité n'est pas un fantôme
for mem in memory/PROJECT_STATE.md memory/liste_projets_antigravity_BASE.md; do
  [ -f "$TESLA_ROOT/$mem" ] || continue
  if grep -F -w -q -- "$ID" "$TESLA_ROOT/$mem"; then
    # Présent en mémoire : vérifier qu'il existe aussi dans les manifestes
    if ! echo "$declared_ids" | grep -Fxq "$ID"; then
      # Pas dans TESLA.json : vérifier si $ID lui-même est explicitement archivé/déprécié
      if ! grep -F -w -- "$ID" "$TESLA_ROOT/$mem" | grep -E -q -w '(\[ARCHIVÉ\]|\[DÉPRÉCIÉ\]|deprecated|retired)'; then
        verdict "GHOST" "$mem"  # Fantôme détecté → BLOCK
      fi
    fi
  fi
done
```

> Un fantôme détecté (`GHOST`) vaut `BLOCK` au même titre qu'un fichier muet.

---

## 6. Matrice de Décision (Fail-Closed)

La sortie console et l'Evidence Ledger sont les **uniques juges**.

| Statut | Condition | Action |
|--------|-----------|--------|
| 🟢 **PASS** | `exit 0` — Toutes les cibles obligatoires retournent ≥1 occurrence ; JSON valides ; 0 orphelin ; 0 fantôme | Parité prouvée. Générer l'Evidence Ledger. Autoriser Phase 4/7. |
| 🟡 **PARTIAL** | Piliers optionnels muets, documentés N/A avec justification. Cœur obligatoire PASS. | Documenter les N/A dans le Ledger. Continuer sous supervision. |
| 🔴 **BLOCKED** | `exit 1` — ≥1 pilier obligatoire retourne 0 occurrence, fichier absent ou JSON invalide | Arrêt immédiat. Lancer Self-Healing. Publication interdite. |
| ⚫ **STALE_STATE** | `exit 2` — Le Fingerprint a changé hors contrat | BLOCK + RELOAD cognitif avant même l'audit. |
| ⚪ **UNKNOWN** | État non observable | Ne jamais assimiler à PASS. |
| 🔵 **UNVERIFIED** | Mutation a eu lieu mais vérification non obtenue | Parité non prouvable → BLOCKED. |

**Règle de Priorité Monotone :** Un BLOCK ne peut être annulé par aucune affirmation verbale d'un sous-agent. La seule annulation valide est un nouveau `exit 0` du script.

---

## 7. Protocole de Self-Healing (Circuit-Breaker : max 3 itérations)

### Condition d'entrée

Activé si et seulement si le script retourne un code non nul.

### Classification des corrections

| Classe | Exemples | Règle |
|--------|----------|-------|
| **A — Auto-correction sûre** | `SESSION_LOG`, `PROJECT_STATE`, index documentaire | Possible automatiquement si : impact low, diff déterministe, rollback disponible |
| **B — Correction contrôlée** | `TESLA.json`, `AGENTS.md` | Proposition + validation du mécanisme de gouvernance |
| **C — Correction interdite** | `settings.json` (permissions), routage critique, sécurité | **Escalade immédiate** à Lord Mahonheim. Ne PAS consommer de retry. |

> **Règle d'escalade Classe C :** Une correction classée C identifiée à n'importe quelle itération (y compris la première) déclenche un BLOCK définitif **immédiat** et une escalade au Gatekeeper. Le compteur de retries (max 3) ne s'applique qu'aux corrections de Classe A et B. L'escalade Classe C est orthogonale au circuit-breaker.

### Séquence obligatoire par itération

**Itération N (max 3) :**

1. **Arrêt total.** Interdiction d'émettre la publication ou de déclarer le succès.
2. **Diagnostic.** Lire le rapport dans le Ledger. Identifier les lignes BLOCK. Ne corriger que les piliers défaillants listés.
3. **Classification.** Déterminer la classe (A/B/C) de la correction requise. Si C → BLOCK définitif.
4. **Correction atomique.** Appliquer l'action correctrice par type de pilier :

| Pilier défaillant | Action correctrice |
|-------------------|-------------------|
| `AGENTS.md` | Ajouter la ligne de routage dans la Table de Délégation |
| `TESLA.json` | Ajouter l'entrée dans `modules.registered` |
| `settings.json` | Inscrire la commande sur liste blanche (Classe C → validation humaine) |
| `liste_projets` | Ajouter l'entrée projet (pagination obligatoire sur fichier tronqué) |
| `PROJECT_STATE.md` | Mettre à jour l'ancre cognitive |
| `SESSION_LOG.md` | Ajouter l'entrée chronologique |

5. **Ré-Audit Complet Obligatoire.** Ré-exécuter l'intégralité du script (tous les fichiers de la matrice). Un audit partiel ciblant uniquement le fichier corrigé est **formellement interdit**.
6. **Validator Rule.** Le ré-audit est une relecture d'octets, pas une relecture d'intention.

### Circuit-Breaker

Si après **3 itérations complètes** le statut reste non nul :

1. Générer un rapport d'échec terminal dans `OUTPUTS/`.
2. Interrompre la mission.
3. Inscrire l'open-item dans `OUTPUTS/open_items_todo-Updated.md`.
4. Escalader à Lord Mahonheim avec le rapport et la liste exacte des piliers bloquants.

---

## 8. Evidence Ledger (Artéfact de Preuve Obligatoire)

Chaque exécution produit un artéfact physique horodaté dans `OUTPUTS/evidence/` :

```
OUTPUTS/evidence/parity_[MISSION_ID]_[YYYYMMDD-HHMMSS].json
```

### Format minimal

```json
{
  "protocol": "Loi-Parite-Absolue",
  "version": "2.0.0",
  "mission_id": "<MISSION_ID>",
  "component_id": "<identifiant canonique>",
  "component_type": "<Skill|Agent|MCP|Script|Modification>",
  "tesla_root": "<TESLA_ROOT>",
  "baseline_fingerprint": "sha256:...",
  "current_fingerprint": "sha256:...",
  "stale_state": false,
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "verdict_global": "PASS|BLOCKED|STALE_STATE",
  "exit_code": 0,
  "checks": [
    {"file": ".agents/TESLA.json", "verdict": "PASS", "sha256": "...", "matched_lines": 2},
    {"file": ".agents/AGENTS.md", "verdict": "PASS", "sha256": "...", "matched_lines": 1},
    {"file": "memory/PROJECT_STATE.md", "verdict": "PASS", "sha256": "...", "matched_lines": 1},
    {"file": "memory/SESSION_LOG.md", "verdict": "N/A", "note": "Non impacté par ce type"}
  ],
  "orphans": [],
  "ghosts": [],
  "self_heal_iterations": 0
}
```

Ce Ledger est archivé dans `OUTPUTS/evidence/` et alimente l'Evidence Chain de la Gravure sur Marbre.

---

## 9. Spécification du Script Validateur

> **STATUT :** Ce script n'est pas encore déployé physiquement sur MIDGARD. La présente section est une **spécification d'implémentation** à déléguer à `tesla-master-code` avant toute première exécution opérationnelle du protocole. Tant que le script n'est pas déployé, whitelisté dans `settings.json` et vérifié par `lsp_diagnostics`, l'Orchestrateur doit exécuter le pseudo-code de §5.3 et §5.4 manuellement dans le terminal.

Le script cible `scripts/audit_parite.sh` doit implémenter les exigences suivantes :

- Vérification **fichier par fichier** (pas de multi-fichiers)
- Correspondance littérale (`grep -F -w` ; `-i`/`-E` proscrits)
- Détection `MISSING` et `INVALID_JSON`
- Matrice d'Impact formelle par type (`Skill|Agent|MCP|Script|Modification|Organe`)
- Résolution dynamique de `TESLA_ROOT` (cascade §5.1)
- Fingerprint baseline et stale-state check
- Détection bidirectionnelle des orphelins et fantômes (`--strict-ghost`)
- Evidence Ledger JSON horodaté dans `OUTPUTS/evidence/`

### Exit Codes (Contrat de sortie)

| Code | Signification |
|------|---------------|
| `0` | PASS — chaque fichier obligatoire matche ; JSON valides |
| `1` | BLOCKED — un fichier obligatoire est muet/absent/invalide, ou fantôme détecté |
| `2` | STALE_STATE — fingerprint divergent (reload) |
| `64` | Erreur d'usage (arguments manquants / type inconnu) |
| `66` | `TESLA_ROOT` introuvable |
| `69` | Dépendance manquante (`jq`, `sha256sum`) |

### Interface d'invocation (cible)

```bash
scripts/audit_parite.sh \
  --id <identifiant-canonique> \
  --type <Skill|Agent|MCP|Script|Modification|Organe> \
  --root <TESLA_ROOT> \
  --mission <MISSION_ID> \
  --baseline "sha256:..."
```

> **Ce script est le VALIDATOR.** Il ne corrige rien. Le self-healing est la boucle appelante (l'Orchestrateur). Le script existe exclusivement pour produire un `exit code` déterministe et un Evidence Ledger JSON.

---

## 10. Interdictions Formelles

| # | Interdiction |
|---|-------------|
| I-01 | Déclarer le succès sans `exit 0` du script |
| I-02 | Interpréter visuellement la console sans exit code |
| I-03 | Exécuter un `grep` multi-fichiers unique comme preuve de parité globale |
| I-04 | Accepter l'affirmation d'un sous-agent comme preuve de parité |
| I-05 | Omettre un pilier obligatoire sans justification N/A documentée |
| I-06 | Dépasser 3 itérations de Self-Healing sans escalade à Lord Mahonheim |
| I-07 | Exécuter cet audit avant la confirmation des checkpoints de tous les sous-agents |
| I-08 | Utiliser `-i` ou `-E` sur un identifiant canonique |
| I-09 | Exécuter un ré-audit partiel (pilier unique) au lieu du script complet |
| I-10 | Fabriquer la preuve après coup (corriger puis se déclarer validateur indépendant) |

---

## 11. Formules Canoniques

> **L'existence n'est pas la preuve.**

> **La présence n'est pas la parité.**

> **La déclaration n'est pas l'état réel.**

> **L'absence d'erreur n'est pas le succès.**

> **Une mutation non relue est UNVERIFIED.**

> **Une preuve manquante interdit PASS.**

> **No Proof, No Parity, No Publish.**

---

## 12. Ancrage dans l'Architecture Canonique

| Document | Relation |
|----------|----------|
| `memory/PROTOCOLES/GRAVURE-SUR-MARBRE.md` | Ce protocole est la **Phase 3.5** de la Gravure sur Marbre (protocole canonique sanctuarisé) — entre l'Assimilation (3.1-3.4) et le Public Staging (4). *(STATUT : À créer et à inscrire dans AGENTS.md §14).* |
| Le Conducteur Absolu v3.2.1 | Implémentation opérationnelle de Gate 5 (Canonical Integration). |
| GEMINI.md Règle 4 | Déclare l'absorption de l'Harmonisation dans la Phase 3.2 de la Gravure. |
| GEMINI.md Règle 18 | Déclare l'absorption de l'Assimilation/Routage dans la Phase 3.3 de la Gravure. Définit les routes correctrices par type de composant. |
| GEMINI.md Règle 16 | Impose la production de l'artéfact OUTPUTS/. |
| AGENTS.md §14 | Définit les Piliers de la Source de Vérité. |
| AGENTS.md §13 | Destination des escalades en cas d'échec terminal. |

---

## 13. Critère ultime

Un composant Tesla n'est **pas** en parité parce que :

- l'agent affirme avoir mis à jour les fichiers ;
- `grep` retourne des lignes ;
- `exit 0` est observé sur un grep multi-fichiers ;
- les fichiers JSON existent ;
- `git status` est propre.

Il est en parité **uniquement** lorsque :

```text
EXPECTED STATE == OBSERVED STATE
  pour CHAQUE fichier obligatoire de la Matrice
  vérifié fichier par fichier
  avec correspondance littérale prouvée
  JSON structurellement valides
  0 orphelin + 0 fantôme
  fingerprint stable
  Evidence Ledger généré et archivé
  = exit 0
```

> ## NO PROOF, NO PARITY, NO PUBLISH.
