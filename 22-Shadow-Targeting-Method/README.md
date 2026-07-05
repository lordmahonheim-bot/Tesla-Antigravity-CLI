# 22-Shadow-Targeting-Method — Subagent Injection & Isolation Framework

## Overview
Project 22 documents and standardizes the **Shadow-Targeting** methodology used within the Tesla agentic platform. Operating under the "Vigilum Codex" doctrine, this framework enables loading custom agent skills dynamically into native subagents (such as `self` or native runtime profiles), bypassing account plan constraints while maintaining strict sandbox isolation and tracking.

## Core Principle of Independence
As defined in the technical specification:
*   *Every skill or subagent must remain strictly independent of others in its creation, naming convention, and functional scope.*
*   Components must never use dependency prefixes (e.g., use standalone `tesla-web-raider` instead of coupling it as a sub-component of another specialized agent).

## Repository Layout
```text
22-Shadow-Targeting-Method/
├── README.md
└── shadow-targeting-method.md
```

## Metadata Standards
All shadow-targeted skills must declare the following YAML frontmatter header to ensure discovery and routing:
```yaml
injection_type: shadow-targeted
target_subagent: self # or target profile role
```

## Database Registry
Every injected skill must register a corresponding entry in the local Alexandria database `subagents_skills` table with:
*   `injection_method = 'shadow-targeting'`
*   `statut = 'active'`
