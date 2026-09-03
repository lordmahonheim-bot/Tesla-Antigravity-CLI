# 🗂️ OPEN ITEMS — Chantiers Futurs Conditionnés (V2.6.1)

**Nature :** Registre des éléments différés (déférérence) — aucune suppression silencieuse (P8).
**Origine :** Verdict d'audit du PLAN D'INTERVENTION DE HAUT NIVEAU V2.6.0 (Phase 1 : Déférement).
**Date :** 2026-09-03

---

## OI-01 — Câblage CI/CD de l'attestation SLSA sur GitHub Actions

| Champ | Valeur |
| :--- | :--- |
| **Statut** | `DEFERRED — CONDITIONED` (non supprimé : l'actif est livré, testé et conservé) |
| **Composant concerné** | `53-Vigilum-Codex-2.0-Executable-Governance/bin/slsa_attestation.py` (8 tests PASS) |
| **Condition de réveil** | Déploiement effectif d'un job GitHub Actions exigeant une preuve Gate 2 (au-delà du `mirror-guard` actuel, qui n'est qu'un garde-fou de miroir unidirectionnel sans Gate) |
| **Travail à réaliser au réveil** | 1. Job de vérification `slsa_attestation.py verify` en tête de pipeline ; 2. Secret `TESLA_CONTROL_PLANE_KEY` côté GitHub Actions (racine hors workspace) ; 3. Passage du niveau L1+HMAC local vers SLSA L2+ (signature native du runner). |

### Note d'audit (corrections apportées au plan V2.6.0)

1. **La prémisse factuelle du déféré est inexacte.** Le plan motive l'annulation par
   « résoudre un problème de runner éphémère cloud *avant son existence* ». Or le
   dépôt possède déjà un runner éphémère cloud : `.github/workflows/mirror-guard.yml`
   (`runs-on: ubuntu-latest`, déclenché sur pull_request). Le déféré reste néanmoins
   admissible *en l'espèce* : ce runner n'exécute aucune Gate Vigilum — aucun besoin
   de preuve Gate 2 n'existe donc aujourd'hui.
2. **L'annulation pure est contradictoire avec la Phase 5 du même plan.** La Gate R
   (« Evidence Reconciliation », P11) exige une signature indépendante du Control
   Plane — c'est précisément la machinerie HMAC/DSSE de `slsa_attestation.py`,
   réutilisée en local par `bin/gate_r.py`. Supprimer l'actif aurait cassé la Gate R.
   Décision : **l'actif est conservé, seul le câblage CI est différé** (présent
   registre).
3. **P8 (No Silent Deletion)** : le présent registre trace le déféré.

---

## OI-02 — Gravure de l'Invariant Cognitif Anti-Friction dans ENGINE.md

| Champ | Valeur |
| :--- | :--- |
| **Statut** | `PENDING SOVEREIGN GRAVURE` — proposition de texte prête, gravure réservée au Souverain |
| **Condition de réveil** | Cérémonie de gravure dans `GENESE-v1/ENGINE.md` (fichier d'identité souverain) |
| **Texte proposé (formulation corrigée par l'audit)** | *« Toute solution proposée par l'agent qui exige de l'opérateur une action hors du chat, alors qu'une voie déterministe in-chat existe (ex. SCD), est invalide et rejetée d'office. La friction évitable est un défaut de conception agentique. En revanche, les ancrages hors-chat du Plan de Contrôle — injection de clé, cérémonies de scellement, veto d'urgence — demeurent des prérogatives souveraines : l'anti-friction lie l'agent, jamais le Souverain. »* |

### Note d'audit

La formulation absolue du plan V2.6.0 (« *Toute solution exigeant de l'opérateur une
action hors du chat est invalide* ») est **rejetée** : elle contredit la racine de
confiance du Codex (clé Control Plane hors workspace, cérémonies `gate2_guard
issue-token`, jeton de push A-001, `TESLA_ALLOW_PRIVILEGE_ESCALATION` au terminal).
Une architecture entièrement in-chat offrirait à l'agent la totalité de ses ancres
de confiance. La version corrigée ci-dessus cible la *friction imposée par l'agent*
(RETEX Incident 2), pas les prérogatives souveraines.

---

## OI-03 — Courtier de délégation Ed25519 sous UID séparé

| Champ | Valeur |
| :--- | :--- |
| **Statut** | `KNOWN LIMITATION` — dépendance PyNaCl déclarée (`requirements.txt`), 26 tests SKIP avec raison P3 explicite |
| **Condition de réveil** | Déploiement du daemon `vigilum_gate_daemon.py` sous un UID distinct (recommandation `RETEX_GATE2_BYPASS.md` §7) |
| **Travail à réaliser au réveil** | Installation PyNaCl, démarrage systemd (`deploy/vigilum-gate.service`), exécution des 26 tests de régression du courtier. |

---

*Résultat du déféré V2.6.1 : aucun composant supprimé ; 1 câblage différé (OI-01) ;
1 gravure souveraine proposée (OI-02) ; 1 limitation documentée (OI-03).*
