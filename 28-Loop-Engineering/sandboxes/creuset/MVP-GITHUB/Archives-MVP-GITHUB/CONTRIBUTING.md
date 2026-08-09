# Contributing to Vigilum Codex MVP

Thank you for your interest in contributing to the Vigilum Codex MVP repository. Please review the following guidelines before submitting any modifications or code adjustments.

## Doctrinal Alignment
All contributions must align with the **Vigilum Codex** architecture:
1.  **Low-Code/No-Code Priority**: Automate using standard CLI commands and low-code integrations before introducing complex custom scripts.
2.  **English Language**: All code syntax, documentation, issue tracking, and pull request write-ups must be written in English.
3.  **Local Execution**: Ensure modules do not depend on external, unverified network API calls. Maintain technological sovereignty.

## Coding and Formatting Rules
*   **Zero Secrets**: Do not commit API keys, personal file paths (such as `/home/lord-mahonheim`), or private variables. Use relative paths and environment-based fallbacks.
*   **Git Commits**: Follow the *Conventional Commits* standard: `<type>(<scope>): <description>`.
*   **Linting & Verification**: Run the local LSP diagnostic script (`01-LSP-Self-Healing/examples/test_lsp.py`) to verify file health before committing.

## Branch and Pull Request Policy
1.  Develop all changes in a dedicated branch (`feature/your-feature` or `fix/your-fix`).
2.  Do not commit directly to the `main` branch.
3.  Open a Pull Request with a clear Diagnostic (Why?), Change Description (What?), and Verification Proof (Logs or Test results).
