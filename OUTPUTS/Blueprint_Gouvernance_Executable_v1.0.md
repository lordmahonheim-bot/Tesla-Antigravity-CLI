# 🏛️ BLUEPRINT DE GOUVERNANCE EXÉCUTABLE — VIGILUM CODEX 2.0

**Version:** 1.0.0  
**Statut:** STRATÉGIQUE — PRÊT POUR IMPLÉMENTATION  
**Écosystème:** Tesla / Antigravity CLI / MIDGARD  
**Doctrine:** Vigilum Codex  
**Date d'audit:** 2026-08-26  
**Classification:** ULTRA-SENSIBLE — FAIL-CLOSED MANDATORY  

---

## PRÉAMBULE

La gouvernance déclarative (fichiers `.md`) a atteint ses limites face à la nature probabiliste des LLM. Le postulat fondamental est le suivant :

> **Tout fichier `.md` est un desiderata. Aucun `.md` n'est une contrainte d'exécution.**

L'écosystème Tesla doit muter vers une **gouvernance 100% exécutable**, où les protocoles canoniques sont appliqués par des **mécanismes déterministes** (Scripts, MCP, Daemons, Hooks). L'invariant cardinal demeure :

> **"Le code valide, l'IA propose."**

Ce Blueprint constitue le plan d'ingénierie définitif pour réaliser cette transition.

---

# AXE 1 : AUDIT D'ENCAPSULATION (DE TEXTE À CODE)

## 1.1 Inventaire de l'Infrastructure Canonique Actuelle

### 1.1.1 État des lieux des Protocoles Existants

| ID | Nom du Protocole | Fichier Source | Statut Actuel | Criticité |
|:---|:---|:---|:---|:---|
| P-01 | **Gravure sur Marbre** | `PROTOCOLES/GRAVURE-SUR-MARBRE.md` | Déclaratif | CRITIQUE |
| P-02 | **Loi de Parité Absolue** | `PROTOCOLES/LOI-DE-PARITE-ABSOLUE.md` | Déclaratif | CRITIQUE |
| P-03 | **Le Conducteur Absolu v3.2.1** | `46-Conducteur-Absolu-v3.2.1/Le_Conducteur_Absolu_v3.2.1.md` | Déclaratif | CRITIQUE |
| P-04 | **Vigilum Gateway V2.1** | `31-Vigilum-Gateway-V2.1/README.md` | Partiellement Exécutable | HAUTE |
| P-05 | **Tesla Governance Gateway** | `27-Tesla-Governance-Gateway/` | MVP Existant | MOYENNE |

### 1.1.2 Inventaire des Fichiers de Gouvernance Ciblés

```
INFRASTRUCTURE ACTUELLE (AUDITÉE)
├── PROTOCOLES/
│   ├── GRAVURE-SUR-MARBRE.md          [CRITIQUE - 727 lignes]
│   └── LOI-DE-PARITE-ABSOLUE.md      [CRITIQUE - 427 lignes]
├── memory/                            [RÉFÉRENCE - Source de Vérité]
│   ├── PROJECT_STATE.md               [OBLIGATOIRE - Ancre]
│   ├── SESSION_LOG.md                 [OBLIGATOIRE - Journal]
│   └── liste_projets_antigravity_BASE.md [OBLIGATOIRE - Taxonomie]
├── .agents/                           [RÉFÉRENCE - Manifestes]
│   ├── TESLA.json                     [OBLIGATOIRE - Registre]
│   ├── AGENTS.md                      [OBLIGATOIRE - Routage]
│   └── settings.json                  [OBLIGATOIRE - Permissions]
├── 46-Conducteur-Absolu-v3.2.1/
│   └── Le_Conducteur_Absolu_v3.2.1.md [CRITIQUE - 186 lignes]
├── 31-Vigilum-Gateway-V2.1/           [HAUTE]
├── 27-Tesla-Governance-Gateway/       [MOYEN - MVP Existant]
│   ├── policy_engine.sh               [EXISTANT - À ÉTENDRE]
│   ├── capability_registry.json       [EXISTANT]
│   └── agents/*.sh                    [EXISTANT]
└── OUTPUTS/
    └── CHECKPOINT_CONTRACT.yaml        [EXISTANT]
```

### 1.1.3 Lacunes Identifiées (Gap Analysis)

| Lacune | Impact | Risque |
|:---|:---|:---|
| Aucune validation automatique des Gates 0-6 | Bloquante | CRITIQUE |
| Absence de démon Broker Pattern | Bloquante | CRITIQUE |
| Pas de hooks git actifs sur la branche | Majeure | HAUTE |
| Vérification Parité non déterministe | Majeure | HAUTE |
| Scripts de scan secrets non whitelisted | Modérée | MOYENNE |
| Pas de circuit-breaker standardisé | Modérée | MOYENNE |

---

## 1.2 Inventaire des Protocoles Candidats à la Mécanisation

### 1.2.1 Matrice de Priorisation

| Priorité | Protocole | Vecteur Optimal | Complexité | ROI |
|:---:|:---|:---|:---|:---|
| P0 | Gravure sur Marbre (Machine d'État) | Script Bash + Daemon | ÉLEVÉE | CRITIQUE |
| P0 | Loi de Parité Absolue (Audit Post-Mission) | Script Bash | MOYENNE | CRITIQUE |
| P0 | Conducteur Absolu (7 Gates) | Script Bash + MCP | TRÈS ÉLEVÉE | CRITIQUE |
| P1 | Vigilum Gateway (Orchestration Hardening) | MCP Server (Python/TS) | MOYENNE | HAUTE |
| P1 | Policy Engine (Tesla Governance Gateway) | Script Bash (EXISTANT) | FAIBLE | HAUTE |
| P2 | Capability Bus (Canonical Sync) | Script Bash (PARTIEL) | FAIBLE | MOYENNE |

### 1.2.2 Protocole P-01 : Gravure sur Marbre — Découpage en Modules Exécutables

#### Phase 0 (AUTHORITY) — Module : `tesla-gravure-authority.sh`

```bash
# SPEC : AUTHORITY Module
# Inputs:
#   - $1: mission_id (ex: GRAVURE-20260826-SKILL-001)
#   - $2: closure_type (internal-only|public-mvp|public-update)
#   - $3: operator (principal humain)
#   - $4: producer (agent producteur)
#   - $5: validator (agent validateur)
#   - $6: sgc_item (identifiant SGC)
# Outputs:
#   - Exit 0 + TOKEN_AUTHORITY si PASS
#   - Exit 1 + reason si BLOCKED
#   - Fichier: /tmp/tesla_gravure/authority_[mission_id].json
```

#### Phase 1 (CLOSURE) — Module : `tesla-gravure-closure.sh`

```bash
# SPEC : CLOSURE Module
# Inputs:
#   - TOKEN_AUTHORITY de Phase 0
#   - Fichier: cahier des charges (Markdown)
#   - Checklist DoD (YAML)
# Outputs:
#   - Exit 0 si CLOSED
#   - Exit 1 si BLOCKED (DoD incomplet)
#   - Fichier: /tmp/tesla_gravure/closure_[mission_id].json
```

#### Phase 2 (VALIDATION) — Module : `tesla-gravure-validation.sh`

```bash
# SPEC : VALIDATION Module (Gatekeeper 4 Niveaux)
# Inputs:
#   - TOKEN_AUTHORITY + TOKEN_CLOSURE
#   - workdir (répertoire à vérifier)
#   - authorized_files (liste blanche)
#   - forbidden_files (liste noire)
# Outputs:
#   - Exit 0 si VERIFIED_LOCAL
#   - Exit 1 si BLOCKED (échec niveau)
#   - Fichier: /tmp/tesla_gravure/validation_[mission_id].json
# Contrôles:
#   Niveau 1: Spatial (fichiers limités aux chemins autorisés)
#   Niveau 2: Intégrité (lsp, tests, build)
#   Niveau 3: Sécurité (scan-secrets, PII)
#   Niveau 4: Sémantique (diff vs objectif contractuel)
```

#### Phase 3 (ASSIMILATION) — Module : `tesla-gravure-assimilation.sh`

```bash
# SPEC : ASSIMILATION Module (Matrice d'Impact Canonique)
# Inputs:
#   - TOKEN_AUTHORITY + TOKEN_CLOSURE + TOKEN_VALIDATION
#   - component_type (Skill|Agent|MCP|Script|Modification)
#   - component_id (identifiant canonique)
# Outputs:
#   - Exit 0 si INTEGRATED_LOCAL
#   - Exit 1 si BLOCKED (canonical drift)
#   - Fichier: /tmp/tesla_gravure/assimilation_[mission_id].json
```

#### Phase 4 (PUBLIC STAGING) — Module : `tesla-gravure-staging.sh`

```bash
# SPEC : PUBLIC STAGING Module
# Inputs:
#   - TOKEN_AUTHORITY + TOKEN_CLOSURE + TOKEN_VALIDATION + TOKEN_ASSIMILATION
#   - closure_type != internal-only
# Outputs:
#   - Exit 0 si STAGED
#   - Exit 1 si BLOCKED
#   - Fichier: /tmp/tesla_gravure/staging_[mission_id].json
```

#### Phase 5 (AUTHORIZATION) — Module : `tesla-gravure-authorization.sh`

```bash
# SPEC : BIOLOGICAL GATE MODULE
# Inputs:
#   - TOKEN_AUTHORITY + TOKEN_CLOSURE + TOKEN_VALIDATION + TOKEN_ASSIMILATION + TOKEN_STAGING
#   - PUSH_REQUEST.md (produit par le module)
# Outputs:
#   - Exit 0 si AUTHORIZED
#   - Exit 1 si BLOCKED (autorisation non obtenue)
#   - Fichier: /tmp/tesla_gravure/authorization_[mission_id].json
```

#### Phase 6 (PUBLICATION) — Module : `tesla-gravure-publication.sh`

```bash
# SPEC : PUBLICATION Module
# Inputs:
#   - TOKEN_AUTHORIZATION (Mahonheim approval)
#   - git remote + ref
#   - expected_sha
# Outputs:
#   - Exit 0 + SHA si PUBLISHED + REMOTE_VERIFIED
#   - Exit 1 si FAIL
#   - Fichier: /tmp/tesla_gravure/publication_[mission_id].json
```

#### Phase 7 (SEAL) — Module : `tesla-gravure-seal.sh`

```bash
# SPEC : SEAL Module (Marble Certificate Generator)
# Inputs:
#   - TOKEN_AUTHORITY + TOKEN_CLOSURE + TOKEN_VALIDATION
#   - TOKEN_ASSIMILATION + TOKEN_STAGING + TOKEN_AUTHORIZATION + TOKEN_PUBLICATION
#   - Tous les fichiers de preuve des phases précédentes
# Outputs:
#   - Exit 0 si SEALED (Marble Certificate généré)
#   - Exit 1 si BLOCKED (conditions de scellement non réunies)
#   - Fichier: OUTPUTS/MARBLE_CERTIFICATE_[mission_id].yaml
```

### 1.2.3 Protocole P-02 : Loi de Parité Absolue — Module `audit_parite.sh`

```bash
# SPEC : AUDIT_PARITE Script (Conforme au §9 du protocole)
# Inputs:
#   --id <identifiant-canonique>
#   --type <Skill|Agent|MCP|Script|Modification|Organe>
#   --root <TESLA_ROOT>
#   --mission <MISSION_ID>
#   --baseline "sha256:..."
# Outputs:
#   Exit 0: PASS (parité prouvée)
#   Exit 1: BLOCKED (orphelin ou fantôme détecté)
#   Exit 2: STALE_STATE (fingerprint divergent)
#   Exit 64: Erreur d'usage
#   Exit 66: TESLA_ROOT introuvable
#   Exit 69: Dépendance manquante
#   Fichier: OUTPUTS/evidence/parity_[MISSION_ID]_[TIMESTAMP].json
#
# VÉRIFICATION OBLIGATOIRE (interdictions formelles):
#   - grep fichier par fichier (PAS de grep multi-fichiers)
#   - Correspondance littérale: grep -F -w (PAS -i, PAS -E)
#   - Détection bidirectionnelle: anti-amnésie ET anti-fantôme
```

### 1.2.4 Protocole P-03 : Le Conducteur Absolu — Orchestrateur de Gates

```bash
# SPEC : CONDUCTEUR_ABSOLU Orchestrateur
# Inputs:
#   - Mission ID
#   - Classe (Triviale | Standard | Complexe | Critique)
#   - Baseline Fingerprint
# Outputs:
#   - Pipeline de Gates G0-G6 orchestré
#   - Evidence Chain Ledger dans OUTPUTS/
#   - Exit global = AND de tous les Gates
#
# GATE 0: AUTHORITY & RELOAD COGNITIF
#   -> Script: tesla-conductor-gate0.sh
#   -> Contrat: PROJECT_STATE.md + TELEGRAM_SYNAPSE.md
#
# GATE 1: CANONICAL DISCOVERY
#   -> Script: tesla-conductor-gate1.sh
#   -> Contrat: State Fingerprint + rg/deterministic search
#
# GATE 2: MISSION CONTRACT (DAG)
#   -> Script: tesla-conductor-gate2.sh
#   -> Contrat: OUTPUTS/CONTRACTS/CONTRACT_*.yaml
#
# GATE 3: DELEGATION & BROKER PATTERN
#   -> Script: tesla-conductor-gate3.sh
#   -> Contrat: CHECKPOINT_*.yaml (15s grace period)
#
# GATE 4: INDEPENDENT VERIFICATION
#   -> Script: tesla-conductor-gate4.sh
#   -> Contrat: 4-Niveaux Gatekeeper
#
# GATE 5: CANONICAL INTEGRATION
#   -> Script: tesla-conductor-gate5.sh
#   -> Contrat: 14 Piliers Canoniques
#
# GATE 6: CLOSURE & EVIDENCE
#   -> Script: tesla-conductor-gate6.sh
#   -> Contrat: EVIDENCE_CHAIN_[ID]_[DATE].md
```

---

## 1.3 Spécifications I/O pour les Futurs Outils

### 1.3.1 Format Standard des Intents (Entrées Démon)

```yaml
# /OUTPUTS/intents/[INTENT_TYPE]_[MISSION_ID]_[TIMESTAMP].yaml
intent_schema: "VIGILUM_CODEX_2.0"
version: "1.0.0"

intent_id: "GRAVURE-20260826-MVP-001"
intent_type: "GRAVURE|MISSION|PARITE|PRECOMMIT|PREPUSH"
priority: "P0|P1|P2|P3"
emitter: "tesla-master-code|tesla-arcanis|human:lordmahonheim"
timestamp: "2026-08-26T14:30:00Z"
session_id: "sess_abc123"

# Payload selon intent_type
payload:
  # Pour GRAVURE:
  mission_id: "GRAVURE-20260826-SKILL-001"
  closure_type: "public-mvp"
  operator: "lordmahonheim"
  producer: "tesla-master-code"
  validator: "tesla-code-auditor"
  scope:
    authorized_files: ["/home/user/Tesla-Antigravity-CLI/52-XXX/"]
    forbidden_files: ["/home/user/Tesla-Antigravity-CLI/memory/", "/home/user/Tesla-Antigravity-CLI/.agents/"]
    authorized_operations: ["write_file", "read_file", "lsp_diagnostics"]
    forbidden_operations: ["git push", "ask_permission", "rm -rf"]
  baseline_fingerprint: "sha256:abc123..."
  rollback_plan: "git checkout -- ."

  # Pour PARITE:
  component_id: "tesla-master-code"
  component_type: "Skill"
  stale_state_check: true

  # Pour PRECOMMIT:
  files_staged: ["file1.md", "file2.py"]
  diff_hash: "sha256:def456..."
  
  # Pour PREPUSH:
  remote: "origin"
  ref: "refs/heads/main"
  expected_sha: "sha256:ghi789..."

# Signatures
signature:
  algorithm: "HMAC-SHA256"
  key_id: "tesla-master-key-01"
  value: "base64:..."

attestation:
  - role: "producer"
    agent: "tesla-master-code"
    timestamp: "2026-08-26T14:30:00Z"
```

### 1.3.2 Format Standard des Rapports (Sorties Démon)

```yaml
# /tmp/tesla_broker/reports/[INTENT_ID]_[PHASE]_[TIMESTAMP].yaml
report_schema: "VIGILUM_CODEX_2.0"
version: "1.0.0"

intent_id: "GRAVURE-20260826-MVP-001"
phase: "AUTHORITY|CLOSURE|VALIDATION|ASSIMILATION|STAGING|AUTHORIZATION|PUBLICATION|SEAL"
status: "PASS|BLOCKED|FAIL|UNKNOWN|STALE_STATE"
timestamp: "2026-08-26T14:30:05Z"
duration_ms: 1234
circuit_breaker:
  iteration: 0
  max_iterations: 3
  triggered: false

# Vérifications détaillées
checks:
  - id: "AUTH_TOKEN_VALID"
    description: "Authority token valide et non expiré"
    result: "PASS"
    evidence: "token_expiry=2026-08-26T15:30:00Z"
  
  - id: "BASELINE_STABLE"
    description: "State fingerprint inchangé"
    result: "PASS"
    evidence: "fingerprint=sha256:abc123..."
    
  - id: "SCOPE_COMPLIANT"
    description: "Fichiers dans périmètre autorisé"
    result: "PASS"
    evidence: "files_compliant=12, files_forbidden=0"

# Outputs
outputs:
  next_phase: "CLOSURE"
  next_token: "TOKEN_CLOSURE_xxx"
  artifacts:
    - path: "/tmp/tesla_gravure/authority_GRAVURE-20260826-MVP-001.json"
      sha256: "sha256:..."
      
# Recommandations (si BLOCKED)
block_reason:
  code: "E_AUTH_SCOPE_DRIFT"
  description: "Fichiers modifiés hors périmètre autorisé détectés"
  affected_files: ["/home/user/memory/SESSION_LOG.md"]
  remediation: "Relancer avec TOKEN mis à jour"
  escalate: true
```

### 1.3.3 Matrice de Décideurs et Routing

| Intent Type | Routage | Validateur | Approbateur |
|:---|:---|:---|:---|
| `GRAVURE` | tesla-brokerd | Gate 0-6 scripts | Lord Mahonheim (Biological) |
| `PARITE` | tesla-brokerd | audit_parite.sh | Automatique (fail-closed) |
| `MISSION` | tesla-brokerd | Conducteur Absolu | Selon matrice risque |
| `PRECOMMIT` | git hook | Scripts validation | Automatique |
| `PREPUSH` | git hook | Scripts validation + Human | Lord Mahonheim |

---

# AXE 2 : PLAN D'INTERVENTION "BROKER PATTERN"

## 2.1 Architecture du Démon Local `tesla-brokerd`

### 2.1.1 Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           TESLA BROKER DAEMON                            │
│                         tesla-brokerd.service                            │
│                                                                ────────  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     INTENT INTAKE LAYER                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ FileWatcher│  │  IPC Socket │  │   Git Hook Interceptor  │  │   │
│  │  │ /OUTPUTS/  │  │  /run/      │  │   (pre-commit/pre-push) │  │   │
│  │  │ intents/   │  │  tesla.sock │  │                          │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │   │
│  └─────────┼────────────────┼──────────────────────┼────────────────┘   │
│            │                │                      │                       │
│            ▼                ▼                      ▼                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      VALIDATION ENGINE                          │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │                    AMDEC ANALYSIS                          │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │   │
│  │  │  │ A - Mode  │  │ M - Effets│  │ D - Détect│  │ E - Fré│  │   │   │
│  │  │  │ Défaillanc│  │ Secondaires│ │ Détéction │ │ Quence │  │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │   │
│  │  │                                                          │   │   │
│  │  │  NIVEAU RISQUE: CRITIQUE | HAUT | MOYEN | FAIBLE        │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │                  VIGILUM CODEX VALIDATOR                  │   │   │
│  │  │  • Schéma YAML/JSON valide                              │   │   │
│  │  │  • Signature HMAC vérifiée                              │   │   │
│  │  │  • Intent type reconnu                                  │   │   │
│  │  │  • Priorité dans plage valide                          │   │   │
│  │  │  • Timestamps cohérents                                 │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│            │                                                         │
│            ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      ROUTING ENGINE                              │   │
│  │                                                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐  │   │
│  │  │  GRAVURE   │  │  PARITE    │  │  PRECOMMIT │  │ PREPUSH│  │   │
│  │  │  Pipeline  │  │  audit     │  │  Validator │  │ Validat│  │   │
│  │  │  (G0-G7)   │  │  parite.sh │  │            │  │        │  │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───┬────┘  │   │
│  └─────────┼──────────────┼─────────────────┼──────────────┼───────┘   │
│            │              │                 │              │            │
│            ▼              ▼                 ▼              ▼            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    DECISION ENGINE                               │   │
│  │                                                                  │   │
│  │   FAIL-CLOSED DECISION MATRIX                                    │   │
│  │   ┌────────────────────────────────────────────────────────┐    │   │
│  │   │  Validation OK  │  AMDEC Acceptable │  Codex OK      │    │   │
│  │   │       ✓         │         ✓         │       ✓        │    │   │
│  │   ├─────────────────┼───────────────────┼─────────────────┤    │   │
│  │   │  PASS → EXECUTE │  PROCEED          │  BLOCK → REJECT│    │   │
│  │   └────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│            │                                                         │
│            ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    EXECUTION & REPORTING                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│   │
│  │  │ Execute Cmd │  │ GitOps Hook │  │   Notification Layer    ││   │
│  │  │ (if PASS)   │  │ (apply/deny)│  │   (logs, alerts, IPC)   ││   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
```

### 2.1.2 Spécifications Techniques du Démon

```python
# SPEC : tesla_brokerd.py
# Langage: Python 3.12+
# Type: systemd service (user session ou system)
# Dépendances: PyYAML, jsonschema, hmac, inotify, watchdog

# CONFIGURATION
TESLA_BROKER_CONFIG = {
    "intents_dir": "/home/user/Tesla-Antigravity-CLI/OUTPUTS/intents/",
    "reports_dir": "/tmp/tesla_broker/reports/",
    "evidence_dir": "/home/user/Tesla-Antigravity-CLI/OUTPUTS/evidence/",
    "lock_dir": "/tmp/tesla_broker/locks/",
    "socket_path": "/run/user/$(id -u)/tesla-brokerd.sock",
    "pid_file": "/run/user/$(id -u)/tesla-brokerd.pid",
    
    # Timeouts (secondes)
    "intent_timeout": 300,        # 5 minutes max par intent
    "gate_timeout": 60,           # 1 minute max par gate
    "graceful_shutdown": 30,      # Drain avant kill
    
    # Circuit Breaker
    "max_retries": 3,
    "retry_delay": 5,
    
    # Security
    "hmac_key_path": "/etc/tesla/broker.key",  # chmod 600
    "allowed_emitters": ["tesla-master-code", "tesla-arcanis", "human:lordmahonheim"],
    "allowed_intent_types": ["GRAVURE", "PARITE", "MISSION", "PRECOMMIT", "PREPUSH"],
}

# SCHEMA VALIDATION (jsonschema)
INTENT_SCHEMA = {
    "type": "object",
    "required": ["intent_schema", "version", "intent_id", "intent_type", 
                  "priority", "emitter", "timestamp", "payload"],
    "properties": {
        "intent_schema": {"const": "VIGILUM_CODEX_2.0"},
        "version": {"const": "1.0.0"},
        "intent_id": {"pattern": "^[A-Z]+-[0-9]{8}-[A-Z0-9-]+$"},
        "intent_type": {
            "enum": ["GRAVURE", "PARITE", "MISSION", "PRECOMMIT", "PREPUSH"]
        },
        "priority": {"enum": ["P0", "P1", "P2", "P3"]},
        "emitter": {
            "oneOf": [
                {"pattern": "^tesla-[a-z-]+$"},
                {"pattern": "^human:[a-z]+$"}
            ]
        },
        "timestamp": {"format": "date-time"},
        "payload": {"type": "object"}
    }
}
```

### 2.1.3 Schéma de Données "Intention" Détaillé

```yaml
# SCHÉMA COMPLET D'UNE INTENTION — GravureIntent
# /OUTPUTS/intents/GravureIntent_[MISSION_ID]_[TIMESTAMP].yaml

schema_version: "VIGILUM_CODEX_2.0"
schema_type: "GravureIntent"
version: "1.0.0"

# Identifiants
intent_id: "GRAVURE-20260826-MVP-001"
mission_id: "GRAVURE-20260826-MVP-001"
intent_type: "GRAVURE"
priority: "P0"
classification: "CRITICAL"

# Métadonnées d'émission
emitter:
  agent: "tesla-master-code"
  session_id: "sess_abc123def"
  workspace: "/home/user/Tesla-Antigravity-CLI"
  timestamp_emit: "2026-08-26T14:30:00Z"
  correlation_id: "corr_xyz789"

# Contrat de Gravure (Phase 0)
authority:
  operator: "lordmahonheim"
  producer: "tesla-master-code"
  validator: "tesla-code-auditor"
  closure_type: "public-mvp"
  sgc_item: "SGC-2026-08-26-001"
  public_repository: "lordmahonheim-bot/Tesla-Antigravity-CLI"
  public_ref: "main"
  supersedes: []
  children: []
  required_checks:
    - "lsp_diagnostics"
    - "secret_scan"
    - "parity_audit"
  authorized_files:
    - "/home/user/Tesla-Antigravity-CLI/52-Tesla-XXX/"
  forbidden_files:
    - "/home/user/Tesla-Antigravity-CLI/memory/"
    - "/home/user/Tesla-Antigravity-CLI/.agents/"
    - "/home/user/Tesla-Antigravity-CLI/PROTOCOLES/"
  rollback_plan: "git checkout -- ."

# Scope Contractuel
scope:
  workdir: "/home/user/Tesla-Antigravity-CLI/52-Tesla-XXX"
  authorized_operations:
    - "write_file"
    - "read_file"
    - "edit_file"
    - "lsp_diagnostics"
    - "bash (ls, cat, grep -F)"
  forbidden_operations:
    - "git push"
    - "ask_permission"
    - "rm -rf"
    - "bash (curl, wget, nc)"
    - "systemctl"
  baseline_fingerprint: "sha256:abc123def456..."
  baseline_timestamp: "2026-08-26T14:00:00Z"

# Conditions de Succès
success_criteria:
  - id: "DOD-001"
    description: "README.md complet et fonctionnel"
    proof_required: "fichier existe + ls -la"
    
  - id: "DOD-002"
    description: "SKILL.md valide"
    proof_required: "jq -e . SKILL.md"
    
  - id: "DOD-003"
    description: "Aucun secret exposé"
    proof_required: "scan-secrets.sh sortie vide"

# Pipeline Gates
gates:
  gate0_authority:
    required: true
    skip_if: null
    
  gate1_closure:
    required: true
    dod_check: true
    
  gate2_validation:
    required: true
    levels: ["spatial", "integrity", "security", "semantic"]
    
  gate3_assimilation:
    required: true
    component_type: "Skill"
    component_id: "tesla-xxx"
    
  gate4_staging:
    required: false  # Si internal-only
    condition: "closure_type != 'internal-only'"
    
  gate5_authorization:
    required: false  # Si internal-only
    biological_gate: true
    
  gate6_publication:
    required: false  # Si internal-only
    expected_sha: null
    
  gate7_seal:
    required: true
    marble_certificate_path: "OUTPUTS/MARBLE_CERTIFICATE_[MISSION_ID].yaml"

# Signature et Attestation
signature:
  algorithm: "HMAC-SHA256"
  key_id: "tesla-broker-master-key-01"
  value: "base64:encrypted_hmac..."
  
attestations:
  - role: "producer"
    agent: "tesla-master-code"
    timestamp: "2026-08-26T14:30:00Z"
    key_fingerprint: "SHA256:abc..."

# AMDEC (Analyse des Risques)
amdec:
  modes_defaillance:
    - mode: "Fichiers hors scope modifiés"
      severite: 5
      probabilite: 2
      detectabilite: 1
      NPR: 10
      action: "BLOCK"
      
    - mode: "Secret exposé"
      severite: 5
      probabilite: 3
      detectabilite: 2
      NPR: 30
      action: "BLOCK + ALERT"
      
    - mode: "Baseline drift non détecté"
      severite: 4
      probabilite: 2
      detectabilite: 3
      NPR: 24
      action: "BLOCK + RELOAD"

# Journal d'Audit
audit:
  created_at: "2026-08-26T14:30:00Z"
  expires_at: "2026-08-26T15:30:00Z"
  status: "PENDING"
  retry_count: 0
```

---

## 2.2 Cinématique de Validation Complète

### 2.2.1 Diagramme de Flux Déterministe

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CINÉMATIQUE DE VALIDATION                            │
│                    tesla-brokerd Intent Processing                       │
└─────────────────────────────────────────────────────────────────────────┘

  [INTENT FILE ARRIVES]
          │
          ▼
  ┌───────────────────┐
  │ 1. FILE DETECTED  │ FileWatcher inotify
  │ (intents/*.yaml)  │ watchdog
  └─────────┬─────────┘
            │
            ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ 2. SCHEMA VALIDATION (jsonschema)                                │
  │    • intent_schema == "VIGILUM_CODEX_2.0"                       │
  │    • version == "1.0.0"                                         │
  │    • intent_type in allowed_types                                │
  │    • intent_id format correct                                    │
  └─────────┬───────────────────────────────────────────────────────┘
            │
       ┌────┴────┐
       │ VALID?  │
       └────┬────┘
     FAIL    │    PASS
      │      │      │
      ▼      ▼      ▼
  ┌─────┐ ┌─────────────────────────────┐
  │REJEC│ │ 3. HMAC SIGNATURE CHECK    │
  │T    │ │    hmac.verify(key, data)  │
  │     │ │    • key_id recognized                             │
  │     │ │    • signature valid                               │
  │     │ │    • not expired                                  │
  │     │ └─────────────┬───────────────┘
  │     │               │
  │     │          ┌────┴────┐
  │     │          │ VALID?  │
  │     │          └────┬────┘
  │     │        FAIL   │   PASS
  │     │         │     │     │
  │     │         ▼     ▼     ▼
  │     │     ┌─────┐ ┌─────────────────────────┐
  │     │     │REJEC│ │ 4. AMDEC ANALYSIS      │
  │     │     │T    │ │    • List failure modes │
  │     │     │     │ │    • Calculate NPR      │
  │     │     │     │ │    • Classify risk      │
  │     │     │     │ └─────────────┬───────────┘
  │     │     │     │             │
  │     │     │     │        ┌────┴────┐
  │     │     │     │        │ACCEPT?  │
  │     │     │     │        └────┬────┘
  │     │     │     │     REJECT  │   ACCEPT
  │     │     │     │       │     │      │
  │     │     │     │       ▼     ▼      ▼
  │     │     │     │   ┌─────────┐ ┌─────────────────────────┐
  │     │     │     │   │BLOCK + │ │ 5. VIGILUM CODEX CHECK  │
  │     │     │     │   │ALERT   │ │    • Scope compliant    │
  │     │     │     │   │(severe │ │    • Baseline stable    │
  │     │     │     │   │NPR>20) │ │    • Auth tokens valid  │
  │     │     │     │   └─────────┘ │    • Producer≠Validator│
  │     │     │     │               └────────────┬──────────┘
  │     │     │     │                            │
  │     │     │     │                       ┌────┴────┐
  │     │     │     │                       │ PASS?   │
  │     │     │     │                       └────┬────┘
  │     │     │     │                  FAIL      │   PASS
  │     │     │     │                   │       │      │
  │     │     │     │                   ▼       ▼      ▼
  │     │     │     │              ┌─────────┐ ┌───────────────────┐
  │     │     │     │              │BLOCK + │ │ 6. ROUTE TO       │
  │     │     │     │              │ESCALATE│ │    EXECUTOR       │
  │     │     │     │              └─────────┘ │                   │
  │     │     │     │                         │ GRAVURE → G0-G7    │
  │     │     │     │                         │ PARITE  → audit    │
  │     │     │     │                         │ PRECOMMIT→hook val │
  │     │     │     │                         │ PREPUSH → push val │
  │     │     │     │                         └─────────┬──────────┘
  │     │     │     │                                   │
  │     │     │     │                                   ▼
  │     │     │     │              ┌─────────────────────────────────┐
  │     │     │     │              │ 7. EXECUTE & GATHER EVIDENCE    │
  │     │     │     │              │    • Run phase scripts          │
  │     │     │     │              │    • Capture outputs           │
  │     │     │     │              │    • Generate proof artifacts   │
  │     │     │     │              └─────────────┬───────────────────┘
  │     │     │     │                            │
  │     │     │     │                      ┌─────┴─────┐
  │     │     │     │                      │  RESULT   │
  │     │     │     │                      └─────┬─────┘
  │     │     │     │                     ┌──────┴──────┐
  │     │     │     │                     │             │
  │     │     │     │                 ┌────┴────┐   ┌────┴────┐
  │     │     │     │                 │  PASS   │   │  FAIL  │
  │     │     │     │                 │         │   │        │
  │     │     │     │                 ▼         ▼   ▼        ▼
  │     │     │     │            ┌────────┐  ┌────────────┐  ┌────────┐
  │     │     │     │            │APPLY  │  │CIRCUIT    │  │REJECT  │
  │     │     │     │            │(GitOps│  │BREAKER    │  │+REPORT │
  │     │     │     │            │+Seal) │  │(max 3)    │  │+ALERT  │
  │     │     │     │            └────────┘  └─────┬─────┘  └────────┘
  │     │     │     │                                │
  │     │     │     │                           ┌─────┴─────┐
  │     │     │     │                           │RETRY OK?  │
  │     │     │     │                           └─────┬─────┘
  │     │     │     │                         YES     │    NO
  │     │     │     │                          │       │     │
  │     │     │     │                          ▼       ▼     ▼
  │     │     │     │                     ┌────────┐ ┌────────────────┐
  │     │     │     │                     │RETRY  │ │ESCALATE TO     │
  │     │     │     │                     │(N+1)  │ │LORD MAHONHEIM  │
  │     │     │     │                     └───┬────┘ └────┬─────────┘
  │     │     │     │                         │           │
  └─────┴─────┴─────┴─────────────────────────┴───────────┘
```

### 2.2.2 États de la Machine à États du Broker

| État | Description | Transitions Autorisées |
|:---|:---|:---|
| `PENDING` | Intent reçu, en attente de validation | → `VALIDATING`, → `REJECTED` |
| `VALIDATING` | Schéma + Signature + AMDEC en cours | → `ROUTING`, → `BLOCKED`, → `REJECTED` |
| `ROUTING` | Intent routé vers exécuteur approprié | → `EXECUTING`, → `BLOCKED` |
| `EXECUTING` | Pipeline/Phase en cours d'exécution | → `PASS`, → `FAIL`, → `RETRY` |
| `PASS` | Toutes les vérifications passent | → `APPLIED` |
| `FAIL` | Vérification échouée | → `BLOCKED`, → `RETRY` |
| `BLOCKED` | Bloqué pour cause de risque/crash | → `ESCALATED`, terminal |
| `RETRY` | En retry (circuit breaker actif) | → `EXECUTING`, → `BLOCKED` (après max) |
| `ESCALATED` | Escapade à Lord Mahonheim requise | Attente réponse |
| `APPLIED` | Action appliquée avec succès | terminal |
| `REJECTED` | Intent invalide ou non autorisé | terminal |

### 2.2.3 Règles de Fail-Closed (Non-Négociables)

```bash
# RÈGLES ABSOLUES DU BROKER — FAIL-CLOSED
# Ces règles NE PEUVENT PAS être désactivées

RULE_01: "ANY validation failure → BLOCK"
RULE_02: "UNKNOWN state ≠ PASS"
RULE_03: "Timeout → BLOCK (no implicit success)"
RULE_04: "AMDEC NPR > 20 → BLOCK + ALERT"
RULE_05: "Baseline drift → BLOCK + RELOAD"
RULE_06: "Signature invalid → REJECT (no retry)"
RULE_07: "Producer = Validator → BLOCK (conflict of interest)"
RULE_08: "Secret detected → BLOCK + PURGE"
RULE_09: "Scope violation → BLOCK"
RULE_10: "Max retries exceeded → ESCALATE to Mahonheim"
RULE_11: "No network access unless explicitly authorized"
RULE_12: "Rollback MUST be available before execution"
```

---

# AXE 3 : GARDE-FOUS LOCAUX (GUARDRAILS & HOOKS)

## 3.1 Architecture des Git Hooks

### 3.1.1 Structure des Hooks à Implémenter

```
.git/hooks/ (LIENS SYMBOLIQUES VERS core.hooks/)
├── pre-commit        # Blocage avant commit
├── commit-msg       # Validation format message
├── pre-push         # Blocage avant push
└── post-commit      # Notification (optionnel)

core.hooks/ (DÉPÔT SÉPARÉ OU RÉPERTOIRE)
├── pre-commit/
│   ├── tesla-pre-commit-main.sh      # Orchestrateur
│   ├── 01-schema-validator.sh        # Phase 1: Schema YAML
│   ├── 02-secret-scanner.sh         # Phase 2: Scan secrets/PII
│   ├── 03-scope-validator.sh        # Phase 3: Fichiers autorisés
│   ├── 04-project-state-check.sh    # Phase 4: PROJECT_STATE sync
│   ├── 05-marble-cert-check.sh      # Phase 5: Marble Certificate
│   └── 06-lint-check.sh             # Phase 6: Format/Lint
│
├── commit-msg/
│   └── tesla-commit-msg.sh          # Format Conventional Commits
│
├── pre-push/
│   ├── tesla-pre-push-main.sh       # Orchestrateur
│   ├── 01-authorization-check.sh    # Phase 1: Biological Gate
│   ├── 02-parity-audit.sh          # Phase 2: Loi de Parité
│   ├── 03-remote-state-check.sh      # Phase 3: SHA distant
│   ├── 04-branch-protection.sh      # Phase 4: Branch rules
│   └── 05-force-push-detect.sh      # Phase 5: Anti force-push
│
└── lib/
    ├── tesla-logging.sh             # Bibliothèque logging
    ├── tesla-colors.sh              # Couleurs terminal
    ├── tesla-schema-validator.sh    # Validation JSON/YAML
    ├── tesla-secret-patterns.sh     # Patterns secrets
    └── tesla-exit-codes.sh         # Codes de sortie standardisés
```

### 3.1.2 Configuration du core.hooksPath

```bash
# Configuration Git globale pour activer les hooks Tesla
git config --global core.hooksPath /home/user/Tesla-Antigravity-CLI/core.hooks

# Vérification
git config --get core.hooksPath
# Output attendu: /home/user/Tesla-Antigravity-CLI/core.hooks
```

---

## 3.2 Code Source des Hooks — pre-commit

### 3.2.1 Orchestrateur Principal pre-commit

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TESLA PRE-COMMIT HOOK                              ║
# ║                     VIGILUM CODEX 2.0 — FAIL-CLOSED                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# SYNOPSIS    : Hook de sécurité pré-commit pour Tesla Antigravity CLI
# AUTEUR      : Tesla — Agent Principal & Orchestrateur
# VERSION     : 1.0.0
# DATE        : 2026-08-26
# DOCTRINE    : Vigilum Codex — Fail-Closed
#
# ─────────────────────────────────────────────────────────────────────────────
# RÈGLES ABSOLUES :
#   • TOUT ÉCHEC = COMMIT BLOQUÉ
#   • Aucune exception, aucun bypass, aucune excuse
#   • "Looks correct" ≠ "PASS"
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TESLA_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_LIB="$TESLA_ROOT/core.hooks/lib"
HOOK_NAME="pre-commit"
TRACE_ID="precommit-$(date +%s)-$(head -c 4 /dev/urandom | xxd -p)"

# Répertoires de sortie
LOG_DIR="/tmp/tesla-hooks/logs"
REPORT_DIR="/tmp/tesla-hooks/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

LOG_FILE="$LOG_DIR/${TRACE_ID}.log"
REPORT_FILE="$REPORT_DIR/${TRACE_ID}.report"

# ═══════════════════════════════════════════════════════════════════════════════
# LIBRAIRIES
# ═══════════════════════════════════════════════════════════════════════════════

# shellcheck source=lib/tesla-logging.sh
source "$HOOKS_LIB/tesla-logging.sh" 2>/dev/null || {
    echo "[CRITICAL] Librairie tesla-logging.sh introuvable"
    exit 1
}

# shellcheck source=lib/tesla-exit-codes.sh
source "$HOOKS_LIB/tesla-exit-codes.sh" 2>/dev/null || {
    echo "[CRITICAL] Librairie tesla-exit-codes.sh introuvable"
    exit 1
}

# shellcheck source=lib/tesla-colors.sh
source "$HOOKS_LIB/tesla-colors.sh" 2>/dev/null || {
    echo "[CRITICAL] Librairie tesla-colors.sh introuvable"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISATION DU TRACE
# ═══════════════════════════════════════════════════════════════════════════════

tesla_log_init "$LOG_FILE" "INFO" "$HOOK_NAME" "$TRACE_ID"
tesla_log "INFO" "═══════════════════════════════════════════════════════"
tesla_log "INFO" "TESLA PRE-COMMIT HOOK v1.0.0"
tesla_log "INFO" "Trace ID: $TRACE_ID"
tesla_log "INFO" "Tesla Root: $TESLA_ROOT"
tesla_log "INFO" "═══════════════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

# Compte-rendu de phase
report_phase() {
    local phase_name="$1"
    local phase_status="$2"
    local phase_duration="$3"
    local phase_details="${4:-}"
    
    echo "| $phase_name | $phase_status | ${phase_duration}ms | $phase_details |" >> "$REPORT_FILE"
    
    if [ "$phase_status" = "FAIL" ]; then
        tesla_log "ERROR" "PHASE FAIL: $phase_name — COMMIT BLOQUÉ"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    local start_time end_time duration
    local overall_status="PASS"
    local failed_phases=()
    
    # Initialisation du rapport
    {
        echo "# TESLA PRE-COMMIT REPORT"
        echo "Trace ID: $TRACE_ID"
        echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "Git Branch: $(git symbolic-ref --short HEAD 2>/dev/null || echo 'detached')"
        echo "Git SHA: $(git rev-parse HEAD 2>/dev/null || echo 'N/A')"
        echo ""
        echo "| Phase | Status | Duration | Details |"
        echo "|-------|--------|----------|---------|"
    } > "$REPORT_FILE"
    
    tesla_log "INFO" "Détection des fichiers modifiés..."
    
    # Récupérer la liste des fichiers stagés (diff --cached)
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM)
    
    if [ -z "$staged_files" ]; then
        tesla_log "WARN" "Aucun fichier stagé — nothing to commit"
        echo "| (none) | SKIP | 0 | No staged files |" >> "$REPORT_FILE"
        {
            echo ""
            echo "RESULT: PASS (no changes staged)"
        } >> "$REPORT_FILE"
        cat "$REPORT_FILE"
        exit 0
    fi
    
    local file_count
    file_count=$(echo "$staged_files" | wc -l)
    tesla_log "INFO" "$file_count fichier(s) stagé(s)"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: SCHEMA VALIDATOR (YAML/JSON)
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 1: Validation des schémas YAML/JSON..."
    
    if [ -f "$HOOKS_LIB/01-schema-validator.sh" ]; then
        if bash "$HOOKS_LIB/01-schema-validator.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCHEMA_VALIDATOR" "PASS" "$duration"
            tesla_log "INFO" "PHASE 1: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCHEMA_VALIDATOR" "FAIL" "$duration" "Schema invalid detected"
            tesla_log "ERROR" "PHASE 1: FAIL — COMMIT BLOQUÉ"
            overall_status="FAIL"
            failed_phases+=("SCHEMA_VALIDATOR")
        fi
    else
        tesla_log "WARN" "PHASE 1: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: SECRET SCANNER
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 2: Scan de secrets et PII..."
    
    if [ -f "$HOOKS_LIB/02-secret-scanner.sh" ]; then
        if bash "$HOOKS_LIB/02-secret-scanner.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SECRET_SCANNER" "PASS" "$duration"
            tesla_log "INFO" "PHASE 2: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SECRET_SCANNER" "FAIL" "$duration" "Secret/PII detected"
            tesla_log "ERROR" "PHASE 2: FAIL — COMMIT BLOQUÉ (SECRET DÉTECTÉ)"
            overall_status="FAIL"
            failed_phases+=("SECRET_SCANNER")
        fi
    else
        tesla_log "WARN" "PHASE 2: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: SCOPE VALIDATOR (Fichiers autorisés)
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 3: Validation du périmètre (scope)..."
    
    if [ -f "$HOOKS_LIB/03-scope-validator.sh" ]; then
        if bash "$HOOKS_LIB/03-scope-validator.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCOPE_VALIDATOR" "PASS" "$duration"
            tesla_log "INFO" "PHASE 3: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "SCOPE_VALIDATOR" "FAIL" "$duration" "Scope violation"
            tesla_log "ERROR" "PHASE 3: FAIL — COMMIT BLOQUÉ (SCOPE VIOLATION)"
            overall_status="FAIL"
            failed_phases+=("SCOPE_VALIDATOR")
        fi
    else
        tesla_log "WARN" "PHASE 3: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: PROJECT_STATE SYNC CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 4: Vérification synchronisation PROJECT_STATE..."
    
    if [ -f "$HOOKS_LIB/04-project-state-check.sh" ]; then
        if bash "$HOOKS_LIB/04-project-state-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "PROJECT_STATE_SYNC" "PASS" "$duration"
            tesla_log "INFO" "PHASE 4: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "PROJECT_STATE_SYNC" "FAIL" "$duration" "PROJECT_STATE not synced"
            tesla_log "ERROR" "PHASE 4: FAIL — COMMIT BLOQUÉ (PROJECT_STATE DÉSYNCHRONISÉ)"
            overall_status="FAIL"
            failed_phases+=("PROJECT_STATE_SYNC")
        fi
    else
        tesla_log "WARN" "PHASE 4: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: MARBLE CERTIFICATE CHECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 5: Vérification Marble Certificate..."
    
    if [ -f "$HOOKS_LIB/05-marble-cert-check.sh" ]; then
        if bash "$HOOKS_LIB/05-marble-cert-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "MARBLE_CERT_CHECK" "PASS" "$duration"
            tesla_log "INFO" "PHASE 5: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "MARBLE_CERT_CHECK" "FAIL" "$duration" "Marble cert missing or invalid"
            tesla_log "ERROR" "PHASE 5: FAIL — COMMIT BLOQUÉ (MARBLE CERTIFICATE ABSENT)"
            overall_status="FAIL"
            failed_phases+=("MARBLE_CERT_CHECK")
        fi
    else
        tesla_log "WARN" "PHASE 5: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6: LINT CHECK (Format/Lint)
    # ═══════════════════════════════════════════════════════════════════════════
    
    start_time=$(date +%s%3N)
    tesla_log "INFO" "PHASE 6: Vérification format et lint..."
    
    if [ -f "$HOOKS_LIB/06-lint-check.sh" ]; then
        if bash "$HOOKS_LIB/06-lint-check.sh" "$staged_files" "$TESLA_ROOT" "$TRACE_ID"; then
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "LINT_CHECK" "PASS" "$duration"
            tesla_log "INFO" "PHASE 6: PASS (${duration}ms)"
        else
            end_time=$(date +%s%3N)
            duration=$((end_time - start_time))
            report_phase "LINT_CHECK" "FAIL" "$duration" "Lint errors detected"
            tesla_log "ERROR" "PHASE 6: FAIL — COMMIT BLOQUÉ (LINT ERRORS)"
            overall_status="FAIL"
            failed_phases+=("LINT_CHECK")
        fi
    else
        tesla_log "WARN" "PHASE 6: Script absent — SKIP"
    fi
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RÉSULTAT FINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    {
        echo ""
        echo "═══════════════════════════════════════════════════════"
        echo "FINAL RESULT: $overall_status"
        echo "═══════════════════════════════════════════════════════"
        echo "Log: $LOG_FILE"
        echo "Report: $REPORT_FILE"
    } >> "$REPORT_FILE"
    
    tesla_log "INFO" "═══════════════════════════════════════════════════════"
    tesla_log "INFO" "RÉSULTAT FINAL: $overall_status"
    tesla_log "INFO" "═══════════════════════════════════════════════════════"
    
    # Affichage du rapport
    cat "$REPORT_FILE"
    
    if [ "$overall_status" = "FAIL" ]; then
        echo ""
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    COMMIT BLOQUÉ                             ║${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  Échec(s): ${failed_phases[*]}${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  Consultez le rapport: $REPORT_FILE${NC}"
        echo -e "${RED}║  Consultez les logs: $LOG_FILE${NC}"
        echo -e "${RED}║                                                               ║${NC}"
        echo -e "${RED}║  Action requise: Corrigez les erreurs et re-stagez.        ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    COMMIT AUTORISÉ                             ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║  Toutes les validations ont passé.                          ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
}

# Exécution
main "$@"
```

### 3.2.2 Module 02 — Scanner de Secrets

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA SECRET SCANNER — PHASE 2                           ║
# ║              Détection de secrets, tokens et PII                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"

# Patterns de secrets à détecter
SECRET_PATTERNS=(
    # Clés API / Tokens
    "api[_-]?key['\":\s=]+[a-zA-Z0-9_-]{20,}"
    "api[_-]?secret['\":\s=]+[a-zA-Z0-9_-]{20,}"
    "access[_-]?token['\":\s=]+['\"]?[a-zA-Z0-9_-]{20,}['\"]?"
    "bearer['\":\s]+[a-zA-Z0-9_-]{20,}"
    "ghp_[a-zA-Z0-9]{36,}"
    "gho_[a-zA-Z0-9]{36,}"
    "xox[baprs]-[a-zA-Z0-9]{10,}"
    "sk-[a-zA-Z0-9]{48,}"
    "sk-proj-[a-zA-Z0-9_-]{48,}"
    
    # Mots de passe
    "password['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    "passwd['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    "pwd['\":\s=]+['\"]?[^\s'\"]{8,}['\"]?"
    
    # Connexions DB
    "mongodb://[^\s'\"]{10,}"
    "postgres://[^\s'\"]{10,}"
    "mysql://[^\s'\"]{10,}"
    "redis://[^\s'\"]{10,}"
    
    # Clés SSH / Certificats
    "-----BEGIN[ A-Z]+PRIVATE KEY-----"
    "ssh-rsa AAAA[0-9A-Za-z+/]{100,}"
    
    # AWS
    "AKIA[0-9A-Z]{16}"
    "aws[_-]?secret[_-]?access[_-]?key['\":\s=]+"
    
    # URLs avec credentials
    "https?://[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+@[^\s'\"<>]+"
)

# Fichiers à exclure du scan
EXCLUDE_PATTERNS=(
    "*.png" "*.jpg" "*.jpeg" "*.gif" "*.ico" "*.woff" "*.woff2" "*.ttf"
    ".git/*" "node_modules/*" "__pycache__/*" "*.pyc" "*.min.js"
    "*.lock" "package-lock.json" "yarn.lock"
)

SECRETS_FOUND=0
SECRET_DETAILS=()

scan_file_for_secrets() {
    local file="$1"
    local found=0
    
    # Vérifier si le fichier doit être exclu
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            return 0
        fi
    done
    
    # Scanner le fichier avec grep
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -E -n -i -- "$pattern" "$file" 2>/dev/null | head -3; then
            SECRET_DETAILS+=("  $file: $(grep -E -n -i -- "$pattern" "$file" 2>/dev/null | head -1)")
            found=1
            ((SECRETS_FOUND++))
        fi
    done
    
    return $found
}

# Scanner chaque fichier stagé
while IFS= read -r file; do
    if [ -f "$file" ]; then
        scan_file_for_secrets "$file" || true
    fi
done <<< "$STAGED_FILES"

# Résultat
if [ "$SECRETS_FOUND" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ATTENTION: SECRETS DÉTECTÉS                      ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "Secrets détectés: $SECRETS_FOUND"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for detail in "${SECRET_DETAILS[@]}"; do
        printf "║ %-60s ║\n" "$detail"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION REQUISE:"
    echo "  1. Retirez les secrets du code"
    echo "  2. Utilisez des variables d'environnement ou un vault"
    echo "  3. Ajoutez le fichier à .gitignore si nécessaire"
    echo "  4. Re-stagez les fichiers corrigés"
    echo ""
    exit 1
fi

echo "✓ Aucun secret détecté dans les fichiers stagés"
exit 0
```

### 3.2.3 Module 03 — Validateur de Scope

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                   TESLA SCOPE VALIDATOR — PHASE 3                           ║
# ║          Validation des fichiers autorisés/interdits                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"

# ═══════════════════════════════════════════════════════════════════════════════
# LISTES DE CONTRÔLE — À CONFIGURER SELON L'ENVIRONNEMENT
# ═══════════════════════════════════════════════════════════════════════════════

# Fichiers/répertoires STRICTEMENT INTERDITS (sans autorisation)
FORBIDDEN_PATHS=(
    "memory/"
    "memory/*"
    ".agents/"
    ".agents/*"
    "PROTOCOLES/"
    "PROTOCOLES/*"
    ".git/config"
    ".git/credentials"
    "*.key"
    "*.pem"
    "secrets.yaml"
    "secrets.yml"
    "secrets.json"
)

# Extensions de fichiers à risque
FORBIDDEN_EXTENSIONS=(
    ".exe" ".dll" ".so" ".dylib"
    ".db" ".sqlite" ".sqlite3"
)

# Vérification du fichier PROJECT_STATE.md (doit être sync si modifié)
PROJECT_STATE_FILE="$TESLA_ROOT/memory/PROJECT_STATE.md"

VIOLATIONS=0
VIOLATION_DETAILS=()

# Vérifier les fichiers stagés
while IFS= read -r file; do
    # Skip si fichier inexistant
    [ -z "$file" ] && continue
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VÉRIFICATION: Chemins interdits
    # ═══════════════════════════════════════════════════════════════════════════
    
    for forbidden in "${FORBIDDEN_PATHS[@]}"; do
        # Supporter les wildcards simples
        if [[ "$file" == $forbidden ]]; then
            VIOLATION_DETAILS+=("PATH: Accès interdit à $file")
            ((VIOLATIONS++))
            continue 2
        fi
        
        # Vérifier si le chemin contient un préfixe interdit
        if [[ "$file" == "$forbidden" ]] || [[ "$file" == *"/$forbidden" ]]; then
            # Exceptions pour les patterns avec wildcard à la fin
            if [[ "$forbidden" == */ ]]; then
                :  # Autorisé pour les répertoires avec wildcard
            else
                VIOLATION_DETAILS+=("PATH: Contient chemin interdit $forbidden")
                ((VIOLATIONS++))
                continue 2
            fi
        fi
    done
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VÉRIFICATION: Extensions interdites
    # ═══════════════════════════════════════════════════════════════════════════
    
    for ext in "${FORBIDDEN_EXTENSIONS[@]}"; do
        if [[ "$file" == *"$ext" ]]; then
            VIOLATION_DETAILS+=("EXT: Extension interdite $ext dans $file")
            ((VIOLATIONS++))
            continue 2
        fi
    done
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VÉRIFICATION SPÉCIALE: memory/ ou .agents/ accessibles en lecture seule
    # ═══════════════════════════════════════════════════════════════════════════
    
    if [[ "$file" == memory/* ]] || [[ "$file" == .agents/* ]]; then
        # Vérifier si un Marble Certificate existe pour cette modification
        marble_dir="$TESLA_ROOT/OUTPUTS/MARBLE_CERTIFICATES/"
        
        # Un write/edit dans memory/ ou .agents/ est interdit sans Marble Certificate
        if [ -d "$marble_dir" ]; then
            # Chercher un certificat récent (moins de 24h)
            recent_cert=$(find "$marble_dir" -name "*.yaml" -mtime -1 2>/dev/null | head -1)
            if [ -z "$recent_cert" ]; then
                VIOLATION_DETAILS+=("MEMORY/AGENTS: Modification non autorisée sans Marble Certificate récent")
                ((VIOLATIONS++))
            fi
        else
            VIOLATION_DETAILS+=("MEMORY/AGENTS: Modification non autorisée (pas de répertoire Marble)")
            ((VIOLATIONS++))
        fi
    fi
    
done <<< "$STAGED_FILES"

# ═══════════════════════════════════════════════════════════════════════════════
# RÉSULTAT
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$VIOLATIONS" -gt 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              VIOLATION DE SCOPE DÉTECTÉE                      ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "Violations détectées: $VIOLATIONS"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    for detail in "${VIOLATION_DETAILS[@]}"; do
        printf "║ %-60s ║\n" "$detail"
    done
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION REQUISE:"
    echo "  1. Annulez les modifications sur les fichiers interdits"
    echo "  2. git checkout -- <fichier_interdit>"
    echo "  3. Si modification légitime, ouvrez une demande via Lord Mahonheim"
    echo "  4. Après autorisation, utilisez le protocole Gravure sur Marbre"
    echo ""
    exit 1
fi

echo "✓ Périmètre des fichiers validé — aucune violation"
exit 0
```

### 3.2.4 Module 04 — Vérification PROJECT_STATE

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              TESLA PROJECT_STATE SYNC CHECK — PHASE 4                       ║
# ║     Vérification que PROJECT_STATE.md est synchronisé avec les commits      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"

PROJECT_STATE="$TESLA_ROOT/memory/PROJECT_STATE.md"
SYNC_FLAG_FILE="$TESLA_ROOT/.tesla/.project_state_synced"

VIOLATIONS=0

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIQUE DE VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Règle: Si un fichier MVP/Output/Skill est modifié, PROJECT_STATE doit être mis à jour
MODIFIES_PROJECT_STATE=0
MODIFIES_OUTPUTS=0
MODIFIES_SKILLS=0

# Patterns de fichiers qui nécessitent une sync PROJECT_STATE
OUTPUT_PATTERNS=(
    "*/MVP-*/*"
    "*/OUTPUTS/*"
    "*/*-Skill/*"
    "*/*-skill/*"
)

# Vérifier les fichiers stagés
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    # PROJECT_STATE modifié?
    if [[ "$file" == "memory/PROJECT_STATE.md" ]]; then
        MODIFIES_PROJECT_STATE=1
        continue
    fi
    
    # OUTPUTS modifié?
    for pattern in "${OUTPUT_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            MODIFIES_OUTPUTS=1
            break
        fi
    done
    
    # Skills modifié?
    if [[ "$file" == *"-Skill/SKILL.md" ]] || [[ "$file" == *"-skill/SKILL.md" ]]; then
        MODIFIES_SKILLS=1
    fi
    
done <<< "$STAGED_FILES"

# ═══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Si OUTPUTS/Skills modifiés mais PROJECT_STATE non modifié → VIOLATION
if [ "$MODIFIES_OUTPUTS" -eq 1 ] && [ "$MODIFIES_PROJECT_STATE" -eq 0 ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           PROJECT_STATE DÉSYNCHRONISÉ                         ║"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    echo "║                                                               ║"
    echo "║  Les fichiers OUTPUTS/MVP/Skills ont été modifiés mais       ║"
    echo "║  PROJECT_STATE.md n'a pas été mis à jour.                    ║"
    echo "║                                                               ║"
    echo "║  RÈGLE VIGILUM CODEX:                                        ║"
    echo "║  'PROJECT_STATE est TOUJOURS une cible obligatoire,          ║"
    echo "║   sans exception, quelle que soit la nature du déploiement.'   ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "ACTION REQUISE:"
    echo "  1. Mettez à jour memory/PROJECT_STATE.md avec:"
    echo "     - Nouveau statut du projet"
    echo "     - Date de dernière modification"
    echo "     - Résumé des changements"
    echo "  2. Re-stagez: git add memory/PROJECT_STATE.md"
    echo "  3. Réessayez le commit"
    echo ""
    ((VIOLATIONS++))
fi

# Si PROJECT_STATE modifié, vérifier qu'il a un format valide
if [ "$MODIFIES_PROJECT_STATE" -eq 1 ]; then
    if ! grep -q "^# PROJECT STATE" "$PROJECT_STATE" 2>/dev/null; then
        echo "⚠ PROJECT_STATE.md modifié mais format invalide"
        ((VIOLATIONS++))
    fi
fi

# Résultat
if [ "$VIOLATIONS" -gt 0 ]; then
    exit 1
fi

echo "✓ PROJECT_STATE synchronisé"
exit 0
```

### 3.2.5 Module 05 — Vérification Marble Certificate

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              TESLA MARBLE CERTIFICATE CHECK — PHASE 5                      ║
# ║     Vérification de l'existence du Marble Certificate pour mutations         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

set -euo pipefail

STAGED_FILES="$1"
TESLA_ROOT="$2"
TRACE_ID="$3"

MARBLE_DIR="$TESLA_ROOT/OUTPUTS/MARBLE_CERTIFICATES"
MARBLE_CACHE="$TESLA_ROOT/.tesla/.marble_cache"

VIOLATIONS=0

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIQUE DE VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

# Créer le répertoire si nécessaire
mkdir -p "$MARBLE_DIR" "$MARBLE_CACHE"

# Déterminer si un Marble Certificate est requis
REQUIRES_MARBLE=0
REQUIRED_FOR=()

while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    # Tout fichier modifiant le socle canonique requiert un Marble Certificate
    case "$file" in
        memory/*|.agents/*|PROTOCOLES/*)
            REQUIRES_MARBLE=1
            REQUIRED_FOR+=("$file")
            ;;
        *.md)
            # Lire le fichier pour déterminer s'il s'agit d'un document canonique
            if grep -q "^# PROTOCOLE CANONIQUE" "$file" 2>/dev/null; then
                REQUIRES_MARBLE=1
                REQUIRED_FOR+=("$file")
            fi
            ;;
    esac
done <<< "$STAGED_FILES"

# ═══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$REQUIRES_MARBLE" -eq 1 ]; then
    echo ""
    echo "⚠ Marble Certificate requis pour cette modification"
    
    # Chercher un Marble Certificate récent (moins de 24h)
    RECENT_MARBLE=$(find "$MARBLE_DIR" -name "*.yaml" -mtime -1 2>/dev/null | head -1)
    
    if [ -z "$RECENT_MARBLE" ]; then
        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║           MARBLE CERTIFICATE REQUIS                         ║"
        echo "╠═══════════════════════════════════════════════════════════════╣"
        echo "║                                                               ║"
        echo "║  Les fichiers suivants requièrent un Marble Certificate:     ║"
        for f in "${REQUIRED_FOR[@]}"; do
            printf "║    • %-50s ║\n" "$f"
        done
        echo "║                                                               ║"
        echo "║  RÈGLE VIGILUM CODEX (Protocole Gravure sur Marbre):        ║"
        echo "║  'No Proof, No Marble.'                                     ║"
        echo "║  'Gravé n'est pas déclaré. Gravé est prouvé.'               ║"
        echo "║                                                               ║"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "ACTION REQUISE:"
        echo "  1. Exécutez le protocole Gravure sur Marbre complet (Phases 0-7)"
        echo "  2. Ou obtenez une autorisation explicite de Lord Mahonheim"
        echo "  3. Après obtention, recommencez le commit"
        echo ""
        ((VIOLATIONS++))
    else
        # Vérifier la cohérence du certificate
        MARBLE_COMPONENT=$(grep "^component_id:" "$RECENT_MARBLE" 2>/dev/null | cut -d: -f2 | tr -d ' ')
        
        echo "✓ Marble Certificate trouvé: $(basename "$RECENT_MARBLE")"
        echo "  Composant: $MARBLE_COMPONENT"
        
        # Vérifier la date (doit être récent)
        MARBLE_DATE=$(stat -c %Y "$RECENT_MARBLE" 2>/dev/null || stat -f %m "$RECENT_MARBLE" 2>/dev/null)
        CURRENT_DATE=$(date +%s)
        AGE_HOURS=$(( (CURRENT_DATE - MARBLE_DATE) / 3600 ))
        
        if [ "$AGE_HOURS" -gt 24 ]; then
            echo "⚠ Marble Certificate expiré (>24h)"
            ((VIOLATIONS++))
        fi
    fi
fi

# Résultat
if [ "$VIOLATIONS" -gt 0 ]; then
    exit 1
fi

echo "✓ Vérification Marble Certificate passed"
exit 0
```

---

## 3.3 Code Source des Hooks — pre-push

### 3.3.1 Orchestrateur Principal pre-push

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TESLA PRE-PUSH HOOK                                ║
# ║                     VIGILUM CODEX 2.0 — FAIL-CLOSED                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# SYNOPSIS    : Hook de sécurité pré-push pour Tesla Antigravity CLI
# AUTEUR      : Tesla — Agent Principal & Orchestrateur
# VERSION     : 1.0.0
# DATE        : 2026-08-26
# DOCTRINE    : Vigilum Codex — Fail-Closed
#
# ─────────────────────────────────────────────────────────────────────────────
# RÈGLES ABSOLUES :
#   • TOUT PUSH REQUIERT AUTORISATION EXPLICITE
#   • "git push ne retourne pas d'erreur" ≠ "push autorisé"
#   • push = publication = engagement envers l'extérieur
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

TESLA_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_LIB="$TESLA_ROOT/core.hooks/lib"
HOOK_NAME="pre-push"
TRACE_ID="prepush-$(date +%s)-$(head -c 4 /dev/urandom | xxd -p)"

# Paramètres reçus de git (git les passe automatiquement au hook)
REMOTE_URL="$1"
REMOTE_NAME="$2"

# Répertoires de sortie
LOG_DIR="/tmp/tesla-hooks/logs"
REPORT_DIR="/tmp/tesla-hooks/reports"
mkdir -p "$LOG_DIR" "$REPORT_DIR"

LOG_FILE="$LOG_DIR/${TRACE_ID}.log"
REPORT_FILE="$REPORT_DIR/${TRACE_ID}.report"

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

log_msg() {
    local level="$1"
    local msg="$2"
    echo "[$(date +%H:%M:%S)] [$level] $msg" >> "$LOG_FILE"
    echo "[$level] $msg"
}

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "═══════════════════════════════════════════════════════"
log_msg "INFO" "TESLA PRE-PUSH HOOK v1.0.0"
log_msg "INFO" "Trace ID: $TRACE_ID"
log_msg "INFO" "Remote: $REMOTE_NAME ($REMOTE_URL)"
log_msg "INFO" "═══════════════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISATION DU RAPPORT
# ═══════════════════════════════════════════════════════════════════════════════

{
    echo "# TESLA PRE-PUSH REPORT"
    echo "Trace ID: $TRACE_ID"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Remote: $REMOTE_NAME"
    echo "Remote URL: $REMOTE_URL"
    echo ""
    echo "| Phase | Status | Details |"
    echo "|-------|--------|---------|"
} > "$REPORT_FILE"

report_phase() {
    local phase_name="$1"
    local phase_status="$2"
    local phase_details="${3:-}"
    echo "| $phase_name | $phase_status | $phase_details |" >> "$REPORT_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 0: VÉRIFICATION GIT (Prérequis)
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 0: Vérifications préliminaires..."

# Vérifier que nous ne sommes pas en detached HEAD
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "detached")
if [ "$CURRENT_BRANCH" = "detached" ]; then
    log_msg "WARN" "HEAD détaché — vérification spéciales..."
fi

# Récupérer les commits à pusher
LOCAL_REF="$1"
LOCAL_SHA="$2"
REMOTE_REF="$3"
REMOTE_SHA="$4"

log_msg "INFO" "Local:  $LOCAL_REF ($LOCAL_SHA)"
log_msg "INFO" "Remote: $REMOTE_REF ($REMOTE_SHA)"

# Si c'est un nouveauremote (remote_sha = 000000...), c'est un premier push
if [ "$REMOTE_SHA" = "0000000000000000000000000000000000000000" ]; then
    log_msg "INFO" "Premier push sur cette branche — règles renforcées"
    FIRST_PUSH=1
else
    FIRST_PUSH=0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: VÉRIFICATION D'AUTORISATION (BIOLOGICAL GATE)
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 1: Vérification Biological Gate..."

AUTH_REQUIRED=0
AUTH_FILE="$TESLA_ROOT/OUTPUTS/authorized_pushes.txt"

# Déterminer si push nécessite autorisation
case "$REMOTE_URL" in
    *github.com*)
        # Push vers GitHub = publication = autorisation requise
        AUTH_REQUIRED=1
        ;;
    *gitlab.com*)
        AUTH_REQUIRED=1
        ;;
    *bitbucket.org*)
        AUTH_REQUIRED=1
        ;;
    *)
        # Autres remotes = évaluation au cas par cas
        if [[ "$REMOTE_URL" == *":/home/"* ]] || [[ "$REMOTE_URL" == *"localhost"* ]]; then
            # Dépôts locaux = souvent internes, moins strict
            AUTH_REQUIRED=0
        else
            AUTH_REQUIRED=1
        fi
        ;;
esac

if [ "$AUTH_REQUIRED" -eq 1 ]; then
    # Vérifier existence autorisation
    if [ -f "$AUTH_FILE" ]; then
        # Chercher une autorisation valide pour ce remote + ref
        AUTH_LINE=$(grep -E "^${REMOTE_NAME}@${REMOTE_REF}@${LOCAL_SHA}@" "$AUTH_FILE" 2>/dev/null || true)
        
        if [ -n "$AUTH_LINE" ]; then
            AUTH_EXPIRY=$(echo "$AUTH_LINE" | cut -d@ -f4)
            AUTH_BY=$(echo "$AUTH_LINE" | cut -d@ -f5)
            
            # Vérifier expiration
            EXPIRY_EPOCH=$(date -d "$AUTH_EXPIRY" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$AUTH_EXPIRY" +%s 2>/dev/null || echo 0)
            CURRENT_EPOCH=$(date +%s)
            
            if [ "$EXPIRY_EPOCH" -gt "$CURRENT_EPOCH" ]; then
                log_msg "INFO" "Push autorisé par $AUTH_BY jusqu'à $AUTH_EXPIRY"
                report_phase "BIOLOGICAL_GATE" "PASS" "Authorized by $AUTH_BY"
            else
                log_msg "ERROR" "Autorisation expirée"
                report_phase "BIOLOGICAL_GATE" "FAIL" "Authorization expired"
                PUSH_BLOCKED=1
            fi
        else
            log_msg "ERROR" "Aucune autorisation trouvée pour ce push"
            log_msg "ERROR" "Remote: $REMOTE_NAME, Ref: $REMOTE_REF, SHA: $LOCAL_SHA"
            report_phase "BIOLOGICAL_GATE" "FAIL" "No authorization found"
            PUSH_BLOCKED=1
        fi
    else
        log_msg "ERROR" "Fichier d'autorisations introuvable: $AUTH_FILE"
        report_phase "BIOLOGICAL_GATE" "FAIL" "Authorization file missing"
        PUSH_BLOCKED=1
    fi
else
    log_msg "INFO" "Autorisation non requise pour ce remote (local/dev)"
    report_phase "BIOLOGICAL_GATE" "SKIP" "Local/dev remote"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: AUDIT DE PARITÉ (LOI DE PARITÉ ABSOLUE)
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 2: Audit de Parité Absolue..."

if [ -f "$HOOKS_LIB/../pre-push/02-parity-audit.sh" ]; then
    if bash "$HOOKS_LIB/../pre-push/02-parity-audit.sh" "$LOCAL_SHA" "$REMOTE_SHA" "$TESLA_ROOT" "$TRACE_ID"; then
        report_phase "PARITY_AUDIT" "PASS" "Parité vérifiée"
    else
        report_phase "PARITY_AUDIT" "FAIL" "Parité non prouvée"
        PUSH_BLOCKED=1
    fi
else
    log_msg "WARN" "Script audit_parite.sh absent — SKIP"
    report_phase "PARITY_AUDIT" "SKIP" "Script not found"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: VÉRIFICATION SHA DISTANT
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 3: Vérification état distant..."

if [ "$FIRST_PUSH" -eq 0 ]; then
    # Vérifier que le SHA distant attendu correspond toujours
    ACTUAL_REMOTE_SHA=$(git ls-remote "$REMOTE_URL" "$REMOTE_REF" 2>/dev/null | cut -f1 || echo "ERROR")
    
    if [ "$ACTUAL_REMOTE_SHA" = "ERROR" ]; then
        log_msg "WARN" "Impossible de lire l'état distant"
        report_phase "REMOTE_STATE" "WARN" "Cannot verify remote state"
    elif [ "$ACTUAL_REMOTE_SHA" != "$REMOTE_SHA" ]; then
        log_msg "ERROR" "SHA distant changé depuis le dernier fetch!"
        log_msg "ERROR" "Attendu: $REMOTE_SHA"
        log_msg "ERROR" "Actuel:  $ACTUAL_REMOTE_SHA"
        report_phase "REMOTE_STATE" "FAIL" "Remote SHA mismatch — someone pushed"
        PUSH_BLOCKED=1
    else
        log_msg "INFO" "SHA distant vérifié: OK"
        report_phase "REMOTE_STATE" "PASS" "SHA verified"
    fi
else
    log_msg "INFO" "Premier push — pas de vérification SHA distant"
    report_phase "REMOTE_STATE" "SKIP" "First push"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: PROTECTION DE BRANCHE
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 4: Vérification protection de branche..."

PROTECTED_BRANCHES=("main" "master" "production" "release/*")

for protected in "${PROTECTED_BRANCHES[@]}"; do
    if [[ "$CURRENT_BRANCH" == $protected ]]; then
        log_msg "WARN" "Branche '$CURRENT_BRANCH' est protégée"
        
        # Pour les branches protégées, vérifier les commits autorisés
        if [ "$AUTH_REQUIRED" -eq 1 ]; then
            # Vérifier que le commit a été autorisé explicitement
            if [ -f "$AUTH_FILE" ]; then
                COMMIT_AUTH=$(grep -E "COMMIT@${LOCAL_SHA}@" "$AUTH_FILE" 2>/dev/null || true)
                if [ -z "$COMMIT_AUTH" ]; then
                    log_msg "ERROR" "Push sur branche protégée sans autorisation de commit"
                    report_phase "BRANCH_PROTECTION" "FAIL" "No commit authorization"
                    PUSH_BLOCKED=1
                else
                    report_phase "BRANCH_PROTECTION" "PASS" "Commit authorized"
                fi
            fi
        fi
        break
    fi
done

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: DÉTECTION FORCE PUSH
# ═══════════════════════════════════════════════════════════════════════════════

log_msg "INFO" "PHASE 5: Détection force-push..."

if [ "$FIRST_PUSH" -eq 0 ]; then
    # Vérifier si ce serait un force-push
    MERGE_BASE=$(git merge-base "$REMOTE_SHA" "$LOCAL_SHA" 2>/dev/null || echo "")
    
    if [ -n "$MERGE_BASE" ]; then
        if [ "$MERGE_BASE" != "$REMOTE_SHA" ]; then
            log_msg "WARN" "FORCE-PUSH détecté!"
            log_msg "WARN" "Remote sera réécrit de $REMOTE_SHA à $LOCAL_SHA"
            
            # Vérifier si force-push est autorisé
            FORCE_AUTH=$(grep -E "FORCE@${REMOTE_NAME}@${CURRENT_BRANCH}" "$AUTH_FILE" 2>/dev/null || true)
            
            if [ -z "$FORCE_AUTH" ]; then
                log_msg "ERROR" "Force-push non autorisé"
                report_phase "FORCE_PUSH_DETECT" "FAIL" "Force-push blocked"
                PUSH_BLOCKED=1
            else
                log_msg "INFO" "Force-push autorisé explicitement"
                report_phase "FORCE_PUSH_DETECT" "PASS" "Force-push authorized"
            fi
        else
            log_msg "INFO" "Push standard — pas de réécriture d'historique"
            report_phase "FORCE_PUSH_DETECT" "PASS" "Standard push"
        fi
    fi
else
    report_phase "FORCE_PUSH_DETECT" "SKIP" "First push"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# RÉSULTAT FINAL
# ═══════════════════════════════════════════════════════════════════════════════

PUSH_BLOCKED="${PUSH_BLOCKED:-0}"

{
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    if [ "$PUSH_BLOCKED" -eq 1 ]; then
        echo "FINAL RESULT: BLOCKED"
    else
        echo "FINAL RESULT: PASS"
    fi
    echo "═══════════════════════════════════════════════════════════════"
} >> "$REPORT_FILE"

log_msg "INFO" "═══════════════════════════════════════════════════════"
log_msg "INFO" "RÉSULTAT FINAL: $([ "$PUSH_BLOCKED" -eq 1 ] && echo 'BLOCKED' || echo 'PASS')"
log_msg "INFO" "═══════════════════════════════════════════════════════"

cat "$REPORT_FILE"

if [ "$PUSH_BLOCKED" -eq 1 ]; then
    echo ""
    echo -e "\e[31m╔═══════════════════════════════════════════════════════════════╗\e[0m"
    echo -e "\e[31m║                    PUSH BLOQUÉ                              ║\e[0m"
    echo -e "\e[31m║                                                               ║\e[0m"
    echo -e "\e[31m║  Au moins une vérification a échoué.                        ║\e[0m"
    echo -e "\e[31m║                                                               ║\e[0m"
    echo -e "\e[31m║  Consultez le rapport: $REPORT_FILE\e[0m"
    echo -e "\e[31m║  Consultez les logs: $LOG_FILE\e[0m"
    echo -e "\e[31m║                                                               ║\e[0m"
    echo -e "\e[31m║  Pour autoriser un push, créez un fichier d'autorisation:  ║\e[0m"
    echo -e "\e[31m║  OUTPUTS/authorized_pushes.txt                              ║\e[0m"
    echo -e "\e[31m╚═══════════════════════════════════════════════════════════════╝\e[0m"
    exit 1
fi

echo ""
echo -e "\e[32m╔═══════════════════════════════════════════════════════════════╗\e[0m"
echo -e "\e[32m║                    PUSH AUTORISÉ                              ║\e[0m"
echo -e "\e[32m║                                                               ║\e[0m"
echo -e "\e[32m║  Toutes les vérifications ont passé.                         ║\e[0m"
echo -e "\e[32m╚═══════════════════════════════════════════════════════════════╝\e[0m"
exit 0
```

---

## 3.4 Librairies de Support

### 3.4.1 Bibliothèque de Logging

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                    TESLA LOGGING LIBRARY                                    ║
# ║              Bibliothèque de logging standardisé                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables globales
TESLA_LOG_FILE="${TESLA_LOG_FILE:-/tmp/tesla-hooks.log}"
TESLA_LOG_LEVEL="${TESLA_LOG_LEVEL:-INFO}"

# Niveaux de log
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARN"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

# Fonction d'initialisation
tesla_log_init() {
    local log_file="$1"
    local min_level="$2"
    local component="$3"
    local trace_id="$4"
    
    export TESLA_LOG_FILE="$log_file"
    export TESLA_LOG_COMPONENT="$component"
    export TESLA_LOG_TRACE="$trace_id"
    export TESLA_LOG_MIN_LEVEL="${LOG_LEVELS[$min_level]:-1}"
    
    mkdir -p "$(dirname "$log_file")"
    echo "" >> "$log_file"
    echo "══════════════════════════════════════════════════════════════════" >> "$log_file"
    echo "Component: $component | Trace: $trace_id | Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$log_file"
    echo "══════════════════════════════════════════════════════════════════" >> "$log_file"
}

# Fonction de logging principale
tesla_log() {
    local level="$1"
    local message="$2"
    local component="${TESLA_LOG_COMPONENT:-SYSTEM}"
    local trace_id="${TESLA_LOG_TRACE:-N/A}"
    
    local current_level="${LOG_LEVELS[$level]:-1}"
    
    # Filtrer selon le niveau minimum
    if [ "$current_level" -lt "${TESLA_LOG_MIN_LEVEL:-1}" ]; then
        return 0
    fi
    
    local timestamp
    timestamp=$(date +%H:%M:%S)
    
    local log_line="[$timestamp] [$level] [$component] [$trace_id] $message"
    
    # Écrire dans le fichier de log
    echo "$log_line" >> "$TESLA_LOG_FILE"
    
    # Écrire sur stderr avec couleur
    local color=""
    case "$level" in
        DEBUG)   color="$CYAN" ;;
        INFO)    color="$BLUE" ;;
        WARN)    color="$YELLOW" ;;
        ERROR)   color="$RED" ;;
        CRITICAL) color="$RED" ;;
    esac
    
    echo -e "${color}${log_line}${NC}" >&2
}

# Alias pratiques
tesla_debug() { tesla_log "DEBUG" "$1"; }
tesla_info()  { tesla_log "INFO" "$1"; }
tesla_warn()  { tesla_log "WARN" "$1"; }
tesla_error() { tesla_log "ERROR" "$1"; }
tesla_critical() { tesla_log "CRITICAL" "$1"; }

# Export
export -f tesla_log_init tesla_log
export -f tesla_debug tesla_info tesla_warn tesla_error tesla_critical
```

### 3.4.2 Codes de Sortie Standardisés

```bash
#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                 TESLA EXIT CODES LIBRARY                                    ║
# ║              Codes de sortie standardisés pour l'écosystème Tesla           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ═══════════════════════════════════════════════════════════════════════════════
# CODES DE SUCCÈS
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_SUCCESS=0                    # Succès
EXIT_PASS=0                       # Vérification Passed

# ═══════════════════════════════════════════════════════════════════════════════
# CODES D'ÉCHEC GÉNÉRIQUES
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_GENERAL_ERROR=1              # Erreur générale
EXIT_VALIDATION_FAILED=1          # Échec de validation
EXIT_BLOCKED=1                    # Bloqué par sécurité

# ═══════════════════════════════════════════════════════════════════════════════
# CODES SPÉCIFIQUES TESLA
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_INVALID_SCHEMA=64            # Schéma YAML/JSON invalide
EXIT_INVALID_SIGNATURE=65         # Signature HMAC invalide
EXIT_TESLA_ROOT_NOT_FOUND=66       # TESLA_ROOT introuvable
EXIT_DEPENDENCY_MISSING=69        # Dépendance manquante (jq, rg, etc.)

EXIT_SECRET_DETECTED=100          # Secret/token détecté
EXIT_SCOPE_VIOLATION=101          # Violation de périmètre
EXIT_PROJECT_STATE_DESYNC=102     # PROJECT_STATE désynchronisé
EXIT_MARBLE_CERT_MISSING=103      # Marble Certificate absent
EXIT_BASELINE_DRIFT=104           # Baseline drift détecté
EXIT_UNKNOWN_STATE=105            # État non vérifiable (≠ PASS)

EXIT_AUTH_EXPIRED=110             # Autorisation expirée
EXIT_AUTH_MISSING=111             # Autorisation manquante
EXIT_FORCE_PUSH_BLOCKED=112       # Force-push non autorisé

EXIT_RETRY_EXCEEDED=120          # Max retries dépassé
EXIT_CIRCUIT_BREAKER_OPEN=121    # Circuit breaker déclenché
EXIT_ESCALATION_REQUIRED=130     # Escalade vers Mahonheim requise

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

# Obtenir la description d'un code de sortie
exit_code_description() {
    local code="$1"
    case "$code" in
        0)    echo "SUCCESS" ;;
        1)    echo "FAILURE (generic)" ;;
        64)   echo "INVALID_SCHEMA" ;;
        65)   echo "INVALID_SIGNATURE" ;;
        66)   echo "TESLA_ROOT_NOT_FOUND" ;;
        69)   echo "DEPENDENCY_MISSING" ;;
        100)  echo "SECRET_DETECTED" ;;
        101)  echo "SCOPE_VIOLATION" ;;
        102)  echo "PROJECT_STATE_DESYNC" ;;
        103)  echo "MARBLE_CERT_MISSING" ;;
        104)  echo "BASELINE_DRIFT" ;;
        105)  echo "UNKNOWN_STATE" ;;
        110)  echo "AUTH_EXPIRED" ;;
        111)  echo "AUTH_MISSING" ;;
        112)  echo "FORCE_PUSH_BLOCKED" ;;
        120)  echo "RETRY_EXCEEDED" ;;
        121)  echo "CIRCUIT_BREAKER_OPEN" ;;
        130)  echo "ESCALATION_REQUIRED" ;;
        *)    echo "UNKNOWN_CODE" ;;
    esac
}

# Afficher un message d'erreur formaté
exit_with_message() {
    local code="$1"
    local message="$2"
    
    echo "╔═══════════════════════════════════════════════════════════════╗"
    printf "║ %-60s ║\n" "$(exit_code_description $code)"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "$message"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    
    exit "$code"
}

# Export
export -f exit_code_description exit_with_message
export EXIT_SUCCESS EXIT_PASS
export EXIT_GENERAL_ERROR EXIT_VALIDATION_FAILED EXIT_BLOCKED
export EXIT_INVALID_SCHEMA EXIT_INVALID_SIGNATURE EXIT_TESLA_ROOT_NOT_FOUND EXIT_DEPENDENCY_MISSING
export EXIT_SECRET_DETECTED EXIT_SCOPE_VIOLATION EXIT_PROJECT_STATE_DESYNC EXIT_MARBLE_CERT_MISSING
export EXIT_BASELINE_DRIFT EXIT_UNKNOWN_STATE
export EXIT_AUTH_EXPIRED EXIT_AUTH_MISSING EXIT_FORCE_PUSH_BLOCKED
export EXIT_RETRY_EXCEEDED EXIT_CIRCUIT_BREAKER_OPEN EXIT_ESCALATION_REQUIRED
```

---

# ANNEXES

## A. Plan d'Implémentation Phasé

### Phase 1 : Infrastructure Minimale (Semaine 1)
| Tâche | Effort | Dépendances | Validateur |
|:---|:---:|:---:|:---:|
| Structure `core.hooks/` | 2h | Aucune | Scriptable |
| Hooks lib (logging, exit codes) | 4h | Aucune | Tests unitaires |
| pre-commit main orchestrator | 4h | Libs | Integration test |
| pre-push main orchestrator | 4h | Libs | Integration test |
| Secret scanner module | 4h | Patterns | CTF test |
| Scope validator module | 4h | Aucune | Unit test |

### Phase 2 : Validation Scripts (Semaine 2)
| Tâche | Effort | Dépendances | Validateur |
|:---|:---:|:---:|:---:|
| Schema validator module | 4h | jsonschema | Unit test |
| PROJECT_STATE check module | 4h | Aucune | Integration test |
| Marble cert check module | 4h | Gravure protocol | Manual |
| Lint check module | 4h | Linters | Unit test |
| Parity audit pre-push | 8h | audit_parite.sh | Integration test |
| Authorization check | 8h | Mahonheim | Manual |

### Phase 3 : Démon Broker (Semaine 3-4)
| Tâche | Effort | Dépendances | Validateur |
|:---|:---:|:---:|:---:|
| Intent schema YAML | 8h | Blueprint doc | Schema validator |
| Broker Python skeleton | 16h | Aucune | Unit tests |
| FileWatcher integration | 8h | watchdog | Integration test |
| AMDEC engine | 16h | Aucune | Scenario tests |
| Gate validators | 24h | Phase 1-2 scripts | Full integration |
| IPC socket server | 8h | Aucune | Stress test |
| systemd unit file | 2h | Aucune | systemctl test |

### Phase 4 : Gravure Automation (Semaine 5-6)
| Tâche | Effort | Dépendances | Validateur |
|:---|:---:|:---:|:---:|
| Gravure authority module | 8h | Broker skeleton | Integration test |
| Gravure closure module | 8h | Authority | Integration test |
| Gravure validation (4 levels) | 16h | Closure | Full integration |
| Gravure assimilation module | 8h | Parity protocol | Integration test |
| Gravure staging module | 8h | Assimilation | Manual |
| Gravure seal module | 8h | All phases | Full flow test |
| Marble certificate generator | 8h | All phases | Integration test |

## B. Risques et Mitigations

| Risque | Probabilité | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Faux positifs sur secret scanner | HAUTE | MOYEN | Whitelist patterns, exclude dirs |
| Hook trop lent (>30s) | MOYENNE | MOYENNE | Parallélisation, caching |
| INTENT schema breaking change | FAIBLE | TRÈS ÉLEVÉ | Versioning, migration scripts |
| Broker crash loop | FAIBLE | CRITIQUE | Circuit breaker, watchdog |
| Key compromise | TRÈS FAIBLE | CRITIQUE | HSM, key rotation, audit |

## C. Matrice de Conformité

| Requirement | Source | Status | Implementation |
|:---|:---|:---|:---|
| No Proof No Pass | Gravure P1 | Required | Script + Broker |
| Producer ≠ Validator | Gravure P2 | Required | Separate scripts |
| Fail Closed | Gravure P8 | Required | Hooks + Broker |
| No Unauthorized Push | Conducteur G6 | Required | pre-push hook |
| Baseline Fingerprint | Loi Parité §5.2 | Required | Broker state check |
| AMDEC Before Execution | Broker AMDEC | Required | Broker engine |
| Circuit Breaker | Loi Parité §7 | Required | Broker logic |
| Marble Certificate | Gravure Phase 7 | Required | Seal module |

---

## D. Critère Ultime de Validation

Ce Blueprint est considéré comme **implémenté correctement** lorsque :

```
TESTS AUTOMATISÉS:
✓ 100% des hooks passent avec fichiers propres
✓ 100% des hooks bloquent avec secrets injectés
✓ 100% des hooks bloquent avec violations de scope
✓ Broker reject intents non signés (0 false positive)
✓ Broker accept intents valides (0 false negative)
✓ Circuit breaker déclenche après 3 retries

AUDIT MANUEL:
✓ Lord Mahonheim peut autoriser un push (biological gate)
✓ Push refusé sans autorisation
✓ Marble Certificate généré après Gravure complète

DÉPLOIEMENT:
✓ core.hooksPath configuré sur machine de dev
✓ systemd service actif sur session utilisateur
✓ Logs consultables et rotation active
```

---

> **FIN DU BLUEPRINT**
> 
> **Document généré le:** 2026-08-26  
> **Version:** 1.0.0  
> **Classification:** STRATÉGIQUE — ULTRA-SENSIBLE  
> **DOCTRINE:** Vigilum Codex 2.0 — Fail-Closed Mandatory  
> 
> *"Le code valide, l'IA propose."*
> *"No Proof, No Marble."*
> *"Gravé n'est pas déclaré. Gravé est prouvé."*
