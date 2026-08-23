# PROTOCOLE CANONIQUE — GRAVURE SUR MARBRE

**Version:** 2.0.0
**Statut:** Canonical
**Écosystème:** Tesla / Bifrost
**Doctrine:** Vigilum Codex
**Principe cardinal:** **NO PROOF, NO MARBLE.**

---

## 0. Objet

Le protocole **Gravure sur Marbre** régit la transformation d'un accomplissement Tesla en état :

- clôturé ;
- validé indépendamment ;
- assimilé dans l'architecture canonique ;
- harmonisé avec la mémoire ;
- documenté publiquement ;
- autorisé par Lord Mahonheim ;
- propagé à distance ;
- vérifié (parité locale/distante) ;
- puis définitivement scellé.

> **Gravure sur Marbre est le protocole fail-closed qui transforme un accomplissement validé en état canonique, traçable, réversible jusqu'au scellement, publiable sous autorisation et vérifié indépendamment à distance.**

### Périmètre d'application

Le protocole s'applique lorsqu'un chantier ou une capacité :

1. atteint sa définition de terminé ;
2. doit être inscrit dans la mémoire institutionnelle de Tesla ;
3. modifie le socle canonique ;
4. produit un MVP ou un artefact public ;
5. doit être publié ou mis à jour sur GitHub ;
6. remplace ou déprécie un composant existant ;
7. nécessite une preuve finale de cohérence locale et distante.

Il ne doit **pas** être utilisé pour transformer une intention, une proposition ou une hypothèse en fait canonique.

---

## 1. Principes non négociables

| # | Principe | Définition |
|---|---|---|
| P1 | **No Proof, No Pass** | Aucune transition d'état sans preuve exploitable. |
| P2 | **Producer ≠ Validator** | L'agent qui produit ne valide pas seul. |
| P3 | **Unknown ≠ Pass** | Un état inconnu n'est jamais un succès. |
| P4 | **Authorization ≠ Intent** | Un prompt ou une capacité technique ne constitue pas une autorisation. |
| P5 | **Remote State ≠ Local Assumption** | L'état local ne prouve jamais à lui seul l'état distant. |
| P6 | **No Canonical Propagation Without Admission Evidence** | Aucune écriture canonique avant vérification et admission. |
| P7 | **No Silent Deletion** | Aucune information de gouvernance supprimée silencieusement. |
| P8 | **Fail Closed** | Toute ambiguïté provoque un arrêt contrôlé. |
| P9 | **Mahonheim garde le contrôle** | Les mutations majeures et publications restent soumises au checkpoint humain. |
| P10 | **AGENTS délègue, il ne réimplémente pas** | L'orchestrateur route et surveille, il n'exécute pas à la place des agents spécialisés. |

---

## 2. Machine d'état

### Parcours nominal

```text
CLOSE_REQUESTED
       |
       v
PREFLIGHT_PASS ──────── (Autorité + Portée + Baseline)
       |
       v
VERIFIED_LOCAL ──────── (DoD + Validation Indépendante)
       |
       v
INTEGRATED_LOCAL ────── (Assimilation Canonique + Documentation)
       |
       ├──────────────── ARCHIVED_LOCAL_ONLY  (si aucune publication requise)
       v
READY_FOR_REMOTE ────── (Staging Public + Audit Post-Mission)
       |
       v
AWAITING_AUTHORIZATION ─ (Biological Gate Mahonheim)
       |
       v
PUBLISHED ───────────── (Push + Relecture SHA Distant)
       |
       v
REMOTE_VERIFIED ─────── (Parité Prouvée)
       |
       v
SEALED ──────────────── (Marble Certificate + Archivage SGC)
```

### États exceptionnels

| État | Signification |
|---|---|
| BLOCKED | Précondition, preuve ou capacité manquante. |
| FAILED | Non-conformité démontrée. |
| UNKNOWN | État réel non établi. **Jamais** interprété comme succès. |
| ROLLED_BACK | Mutations annulées après échec ou anomalie. |

### Règle de transition

```text
STATE → GATE → EVIDENCE → DECISION → NEXT STATE
```

> **CAUTION :** Un état aval ne peut jamais effacer un FAIL, BLOCKED ou UNKNOWN amont. Une reprise crée une nouvelle preuve et reprend au dernier checkpoint sain.

---

## 3. Classification des décisions

| Décision | Signification |
|---|---|
| PASS | Tous les critères sont satisfaits et prouvés. |
| FAIL | Le contrôle a démontré une non-conformité. |
| BLOCKED | La transition ne peut pas être autorisée. |
| UNKNOWN | L'état réel ne peut pas être établi. |
| N/A | Non applicable — **motif obligatoire**. |
| ROLLED_BACK | Mutation annulée après échec. |

---

## 4. Evidence Chain

Chaque Gravure produit une chaîne de preuve cohérente :

```text
MISSION → SCOPE → CLOSURE → VALIDATION → ASSIMILATION
    → CANONICAL DIFF → STAGING → SECURITY REVIEW
    → INDEPENDENT REVIEW → AUTHORIZATION → LOCAL COMMIT
    → REMOTE COMMIT → REMOTE TREE → PATH PARITY
    → FINAL DECISION → MARBLE CERTIFICATE
```

Une preuve doit être : identifiable, datée, liée à la mission, reproductible lorsque possible, suffisamment précise pour permettre un audit ultérieur.

---

# LES 8 PHASES

---

## Phase 0 — AUTHORITY : Autorité, Contrat et Verrouillage

### Objectif
Établir qui demande, quoi, où, sur quelle référence et avec quelle autorité.

### Contrat de Gravure (entrées obligatoires)

```yaml
mission_id: "GRAVURE-YYYYMMDD-<slug>-<nonce>"
protocol_version: "2.0.0"
operator: "<principal humain>"
producer: "<agent producteur>"
validator: "<agent distinct>"
closure_type: "internal-only | public-mvp | public-update"
sgc_item: "<identifiant interne SGC>"
public_repository: "<owner/repo> | N/A"
public_ref: "<branche cible> | N/A"
supersedes: []
children: []
required_checks: []
authorized_files: []
forbidden_files: []
rollback_plan: "<procédure vérifiable>"
```

### Contrôles

1. Identifier chaque dépôt réel avec `git rev-parse --show-toplevel`.
2. Pour chaque dépôt affecté, relever : racine, remote, branche, HEAD, état du worktree et SHA distant.
3. Calculer l'empreinte de baseline sur les fichiers gouvernants et artefacts ciblés.
4. Déclarer les outils de contrôle réellement disponibles. Un contrôle requis indisponible = UNKNOWN → BLOCKED.

### Postcondition

PREFLIGHT_PASS seulement si l'autorité, la portée, les racines Git, la baseline, le validateur et le rollback sont tous explicites.

### Échec

```text
AUTHORIZATION_MISMATCH → BLOCKED → STOP
```

---

## Phase 1 — CLOSURE : Clôture Interne du Cahier des Charges

### Objectif
Prouver que le chantier est réellement terminé avant d'engager la gravure.

### 1.1 DoD déterministe

Chaque critère de clôture doit comporter :
- un identifiant stable ;
- une postcondition binaire ;
- une commande ou observation reproductible ;
- un résultat PASS, FAIL, N/A ou UNKNOWN ;
- un pointeur vers la preuve.

Un **enfant** est « terminé » uniquement si :
1. il figure dans la liste children du contrat ;
2. son statut terminal est prouvé ;
3. ses livrables requis existent et sont validés ;
4. aucun blocage critique n'est ouvert.

Un enfant PARTIAL, UNKNOWN ou AWAITING_AUTHORIZATION **bloque** la clôture, sauf s'il est explicitement hors périmètre avec justification et validation humaine.

### 1.2 Ruban de Badges

**Badges de base (obligatoires) :**

```markdown
![Status](https://img.shields.io/badge/Status-MVP-blue)
![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple)
```

**Badges conditionnels (uniquement si prouvés) :**
- Security-ID LOCKED → uniquement si le contrôle sécurité correspondant est défini et passé.
- Python-3.12+ → uniquement si le projet requiert et vérifie cette version.

> Tout badge est une affirmation vérifiable, pas un élément décoratif.

### 1.3 Signature & Horodatage de Clôture

Le cahier des charges reçoit :

```yaml
closure_status: "<statut terminal>"
closed_at: "YYYY-MM-DDTHH:MM:SS±HH:MM"
mission_id: "<id>"
producer: "<identité>"
validator: "<identité distincte>"
evidence_chain: "<chemin relatif>"
content_manifest_sha256: "<empreinte>"
internal_commit: "<sha | N/A>"
public_commit: "<sha | N/A>"
remote_verified_at: "<timestamp | N/A>"
supersedes: []
```

### Postcondition

```text
PASS → CLOSED
FAIL → BLOCKED
```

---

## Phase 2 — VALIDATION : Vérification Indépendante

### Objectif
Vérifier que l'accomplissement est techniquement et fonctionnellement conforme. **Producer ≠ Validator.**

### Gatekeeper à 4 niveaux

| Niveau | Contrôle | Outils |
|---|---|---|
| 1. **Spatial** | Fichiers limités aux chemins autorisés, aucun artefact interne exposé | git diff --name-only, ls |
| 2. **Intégrité** | Tests, lint, build, validation JSON/YAML, lsp_diagnostics, Mermaid si présent | pyright, jq, yamllint |
| 3. **Sécurité** | Scan de secrets/PII, dépendances, permissions, aucun credential ni chemin privé exposé | scan-secrets.sh, grep |
| 4. **Sémantique** | Chaque ligne du diff correspond à l'objectif contractuel, sans distillation ni changement opportuniste | Revue de diff |

### Postcondition

VERIFIED_LOCAL exige PASS sur tous les contrôles requis. UNKNOWN n'est **jamais** assimilé à PASS.

---

## Phase 3 — ASSIMILATION : Cartographie Chirurgicale Canonique

### Objectif
Déterminer si la nouvelle capacité appartient à l'architecture Tesla et comment elle doit y être représentée.

### 3.1 Principe cardinal

> **Inspecter exhaustivement ne signifie pas modifier exhaustivement.**

La mission établit une **Matrice d'Impact** et ne modifie que les cibles dont le contenu doit réellement changer.

### 3.2 Matrice d'Impact Canonique

| Cible logique | Déclencheur d'écriture | Contrôle minimal |
|---|---|---|
| SOUL.md | Changement d'identité ou d'invariant constitutionnel | Diff sémantique approuvé |
| ENGINE.md | Nouveau moteur cognitif ou changement de raisonnement | Route et invariant cohérents |
| AGENTS.md | Nouveau rôle, sous-agent, Skill ou règle d'orchestration | Table de délégation sans doublon |
| FORCE_TOOLING.md | Nouveau cycle de découverte/sélection/retrait d'une capacité | Lifecycle complet |
| TESLA.json | Module actif enregistré ou retiré | JSON valide, identifiant unique |
| settings.json | Script/MCP/permission réellement déployé | JSON valide, commande et arguments exacts |
| liste_projets_antigravity_BASE.md | Nouveau projet ou audit à historiser | Identifiant unique et statut exact |
| PROJECT_STATE.md | État de reprise modifié | Reprise cohérente avec le SGC |
| SESSION_LOG.md | Événement de mission à journaliser | Pas de secret ni PII |
| GEMINI.md | Changement d'une règle propre à ce document | Référence non ambiguë |
| Le_Conducteur_Absolu_v3.2.1.md | Changement des Gates ou de leur contrat | Versionnement explicite |
| OUTPUTS/ | Toute intervention majeure | Livrable et Evidence Chain présents |
| Skills Registry | Ajout, évolution ou retrait d'un Skill | Version et route cohérentes |

Pour chaque ligne : PASS si contrôlée et conforme, N/A avec motif si non impactée, UNKNOWN si inaccessible, FAIL si contradictoire. **Une cible requise absente = BLOCKED, jamais N/A.**

### 3.3 Routage minimal

- *Sous-agent, Skill ou module actif* → AGENTS.md, TESLA.json, registre des Skills
- *Moteur cognitif ou organe sensoriel* → ENGINE.md, FORCE_TOOLING.md
- *Script ou outil d'exécution* → settings.json (uniquement si le binaire existe et est validé)
- *Fix, maintenance ou audit* → Taxonomie, état projet et OUTPUTS/ (sans pollution des registres de capacités)
- *Changement de gouvernance* → Corpus concerné, version, migration et décision humaine

### 3.4 Réconciliation des Open-Items

Pour chaque entrée de OUTPUTS/open_items_todo-Updated.md :

1. Faire correspondre un identifiant, jamais une phrase approximative.
2. Passer à RESOLVED **uniquement** avec preuve et date.
3. **Conserver** les items non résolus.
4. Ajouter une référence vers l'Evidence Chain.
5. **Ne jamais supprimer le fichier entier ni effacer son historique.**

### 3.5 Audit Post-Mission (Loi de Parité Absolue)

> **RÉFÉRENTIEL CANONIQUE :** `memory/PROTOCOLES/LOI-DE-PARITE-ABSOLUE.md`

L'Orchestrateur a l'interdiction formelle d'utiliser des recherches globales approximatives (ex: `grep -E -i`). L'Audit Post-Mission s'exécute exclusivement via le validateur déterministe défini dans le protocole de la Loi de Parité Absolue :
L'Orchestrateur invoque le script `scripts/audit_parite.sh --id <ID> --type <TYPE>` (ou exécute sa spécification manuellement en cas d'absence) pour auditer **fichier par fichier** la cohérence entre la Strate d'Exécution et la Strate Mémorielle, et générer l'Evidence Ledger JSON. Un seul échec ou fantôme détecté = BLOCKED + lancement du Circuit-Breaker de Self-Healing.

### Postcondition

```text
PASS → ASSIMILATED + CANONICAL
BLOCKED → aucune propagation canonique
```

---

## Phase 4 — PUBLIC STAGING : Ingénierie Documentaire et Staging Public

> Cette phase vaut N/A pour une clôture strictement interne (closure_type: internal-only).

### 4.1 Délégation et Périmètre de Propagation

L'Orchestrateur invoque l'Agent d'élite tesla-github-manager pour exécuter les missions suivantes. **AGENTS délègue, il ne réimplémente pas.**

L'Agent tesla-github-manager opère sur un double périmètre de propagation :

- **Niveau Local et Interne :** `/home/lord-mahonheim/bifrost/tesla/MVP-GITHUB`
  L'agent structure, vérifie et grave physiquement les fichiers du nouveau MVP dans ce répertoire. Il respecte l'ordre d'incrémentation, la numérotation séquentielle (Décorrélation Taxonomique), les exigences de rédaction en anglais strict et les bonnes pratiques d'une documentation MVP (Objective, Architecture, Deliverables, Governance).

- **Niveau Distant et Public :** `https://github.com/lordmahonheim-bot/Tesla-Antigravity-CLI/tree/main`
  Sous la stricte validation préalable de Lord Mahonheim, l'agent exécute la séquence Git (Add, Commit, Push) pour publier ces livrables sur le dépôt public. Il respecte l'ordre du Repository Layout de la page, la numérotation existante, les exigences de GitHub et les bonnes pratiques de publication de référentiels (README cohérent, badges, liens, schémas Mermaids, structure de dossiers).

La mission est définitivement scellée lorsque tesla-github-manager confirme, via un ultime `git status`, que la branche locale et le dépôt distant sont parfaitement synchronisés.

### 4.2 Mission A — Rédaction (English Strict)

Le README public est rédigé **strictement en anglais** et comprend :

- Objective & non-goals
- Architecture / workflow
- Mermaid Graph (requis uniquement si le flux est complexe ; si présent, syntaxe validée)
- Technical Deliverables & prerequisites
- Installation / usage si applicable
- Validations & known limitations
- Security / Governance
- License & support status si applicable

### 4.3 Mission B — Gestion des Dépréciations (Anti-Oubli)

Un ancien MVP n'est déprécié que s'il est explicitement listé dans supersedes et si le remplacement fonctionnel est **prouvé**.

Pour chaque MVP concerné :

1. Remplacer uniquement le badge Status par Status-OBSOLETE-red.
2. Préserver les autres badges encore exacts.
3. Insérer une DEPRECATION NOTICE datée avec motif, remplaçant et lien.
4. Fournir une migration ou indiquer clairement qu'elle n'existe pas.
5. Ajouter un lien retour depuis le nouveau MVP.
6. **Ne supprimer ni code ni historique** dans cette mission, sauf autorisation destructive séparée.

### 4.4 Mission C — Décorrélation Taxonomique

La numérotation publique est déterminée par l'état réel de MVP-GITHUB/, **jamais** par le numéro SGC interne.

1. Inventorier les dossiers correspondant au pattern ^[0-9]+-[A-Za-z0-9][A-Za-z0-9._-]*$.
2. Signaler noms non conformes, doublons numériques et trous.
3. Calculer le prochain numéro depuis le maximum confirmé du registre public (N+1).
4. Revalider l'inventaire juste avant la création.
5. Créer le dossier par une opération exclusive qui échoue en cas de collision.

### Postcondition

```text
PASS → STAGED
FAIL → BLOCKED
```

---

## Phase 5 — AUTHORIZATION : Biological Gate Mahonheim

### Objectif
Obtenir l'autorisation souveraine lorsque la publication l'exige.

### Présentation à Lord Mahonheim

L'Evidence Chain est présentée sous forme synthétique :

```text
MISSION → SCOPE → CHANGES → VALIDATION → SECURITY
    → REVIEW → TARGET → EXPECTED COMMIT → EXPECTED REMOTE STATE
    → RISKS → ROLLBACK
```

Informations obligatoires :
- dépôt owner/repo ;
- branche source et destination ;
- SHA local et SHA distant attendu ;
- liste des commits et résumé des fichiers ;
- résultats des validations ;
- dépréciations prévues ;
- méthode de rollback ;
- commande distante exacte.

### Décisions

```text
APPROVE → AUTHORIZED
REJECT  → BLOCKED
DEFER   → BLOCKED
```

> Une intention implicite ne vaut jamais approbation. Sans autorisation explicite : enregistrer AWAITING_AUTHORIZATION, créer l'open-item et s'arrêter.

---

## Phase 6 — PUBLICATION : Transaction Git et Vérification Distante

### 6.1 Commit local

1. Une transaction de commit par dépôt Git **réellement affecté**.
2. Stager par chemins explicites, puis relire le diff indexé.
3. Interdire : secrets, fichiers hors contrat, résultats de tests rouges.
4. Enregistrer le SHA de chaque commit local dans l'Evidence Chain.

### 6.2 Push autorisé

1. Vérifier l'identité GitHub et le dépôt cible.
2. Revérifier le SHA distant attendu.
3. Exécuter **exactement** l'opération autorisée.
4. Interdire le force-push sauf mission R3 séparée et explicitement autorisée.

### 6.3 Post-vérification (Remote Parity)

La propagation est PASS uniquement si :

```text
expected_remote_sha == observed_remote_sha
AND expected_paths ⊆ remote_tree
AND scope == authorized_scope
```

Preuves minimales :

```bash
git fetch origin --prune
git rev-parse origin/<ref>
git ls-tree -r --name-only origin/<ref> -- <expected-path>
```

Un timeout ou une réponse ambiguë après écriture produit UNKNOWN_REMOTE_STATE. **Relire l'état distant d'abord ; ne jamais répéter le push à l'aveugle.**

### Postcondition

```text
PASS → PUBLISHED + REMOTE_VERIFIED
UNKNOWN → UNKNOWN_REMOTE_STATE (ne pas sceller)
FAIL → FAILED / ROLLBACK
```

---

## Phase 7 — SEAL : Archivage SGC, Evidence Chain et Scellement

> Cette phase ne commence **que si** :
> - la publication requise est REMOTE_VERIFIED, **ou**
> - le contrat déclarait internal-only ;
> - toutes les validations requises sont PASS ou N/A motivé ;
> - aucun open-item bloquant n'est actif.

### 7.1 Archivage transactionnel SGC

1. Vérifier que la source existe une seule fois et que la destination n'existe pas.
2. Déplacer le cahier des charges vers Gestion-de-Chantiers/Archivage-de-Chantiers/.
3. Mettre à jour INDEX.md → statut ✅ Terminé/Archivé dans le **même changeset**.
4. Vérifier après opération : source absente, destination unique, lien d'index valide.

### 7.2 Marble Certificate

```yaml
mission_id:
artifact:
version:
protocol_version: "2.0.0"
state:
  initial:
  final:
authority:
  principal:
  repository:
  action:
  target:
  ref:
  risk_class:
  session_id:
closure:
  result:
  evidence:
validation:
  result:
  checks:
  validator:
assimilation:
  result:
  canonical_files:
  admission_evidence:
canonical:
  result:
  drift_detected:
staging:
  result:
  paths:
security:
  result:
  scans:
review:
  result:
  independent_validator:
authorization:
  result:
  authorized_by:
publication:
  result:
  local_commit_sha:
  remote_commit_sha:
remote_parity:
  result:
  expected_paths:
  confirmed_paths:
rollback:
  available:
  reference:
seal:
  result:
  sealed_at:
  sealed_by:
```

### 7.3 Conditions de scellement

Le Seal n'est autorisé que si :

```text
Phase 0 = PASS    (Authority)
Phase 1 = PASS    (Closure)
Phase 2 = PASS    (Validation)
Phase 3 = PASS    (Assimilation)
Phase 4 = PASS/NA (Public Staging)
Phase 5 = PASS/NA (Authorization)
Phase 6 = PASS/NA (Publication)
```

**ET :**
- aucune anomalie UNKNOWN critique ;
- aucune autorisation manquante ;
- aucune preuve critique manquante ;
- aucune dérive canonique ;
- aucune exposition de secret ;
- Evidence Chain complète ;
- Marble Certificate écrit ;
- état final reproductible.

### Postcondition

```text
VERIFIED → MARBLE SEAL → SEALED
```

---

# ANNEXES

---

## A. Matrice de défaillance

| Événement | Décision | Action |
|---|---|---|
| DoD incomplet | BLOCKED | Arrêter |
| Test critique échoué | FAIL | Corriger |
| Preuve manquante | BLOCKED | Produire la preuve |
| Canonical drift | BLOCKED | Réconcilier |
| Secret détecté | BLOCKED | Nettoyer + revalider |
| Scope public incorrect | BLOCKED | Corriger staging |
| Review indépendante échouée | BLOCKED | Corriger |
| Autorisation absente | BLOCKED | Arrêter |
| Commit incorrect | FAIL | Rollback/recovery |
| Push timeout | UNKNOWN | Vérifier distant |
| Remote SHA inattendu | FAIL/UNKNOWN | Diagnostiquer |
| Path attendu absent | FAIL | Corriger publication |
| État distant non observable | UNKNOWN | Ne pas sceller |
| Parité complète | PASS | Continuer |
| Tous les Gates PASS | PASS | Éligible au scellement |

---

## B. Rollback / Recovery

| Cas | Procédure |
|---|---|
| Échec avant commit | Restore working tree, verify canonical state |
| Commit local incorrect | Identify bad commit, preserve evidence, revert/reset, revalidate |
| Push échoué (état distant inconnu) | UNKNOWN_REMOTE_STATE → interroger l'état distant d'abord, jamais de retry aveugle |
| Parité distante incorrecte | BLOCK → PRESERVE EVIDENCE → STOP MUTATIONS → RECONCILE → REVALIDATE |
| Publication incorrecte | Correction par nouvelle mutation traçable ou rollback autorisé. Ne jamais réécrire silencieusement l'historique. |

---

## C. Responsabilités des Agents

| Fonction | Autorité / rôle |
|---|---|
| Orchestration | Tesla / AGENTS |
| Stress-test | premortem (Règle 12 - fin de séquencement) |
| Implémentation | Agent spécialisé approprié |
| Documentation & Publication Git | tesla-github-manager |
| Validation technique | Agent/outil indépendant |
| Autorisation souveraine | Lord Mahonheim |

---

## D. Checklist Opérationnelle

### Avant mutation
- [ ] Contrat complet et mission ID unique
- [ ] Producteur et validateur distincts
- [ ] Racines Git et topologie découvertes
- [ ] Baseline et rollback enregistrés
- [ ] DoD et enfants tous prouvés
- [ ] Outils requis disponibles

### Avant commit
- [ ] Matrice canonique complète (Audit Post-Mission / Parité Absolue exécuté)
- [ ] Open-items réconciliés (sans purge globale)
- [ ] Numéro public revalidé (si applicable)
- [ ] README anglais strict et badges probants (si applicable)
- [ ] Dépréciations limitées à supersedes
- [ ] Diff, tests, formats, liens, Mermaid et secrets validés
- [ ] Aucun fichier hors contrat dans le staging

### Avant push
- [ ] Identité et dépôt distant vérifiés
- [ ] SHA distant conforme à l'état attendu
- [ ] Autorisation explicite, exacte et actuelle
- [ ] Commande/opération égale à l'autorisation

### Après push
- [ ] Ref distant relu
- [ ] SHA/PR/checks vérifiés
- [ ] Mutation journalisée et expurgée de secrets
- [ ] Aucun état distant inconnu

### Avant archivage SGC
- [ ] Publication requise vérifiée ou contrat internal-only
- [ ] Métadonnées ISO 8601, SHA et manifeste inscrits
- [ ] Destination libre et rollback possible
- [ ] Déplacement et INDEX.md traités comme une transaction
- [ ] Archive, hashes et lien d'index revérifiés

### Avant déclaration finale
- [ ] Evidence Chain complète
- [ ] Tous les contrôles requis sont PASS ou N/A motivé
- [ ] Aucun open-item bloquant
- [ ] git status collecté pour chaque dépôt
- [ ] Statut final choisi dans la liste autorisée
- [ ] Marble Certificate généré

---

## E. Formules Canoniques

> **No Evidence → No Transition.**

> **No Independent Validation → No Pass.**

> **No Authorization → No Push.**

> **No Remote Proof → No Publication.**

> **No Full Parity → No Marble.**

> **Gravé n'est pas déclaré. Gravé est prouvé.**

---

## F. Critère ultime

Un accomplissement Tesla n'est **pas** gravé parce que :

- l'agent affirme qu'il est terminé ;
- les tests locaux passent ;
- le commit existe ;
- git push ne retourne pas d'erreur ;
- git status est propre ;
- un badge affiche MVP.

Il est gravé **uniquement** lorsque l'état final est :

```text
AUTHORIZED + VALIDATED + CANONICAL + REVIEWED
    + PUBLISHED + REMOTE VERIFIED + EVIDENCE COMPLETE
    = SEALED
```

> ## NO PROOF, NO MARBLE.
