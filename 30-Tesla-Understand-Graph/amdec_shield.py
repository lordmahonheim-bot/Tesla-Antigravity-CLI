import os

MAX_LINES = 2000
BLACKLIST_EXTS = ['.min.js', '.min.css', '.lock']
MAX_LLM_TOKENS_PER_DAY = 100000

class AMDECShield:
    def __init__(self):
        self.tokens_used_today = 0

    def is_file_safe(self, filepath):
        # Filtre OOM et minifiés
        if any(filepath.endswith(ext) for ext in BLACKLIST_EXTS):
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > MAX_LINES:
                    return False
        except Exception:
            return False
        return True

    def check_circuit_breaker(self, estimated_tokens):
        # Circuit Breaker Budgétaire
        if self.tokens_used_today + estimated_tokens > MAX_LLM_TOKENS_PER_DAY:
            raise Exception("AMDEC Circuit Breaker Triggered: Token limit exceeded!")
        return True

    def check_large_diff_approval(self, diff_lines):
        # Approbation manuelle bloquante
        if diff_lines > 500:
            print("MAIN_RENDUE_A_MAHONHEIM=1")
            raise Exception("AMDEC Shield: Large diff requires manual approval from Lord Mahonheim.")
        return True
