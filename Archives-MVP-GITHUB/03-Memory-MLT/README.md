# Long-Term Semantic Memory (LTM)

## Cognitive Persistence Architecture
The Long-Term Memory (LTM) module ensures cognitive persistence and capitalization across execution sessions. By converting transient agent interaction transcripts into structured, indexed markdown documents, this module builds a cumulative memory layer that enables future sessions to build directly upon past discoveries.

## Consolidating Interaction History
The script `update_session_history.py` parses local agent console logs and transcripts, extracting requests, diagnostic findings, actions, and validations. It condenses these into:
1. A **Cognitive Synthesis Table**: A brief summary mapping session date, session ID, and main objective.
2. A **Detailed Session Log**: Expandable markdown blocks preserving precise interactions, stored in a consolidated history file (`SESSION_TRANSCRIPTS.md`).

## Idempotent Update Script Usage
The session updater is strictly idempotent, meaning it updates existing session blocks matching the current `ANTIGRAVITY_CONVERSATION_ID` or appends a new block if not present, preventing duplicate logs.
To run the consolidation script:
```bash
export ANTIGRAVITY_CONVERSATION_ID="your-session-uuid"
python 03-Memory-MLT/update_session_history.py
```
*Note: Make sure `GEMINI_APP_DATA_DIR` is set or points to your actual application home folder structure.*
