# Predictive Failure Diagnosis (Premortem)

## Concept & Gary Klein's Methodology
The Premortem methodology, pioneered by psychologist Gary Klein, is a cognitive strategy used to stress-test project plans. Unlike a postmortem, which examines why a project failed after the fact, a **premortem** occurs *before* deployment. The team assumes the project has completely failed and works backward to identify the vulnerabilities that caused the failure.

## Stress-testing architectures
Using the Premortem approach:
1. We establish a virtual time limit (e.g., T+3 months) and declare the project a catastrophic failure.
2. We perform a structured, tripartite analysis:
   - **Devil's Advocate**: Technical, logical, and code-based failure points (e.g., SSH permission issues, dependency breaks).
   - **Blindspot Inspector**: Unverified assumptions about tools, environments, or operator actions.
   - **Weak Signals Sentinel**: Early-stage signs that indicate drift toward failure.
3. We implement immediate preventive actions and define action thresholds.

## Audit report template
This module provides a standard markdown audit template to run premortems on any software module or organizational system.
The template file is located at [premortem_template.md](file:///home/lord-mahonheim/bifrost/tesla/MVP-GITHUB/08-Premortem-Diagnostic/templates/premortem_template.md).
