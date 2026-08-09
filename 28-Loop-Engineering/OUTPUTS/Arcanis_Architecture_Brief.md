# Architectural Brief: Loop Engineering (MVP 16 & MVP 44)

## 1. Overview
This brief defines the Loop Engineering architecture connecting **MVP 16 (Tesla-Master-Code)** and the newly proposed **MVP 44 (Tesla-Code-Auditor)**. This architecture implements a robust Actor-Validator pattern to ensure code quality, security, and functional correctness within an isolated execution environment.

## 2. Components
### 2.1 MVP 16 (Tesla-Master-Code) - The "Actor"
*   **Role**: Responsible for autonomous code generation, modification, and basic syntax checking (linting).
*   **Environment**: Operates within a sandboxed execution environment.
*   **Responsibilities**:
    *   Receiving coding specifications and requirements.
    *   Writing code and unit tests.
    *   Executing preliminary local linters (e.g., Pyright).
    *   Submitting code blocks to the Validator (MVP 44).
    *   Refactoring code based on feedback received from the Validator.

### 2.2 MVP 44 (Tesla-Code-Auditor) - The "Gatekeeper/Validator"
*   **Role**: Acts as the strict auditor and quality gatekeeper for all code produced by the Actor.
*   **Responsibilities**:
    *   Conducting deep static analysis, security audits, and complexity checks.
    *   Running comprehensive smoke tests and integration test suites in an isolated environment.
    *   Evaluating adherence to project guidelines and best practices.
    *   Generating structured, actionable feedback loops (Pass/Fail with specific error traces and remediation instructions).
    *   Approving code for final merge/commit only when all quality gates are cleared.

## 3. The Loop Engineering Workflow (Dependencies & Interfaces)
1.  **Initiation (Actor -> Validator)**: MVP 16 generates a code artifact and pushes it to an intermediate validation queue or direct API endpoint exposed by MVP 44.
2.  **Validation Phase (Validator)**: MVP 44 intercepts the artifact. It executes its suite of audits (security, style, functional smoke tests).
3.  **Feedback Loop (Validator -> Actor)**:
    *   *If Pass*: MVP 44 flags the artifact as `VALIDATED`. The code proceeds to the deployment or repository synchronization phase (handled by other agents like Tesla-Github-Manager).
    *   *If Fail*: MVP 44 compiles an error report containing stack traces, security warnings, and specific lines of failure. This report is sent back to MVP 16.
4.  **Refactoring (Actor)**: MVP 16 ingests the failure report, modifies the code to address the concerns, and restarts the loop at Step 1.

## 4. Interfaces
*   **Actor-to-Validator Payload**: JSON/YAML containing the file path, code content, intended functionality description, and dependency list.
*   **Validator-to-Actor Response**: JSON/YAML containing `status` (`pass`/`fail`), `error_logs`, `security_warnings`, and `suggested_fixes`.

## 5. Conclusion
This iterative, mandatory feedback loop ensures that no unverified code enters the main repository. MVP 16 focuses on creative problem-solving and implementation, while MVP 44 enforces strict, uncompromising quality control.
