# Rapport d'Évaluation Technique et de Spécification des Contrats : Loop Engineering
**Auteur :** Tesla Master Code (Chief Software Engineering Agent)  
**Destinataire :** Lord Mahonheim  
**Date d'émission :** 10 Juillet 2026  
**Statut de Mission :** Mission terminée et réussie  
**Version :** v1.0  

---

## 1. Diagnostic de l'Écosystème Local (MIDGARD)

Conformément aux conclusions du rapport d'analyse de **Tesla Arcanis-360** (`rapport_arcanis_loop_engineering_v1.0_2026-07-10.md`) et du rapport de curation de **Tesla Curator Prime** (`rapport_curator_loop_engineering_v1.0_2026-07-10.md`), nous avons réalisé l'audit de faisabilité technique pour le déploiement du Loop Engineering (cycle itératif *Act-Verify-Learn-Repeat*).

### Observations directes et contraintes d'environnement :
1. **Réseau Hermétique (Mode `CODE_ONLY`) :** La station MIDGARD n'a aucun accès réseau externe. Toutes les dépendances logicielles doivent être résolues localement ou s'appuyer sur l'existant.
2. **Absence locale de Semgrep dans le venv :** L'outil `semgrep` n'est pas provisionné dans le répertoire virtuel `.venv/bin/`. Toute invocation directe par l'auditeur de code échouera sans une stratégie de contournement ou de provisionnement statique hors-ligne.
3. **Absence des tables relationnelles dans Alexandria :** La base de données SQLite `alexandria_brain.db` (située dans `/home/lord-mahonheim/bifrost/tesla/database/`) n'implémente pas encore les tables `loop_executions` et `loop_iterations` requises pour la persistance de l'état des boucles.
4. **Biais d'Auto-Certification :** `tesla-master-code` est l'exécuteur des modifications de code. Si le même agent évalue ses propres modifications, le risque de "reward hacking" est critique. L'indépendance de `tesla-code-auditor` par rapport à `tesla-master-code` est donc un impératif architectural.

---

## 2. Évaluation de la Faisabilité Technique

Le déploiement est **techniquement réalisable** en local sous réserve de respecter les mesures d'atténuation suivantes pour les contraintes identifiées.

### Tableau de Synthèse des Risques & Atténuations

| Contrainte / Risque | Impact | Mesure d'Atténuation | Statut |
| :--- | :--- | :--- | :--- |
| Pas d'accès internet (`CODE_ONLY`) | Impossible d'installer des bibliothèques à la volée. | Exploitation des bibliothèques standards de Python 3.12 et des paquets déjà présents dans le `.venv` (`chromadb`, `sentence_transformers`, `google-genai`). | **Validé** |
| Semgrep manquant dans `.venv` | Échec de la validation de sécurité statique (Rung 2). | **Stratégie Hybride :** Conception d'un validateur AST local s'appuyant sur le module Python natif `ast` combiné à des expressions régulières pour simuler les règles Tesla, en attendant le provisionnement statique hors-ligne de la roue (`.whl`) de Semgrep. | **Validé** |
| Stagnation cognitive (Doom Loop) | L'agent de codage tourne en boucle sur le même message d'erreur. | L'orchestrateur compare le hash SHA-256 du rapport d'erreur précédent avec le nouveau. En cas de stagnation (messages d'erreur identiques sur deux itérations consécutives) $\rightarrow$ Transition vers `BLOCK`. | **Spécifié** |
| Concurrence sur SQLite Alexandria | Erreurs de verrouillage base (`database is locked`) si plusieurs boucles s'exécutent. | Implémentation d'un mécanisme de retry avec attente exponentielle (backoff) dans l'orchestrateur. | **Spécifié** |
| Reward Hacking (Rung 4) | L'agent de codage leurre le modèle juge sémantique. | Dissociation cognitive : Configuration obligatoire de modèles distincts pour l'action et le jugement (ex. Gemini 1.5 Flash pour le juge, Claude 3.5 Sonnet pour l'actionneur). | **Spécifié** |

---

## 3. Inventaire des Bibliothèques Python Disponibles Localement

Toutes les exécutions de scripts et de wrappers devant s'effectuer sans accès réseau, nous listons ci-dessous les bibliothèques locales sur MIDGARD utilisables pour l'orchestrateur et l'auditeur.

### 3.1 Bibliothèques Standards (Natives)

* **`sqlite3` :** Moteur relationnel utilisé pour la persistance locale de l'état des boucles et l'intégration avec Alexandria.
* **`json` :** Utilisé pour la sérialisation/désérialisation du payload d'audit et des "Learning Deltas".
* **`subprocess` :** Essentiel pour lancer de manière isolée et sécurisée les outils de validation (`ruff`, `pyright`, `pytest`, `deno`, `wasmtime`).
* **`hashlib` :** Utilisé pour calculer les signatures de fichiers et de messages d'erreur afin de détecter les régressions et la stagnation.
* **`argparse` :** Utilisé pour structurer les interfaces CLI de l'orchestrateur et de l'auditeur.
* **`datetime` :** Pour l'horodatage des itérations et de la persistance.
* **`re` :** Utilisé pour parser les rapports de lints, de types, et extraire les lignes fautives.
* **`shutil` :** Pour la création de sauvegardes de sécurité (backups) avant modification et la restauration en cas de blocage (`BLOCK`).
* **`ast` :** Utilisé comme alternative locale et hermétique pour analyser structurellement les fichiers Python et détecter des anti-patterns sans requérir Semgrep.
* **`typing` :** Assure le typage strict du code Python (conforme à la doctrine Ruff/Pyright).

### 3.2 Bibliothèques Tierces Validées dans le `.venv`

* **`google.genai` / `google-genai` :** Le SDK officiel Google GenAI pour l'accès aux modèles Gemini locaux de Rung 4 (Referee Juge).
* **`chromadb` & `sentence_transformers` :** Utilisés pour la recherche sémantique locale dans la base Alexandria.
* **`yaml` (PyYAML) :**
  * *Note de robustesse (Fallback) :* Si le paquet `yaml` venait à présenter un défaut d'importation dans certains sous-environnements, l'orchestrateur doit supporter l'ingestion native des contrats de boucle au format **JSON** via la bibliothèque standard `json`. De plus, un parser minimaliste de fichiers YAML textuels (qui convertit les clés `contract_version`, `goal`, etc., en dictionnaire Python) sera intégré en secours.

---

## 4. Schéma Relationnel de Persistance (Alexandria DDL Version 2.0)

Pour assurer la persistance structurelle de l'état des boucles d'une session à l'autre et alimenter la mémoire globale d'Alexandria, le schéma relationnel de la base SQLite `alexandria_brain.db` est étendu avec la version 2.0 suivante :

```sql
-- DDL Extension Schema Version 2.0
-- Intégration du Loop Engineering dans la base Alexandria

CREATE TABLE IF NOT EXISTS loop_executions (
    id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    goal TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL CHECK(status IN ('PASS', 'DELAY', 'BLOCK', 'RUNNING')),
    total_iterations INTEGER DEFAULT 0,
    total_token_cost REAL DEFAULT 0.0,
    max_iterations INTEGER NOT NULL,
    token_budget REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS loop_iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('PASS', 'DELAY', 'BLOCK')),
    learning_deltas TEXT, -- JSON sérialisé contenant la liste structurée des erreurs
    token_cost REAL DEFAULT 0.0,
    report_path TEXT,
    FOREIGN KEY (execution_id) REFERENCES loop_executions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_loop_executions_status ON loop_executions(status);
CREATE INDEX IF NOT EXISTS idx_loop_iterations_exec ON loop_iterations(execution_id);
```

---

## 5. Contrats d'Interface et Spécifications CLI

Les échanges entre `tesla-loop-orchestrator` (Superviseur) et `tesla-code-auditor` (Independent Gatekeeper) reposent sur des formats d'interface immuables et documentés.

### 5.1 Spécification CLI de l'Orchestrateur (`tesla-loop-orchestrator`)

L'orchestrateur lit le contrat de boucle, pilote l'agent d'écriture et invoque l'auditeur.
* **Commande canonique :** `python3 scripts/loop_orchestrator.py [OPTIONS]`
* **Arguments :**
  * `-c, --contract <PATH>` : (Obligatoire) Chemin vers le fichier de contrat de boucle (YAML ou JSON).
  * `-d, --db <PATH>` : Chemin vers la base SQLite Alexandria (défaut : `database/alexandria_brain.db`).
  * `-a, --action-agent <NAME>` : Nom de l'agent d'ingénierie et d'écriture (défaut : `tesla-master-code`).
  * `-v, --validator <NAME>` : Nom de l'auditeur de validation invoqué (défaut : `tesla-code-auditor`).
  * `-o, --output-dir <PATH>` : Répertoire d'écriture des rapports d'itérations (défaut : `.runtime/loops/`).
  * `--verbose` : Active les logs détaillés de débogage.

### 5.2 Spécification CLI de l'Auditeur (`tesla-code-auditor`)

L'auditeur analyse le code produit sans le modifier et génère un rapport JSON standardisé.
* **Commande canonique :** `python3 scripts/code_auditor.py [OPTIONS]`
* **Arguments :**
  * `-f, --files <PATH> [<PATH> ...]` : Liste des fichiers sources à auditer.
  * `-d, --dir <PATH>` : Répertoire entier à auditer.
  * `--config <PATH>` : Fichier de configuration des règles de lint/sécurité (défaut : `.agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml`).
  * `-r, --rungs <RUNG> [<RUNG> ...]` : Échelons de validation à exécuter (défaut : `1 2 3 4`).
  * `--test-cmd <CMD>` : Commande personnalisée pour le Rung 3 (défaut : `pytest`).
  * `--referee-model <MODEL>` : Modèle LLM utilisé pour la validation sémantique du Rung 4 (défaut : `gemini-1.5-flash`).
  * `-j, --output-json <PATH>` : (Obligatoire) Chemin d'écriture du payload JSON résultat.

---

### 5.3 Payload du Contrat de Boucle (Entrée Orchestrateur)

Le contrat définit les cibles et les budgets de la tâche d'ingénierie.
* **Format YAML (`loop_contract.yaml`) :**
```yaml
contract_version: "1.0"
project: "tesla_cache_optimization"
goal: |
  Optimiser la fonction d'invalidation du cache dans core/cache.py.
  Le code doit supporter un nettoyage concurrent et passer tous les tests unitaires.
validators:
  - name: rung_1_lint
    enabled: true
  - name: rung_2_static
    enabled: true
    config:
      rules_file: ".agents/skills/tesla-code-auditor/rules/tesla_custom_rules.yaml"
  - name: rung_3_tests
    enabled: true
    config:
      command: "pytest tests/test_cache.py"
  - name: rung_4_semantic
    enabled: true
    config:
      referee_model: "gemini-1.5-flash"
limits:
  max_iterations: 5
  token_budget: 0.05  # Budget financier en dollars pour l'évaluation sémantique
  iteration_timeout_seconds: 300
```

---

### 5.4 Payload de Diagnostic de l'Auditeur (Sortie Auditeur $\rightarrow$ Entrée Orchestrateur)

Ce format structuré standardisé permet à l'orchestrateur de prendre sa décision de transition.
* **Format JSON (`audit_report.json`) :**
```json
{
  "verdict": "DELAY",
  "rung_reached": 2,
  "summary": "Pyright compilation check failed on 1 count. Style & Format checks passed.",
  "timestamp": "2026-07-10T01:05:00Z",
  "validators": {
    "style_check": {
      "status": "SUCCESS",
      "tool_used": "ruff",
      "raw_output": "All lints cleared."
    },
    "static_analysis": {
      "status": "FAILED",
      "tool_used": "pyright",
      "raw_output": "error: Expression of type 'str' cannot be assigned to parameter 'max_size' of type 'int'"
    },
    "unit_tests": {
      "status": "SKIPPED",
      "tool_used": "pytest",
      "raw_output": ""
    },
    "semantic_validation": {
      "status": "SKIPPED",
      "tool_used": "referee_llm",
      "raw_output": ""
    }
  },
  "learning_deltas": [
    {
      "file": "core/cache.py",
      "line": 42,
      "severity": "ERROR",
      "code": "pyright_type_error",
      "message": "Type mismatch: expected int, got str in parameter 'max_size'"
    }
  ]
}
```

---

## 6. Signatures des Fonctions Clés (Python API)

Afin de guider le développement de la Phase 2, nous définissons les signatures typées et les contrats logiques des fonctions au sein des modules Python.

### 6.1 `scripts/loop_orchestrator.py`
```python
from typing import Dict, List, Any, Optional

def load_contract(contract_path: str) -> Dict[str, Any]:
    """
    Charge le contrat de boucle (YAML ou JSON).
    Intègre un parser de secours en cas d'absence de PyYAML.
    Raises:
        FileNotFoundError: Si le contrat n'existe pas.
        ValueError: Si le contrat est mal formé.
    """
    pass

def initialize_run_in_db(contract: Dict[str, Any], db_path: str) -> str:
    """
    Crée un enregistrement unique dans loop_executions et génère un UUID4.
    """
    pass

def record_iteration(
    execution_id: str, 
    iteration_num: int, 
    action: str, 
    verdict: str, 
    deltas: List[Dict[str, Any]], 
    cost: float, 
    report_path: str, 
    db_path: str
) -> None:
    """
    Insère les métadonnées de l'itération active et ses Learning Deltas (JSON).
    Gère la tolérance aux pannes avec retry en cas de verrou de base SQLite.
    """
    pass

def check_stagnation(new_deltas: List[Dict[str, Any]], prev_deltas: List[Dict[str, Any]]) -> bool:
    """
    Compare le contenu des deltas d'apprentissage de l'itération courante avec la précédente.
    Retourne True si les messages d'erreur et les localisations sont rigoureusement identiques.
    """
    pass

def generate_learning_prompt(goal: str, deltas: List[Dict[str, Any]]) -> str:
    """
    Formate un message de prompt enrichi contenant l'objectif initial ainsi que
    les indications exactes (fichiers, lignes, erreurs) des échecs de validation.
    """
    pass

def run_loop(contract_path: str, db_path: str) -> str:
    """
    Fonction principale de boucle (Act-Verify-Learn-Repeat).
    Retourne le verdict final ('PASS' ou 'BLOCK').
    """
    pass
```

### 6.2 `scripts/code_auditor.py`
```python
from typing import Dict, List, Any

def run_rung_1_style(files: List[str]) -> Dict[str, Any]:
    """
    Exécute 'ruff check' sur la liste des fichiers.
    Retourne un dictionnaire contenant le statut (SUCCESS/FAILED) et les lints.
    """
    pass

def run_rung_2_static(files: List[str], rules_path: str) -> Dict[str, Any]:
    """
    Exécute 'pyright' pour la vérification de types.
    Exécute le scanner AST local (ou Semgrep) pour les règles Tesla de sécurité.
    """
    pass

def run_rung_3_dynamic(test_command: str) -> Dict[str, Any]:
    """
    Lance la suite de tests unitaires dans un processus isolé (subprocess).
    Capture les sorties stdout/stderr et le code de retour (exit code).
    """
    pass

def run_rung_4_semantic(
    files: List[str], 
    goal: str, 
    referee_model: str
) -> Dict[str, Any]:
    """
    Invoque l'API Gemini avec le client google-genai pour faire valider le code
    par un LLM Juge indépendant (analyse anti-bypass et adéquation logique).
    """
    pass

def consolidate_audit(
    results: Dict[str, Dict[str, Any]], 
    rung_reached: int
) -> Dict[str, Any]:
    """
    Prend les résultats bruts de chaque échelon exécuté et formule le payload
    JSON final de diagnostic contenant le verdict global ('PASS', 'DELAY', 'BLOCK')
    et les Learning Deltas structurés.
    """
    pass
```

---

## 7. Plan d'Implémentation Détaillé (Phase 2 & 3)

Le déploiement s'articulera autour de cinq phases séquentielles de réalisation.

### Phase 1 : Mise à jour DDL Alexandria (Immédiat)
* **Action :** Modifier `memory/db_init.py` pour inclure la DDL Version 2.0.
* **Vérification :** Lancer `./init_alexandria.sh` ou exécuter `just index` pour valider que les tables sont opérationnelles dans SQLite.

### Phase 2 : Développement du Gardien Technique (`tesla-code-auditor`)
* **Action :** Écriture de `scripts/code_auditor.py`.
* **Composant AST de secours :** Développement d'un analyseur statique local basé sur le module natif `ast` pour compenser l'absence de Semgrep. Il analysera les structures de contrôle et lèvera des alertes sur les fonctions vides ou les blocs `try-except` capturant l'exception générique `Exception` sans traitement.
* **Vérification :** Lancer un audit de test sur un fichier factice contenant volontairement une erreur de type et de style.

### Phase 3 : Développement du Superviseur (`tesla-loop-orchestrator`)
* **Action :** Écriture de `scripts/loop_orchestrator.py` contenant la machine d'état logique (`PASS`, `DELAY`, `BLOCK`) et les contrôles de stagnation/régression.
* **Vérification :** Simulation de boucle avec des rapports d'audit pré-remplis pour vérifier le bon comportement de la machine d'état.

### Phase 4 : Rung 4 - Intégration du Modèle Juge (Referee)
* **Action :** Configuration de la validation sémantique via le SDK `google-genai` en spécifiant le modèle `gemini-1.5-flash` distinct de l'agent de codage.
* **Vérification :** Simulation d'une injection de prompt dans le code source (ex: ajout de `# bypass test validation`) pour valider la détection par le juge.

### Phase 5 : Campagne de Tests Unitaires et Intégration
* **Action :** Écriture de tests unitaires (`tests/test_loop_orchestrator.py` et `tests/test_code_auditor.py`) validant le comportement déconnecté de tout le système.
* **Vérification :** Exécution réussie des tests avec `pytest`.

---

## 8. Curation et Clôture

Conformément à la doctrine de gouvernance de **Tesla Curator Prime**, ce rapport technique fige les contrats d'interfaces et clôt la phase d'évaluation technique. La transition vers l'écriture physique du code est prête et validée.

Signé / Fait par: Tesla sur Antigravity CLI  
Main rendue à Mahonheim  
