# PLAN D'INTERVENTION COMPLET — Finalisation MVP 28 (Loop Engineering × Tesla-Code-Auditor)

**Orchestrateur** : `tesla-team-synergy`
**Doctrine** : Vigilum Codex (Act-Verify-Learn-Repeat)
**Statut** : 🔴 À EXÉCUTER (Linéaire, Chronologique)

## Architecture Cible (Rappel)
Le principe fondamental est la séparation physique des responsabilités. `tesla-master-code` ne peut pas s'auto-certifier.
Master-Code produit → Loop orchestre → Code-Auditor juge → TGG gouverne → Alexandria mémorise → Mahonheim conserve l'autorité.

## Phase A — Préparation et Alignement Canonique (tesla-curator-prime & tesla-arcanis-360)
1. **Vérification de l'existant physique** : Confirmer la présence de `SKILL.md` (loop-orchestrator, code-auditor), `tesla_loop_orchestrator.py`, les contrats YAML, et le schéma SQLite v2.0.
2. **Alignement des fichiers canoniques de gouvernance** : Mettre à jour `AGENTS.md`, `FORCE_TOOLING.md`, `GEMINI.md`, `ENGINE.md` pour inclure Loop/Code-Auditor.
3. **Validation du contrat de boucle YAML** : Valider le template contenant les 4 validateurs et les critères de transition.

## Phase B — Intégration Technique (tesla-master-code)
4. **Câblage Loop Orchestrator → Master-Code** : `invoke_subagent` vers master-code, production de `output_manifest.json`.
5. **Câblage Loop Orchestrator → Code Auditor** : Exécution de la chaîne à 4 niveaux (SemGrep, Pyright, Smoke Tests, Policy Engine) pour produire un `audit_verdict.json`.
6. **Câblage des transitions (PASS/DELAY/BLOCK)** : Logique de décision stricte, y compris rollback via Git ou shutil.
7. **Persistance SQLite** : Vérification du schéma `loop_executions` et `loop_iterations` dans `alexandria_brain.db`.
8. **Intégration du Tesla Governance Gateway (TGG)** : Vérification anti-doublon, quotas et enregistrement de l'acteur avant démarrage de boucle.

## Phase C — Documentation (tesla-writing-skills & tesla-curator-prime)
9. **Rédaction du README.md d'autorité** : Dans `MVP-GITHUB/28-Loop-Engineering/` avec 4 badges obligatoires et architecture.
10. **Mise à jour de l'inventaire taxonomique** : Statut **[INTÉGRATION FINALE — MVP 28]** dans `liste_projets_antigravity_BASE.md`.
11. **Synchronisation du répertoire `/memory/`** : Mettre à jour `PROJECT_STATE.md`, `SESSION_LOG.md`, etc.

## Phase D — Validation Physique (tesla-master-code & tesla-premortem)
12. **Scénario 1 (PASS)** : Tâche triviale (code sans faute), verdict PASS, commit.
13. **Scénario 2 (DELAY puis PASS)** : Code avec avertissement Pyright -> correction ciblée -> PASS en itération 2.
14. **Scénario 3 (BLOCK et Rollback)** : Tâche avec faille SemGrep (`eval`) -> verdict BLOCK immédiat -> Rollback.
15. **Audit Premortem final** : Rapport d'échec potentiel via 3 profils.

## Phase E — Publication et Clôture (tesla-web-raider & tesla-curator-prime)
16. **Publication** : Double synchronisation vers `MVP-GITHUB/28-Loop-Engineering/` (push distant avec autorisation).
17. **Assimilation Canonique** : Vérification que l'ADN Tesla est complètement synchronisé.
18. **Clôture** : Mettre à jour `Gestion-de-Chantiers/INDEX.md`, archiver la roadmap, et rendre la main à Lord Mahonheim.

---
**Critère de sortie absolu** :
Les 8 conditions définies (orchestrateur pilote, séparation écrivain/auditeur, 4 validateurs actifs, transitions déterministes, rollback fonctionnel, SQLite à jour, pilote de non-régression, TGG actif) doivent être formellement démontrées.
