import json
import hashlib
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class ExecutionTrace:
    trace_id: str
    skill: str
    domaine: str
    task_id: str
    model: str
    outcome: str
    score: float
    verdict_sources: List[str]
    ast_quarantine_status: str
    steps: List[Dict[str, Any]]
    final_answer: str
    secrets_scrubbed: bool
    sha256: str = field(default="")

    def compute_hash(self) -> str:
        data = asdict(self)
        data.pop('sha256', None)
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def validate(self) -> bool:
        if not isinstance(self.score, (int, float)) or not (0.0 <= self.score <= 1.0):
            raise ValueError("Le score doit être compris entre 0.0 et 1.0")
        if not self.secrets_scrubbed:
            raise ValueError("Les secrets doivent être nettoyés (secrets_scrubbed=True)")
        if not self.trace_id or not self.task_id:
            raise ValueError("trace_id et task_id sont obligatoires")
        return True

    def to_json(self) -> str:
        self.sha256 = self.compute_hash()
        return json.dumps(asdict(self), indent=2)

    def verify_hash(self) -> bool:
        """Verifie l'integrite cryptographique (recalcule vs stocke)."""
        if not self.sha256:
            return False
        return self.compute_hash() == self.sha256

    @classmethod
    def from_json(cls, json_str: str) -> 'ExecutionTrace':
        data = json.loads(json_str)
        instance = cls(**data)
        instance.validate()
        return instance
