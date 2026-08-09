#!/usr/bin/env python3
import re

class PIIScrubber:
    PATTERNS = {
        "google_api_key": r"AIzaSy[a-zA-Z0-9\-_]{33}",
        "openai_api_key": r"sk-[a-zA-Z0-9]{48}",
        "github_token": r"gh[oprs]_[a-zA-Z0-9]{36,255}",
        "generic_secret": r"(?i)(password|secret|passwd|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.\!\@\#\$]{8,}['\"]",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "jwt_token": r"eyJ[a-zA-Z0-9-_]+\.eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+"
    }

    @classmethod
    def scrub(cls, text: str) -> str:
        """Remplace les informations sensibles identifiées par des expressions régulières."""
        scrubbed = text
        for name, pattern in cls.PATTERNS.items():
            scrubbed = re.sub(pattern, f"[REDACTED_{name.upper()}]", scrubbed)
        return scrubbed
