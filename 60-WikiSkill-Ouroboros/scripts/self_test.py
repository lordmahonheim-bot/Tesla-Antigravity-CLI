#!/usr/bin/env python3
"""self_test.py — Harnais de validation déterministe de la boucle WikiSkill/Ouroboros.

Valide, dans des sandboxes temporaires, que la chaîne corrigée est opérationnelle :
  1. bootstrap_runtime (idempotent) crée le socle physique canonique ;
  2. schemas.py scelle / vérifie une trace et détecte une altération ;
  3. trace_writer.py écrit la trace scellée et met à jour la chaîne de hachage ;
  4. la chaîne de proposition de patch (proposer -> formatter -> broker ->
     sandbox -> committer) est cohérente et aboutit à un commit ;
  5. le Gating refuse (fail-closed) les datasets absents et les worktrees vides.

Exit code 0 si TOUS les contrôles PASSent, 1 sinon.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

SKILL_MD = """---
name: tesla-web-raider
status: production
---

# SYSTEM SPECIFICATION : TESLA-WEB-RAIDER

## 1. Posture & Core Identity

Soumis a la doctrine du Vigilum Codex.
"""

WIKI_MD = """# WIKI — tesla-web-raider

Documentation vivante du skill.

## Structure

1. Section 1
2. Section 2
3. Section 3
4. Section 4

- Respecter les standards de code.
- Documenter les fonctions complexes.
- Utiliser le typage strict.
"""

TRACE = {
    "trace_id": "trace-0001",
    "skill": "tesla-web-raider",
    "domaine": "web-osint",
    "task_id": "task-0001",
    "model": "self-test",
    "outcome": "success",
    "score": 0.95,
    "verdict_sources": ["source-a", "source-b"],
    "ast_quarantine_status": "safe",
    "steps": [{"tool": "search_web", "ok": True}],
    "final_answer": "Verification factuelle OK",
    "secrets_scrubbed": True,
    "sha256": "",
}

RESULTS = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"  {'[PASS]' if ok else '[FAIL]'} {name}" + (f" — {detail}" if detail else ""))


def run(cmd, cwd=None, expect=0):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != expect:
        print(f"    cmd: {' '.join(cmd)}")
        print(f"    exit={r.returncode} (attendu {expect})")
        print(f"    stdout: {r.stdout}")
        print(f"    stderr: {r.stderr}")
    return r


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="wikiskill_test_"))
    root = work / "tesla"
    try:
        # ---------- 1. Bootstrap ----------
        print("\n[1] Bootstrap du socle physique (idempotent)")
        r = run([sys.executable, str(SCRIPTS / "bootstrap_runtime.py"), "--root", str(root),
                 "--skills", "tesla-web-raider", "--domains", "web-osint"])
        ok = r.returncode == 0
        ok = ok and (root / "runtime/evidence/traces/tesla-web-raider/.staging").is_dir()
        ok = ok and (root / ".agents/wiki/web-osint/index.tsv").is_file()
        ok = ok and (root / ".agents/wiki/web-osint/chain_head.sha256").is_file()
        check("bootstrap cree le socle canonique", ok)

        genesis = (root / ".agents/wiki/web-osint/chain_head.sha256").read_text().strip()
        r2 = run([sys.executable, str(SCRIPTS / "bootstrap_runtime.py"), "--root", str(root),
                  "--skills", "tesla-web-raider", "--domains", "web-osint"])
        after = (root / ".agents/wiki/web-osint/chain_head.sha256").read_text().strip()
        check("bootstrap idempotent (chain_head non ecrase)", r2.returncode == 0 and genesis == after)

        # ---------- 2. schemas : seal / verify / tamper ----------
        print("\n[2] schemas.py : scellement, verification, detection d'alteration")
        trace_path = work / "trace.json"
        trace_path.write_text(json.dumps(TRACE, indent=2), encoding="utf-8")
        sealed_path = work / "trace.sealed.json"
        r = run([sys.executable, str(SCRIPTS / "schemas.py"), "--seal",
                 "--input", str(trace_path), "--out", str(sealed_path)])
        sealed_ok = r.returncode == 0 and sealed_path.is_file() and json.loads(sealed_path.read_text()).get("sha256")
        check("schemas.py scelle la trace", sealed_ok)

        r = run([sys.executable, str(SCRIPTS / "schemas.py"), "--verify", "--input", str(sealed_path)])
        check("schemas.py verifie l'integrite", r.returncode == 0)

        tampered = json.loads(sealed_path.read_text())
        tampered["outcome"] = "failure"
        tampered_path = work / "trace.tampered.json"
        tampered_path.write_text(json.dumps(tampered, indent=2), encoding="utf-8")
        r = run([sys.executable, str(SCRIPTS / "schemas.py"), "--verify", "--input", str(tampered_path)], expect=1)
        check("schemas.py detecte une alteration (exit 1)", r.returncode == 1)

        # ---------- 3. trace_writer ----------
        print("\n[3] trace_writer.py : ecriture atomique + mise a jour de la chaine")
        r = run([sys.executable, str(SCRIPTS / "trace_writer.py"), str(sealed_path),
                 "--root", str(root), "--update-chain"])
        trace_dir = root / "runtime/evidence/traces/tesla-web-raider"
        written = [p for p in trace_dir.glob("*.json")] if trace_dir.is_dir() else []
        chain_after_trace = (root / ".agents/wiki/web-osint/chain_head.sha256").read_text().strip()
        check("trace_writer ecrit la trace scellee", r.returncode == 0 and len(written) == 1)
        check("trace_writer met a jour la chaine de hachage", chain_after_trace != genesis)

        # ---------- 4. Chaîne de proposition de patch ----------
        print("\n[4] Chaîne de patch .intent (proposer -> formatter -> broker -> sandbox -> committer)")
        gitrepo = work / "gitrepo"
        gitrepo.mkdir()
        skill_dir = gitrepo / ".agents/skills/tesla-web-raider"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
        (skill_dir / "WIKI.md").write_text(WIKI_MD, encoding="utf-8")

        def git(*a):
            return subprocess.run(["git", *a], cwd=gitrepo, capture_output=True, text=True)

        git("init", "-q")
        git("config", "user.name", "self-test")
        git("config", "user.email", "self-test@local")
        git("add", ".")
        git("commit", "-q", "-m", "initial")

        proposals = work / "proposals"
        r = run([sys.executable, str(SCRIPTS / "skill_proposer.py"), "tesla-web-raider",
                 "--proposal-dir", str(proposals)])
        patch_files = list(proposals.glob("*.intent.patch"))
        check("skill_proposer genere un .intent.patch", r.returncode == 0 and len(patch_files) == 1)
        patch = patch_files[0]

        r = run([sys.executable, str(SCRIPTS / "intent_formatter.py"), str(patch)])
        check("intent_formatter valide le format canonique", r.returncode == 0)

        r = run([sys.executable, str(SCRIPTS / "patch_broker.py"), str(patch)])
        check("patch_broker valide la structure", r.returncode == 0)

        gating = str(SCRIPTS / "gating_judge.py")
        sandbox = str(SCRIPTS / "sandbox_evaluator.py")
        r = run([sys.executable, sandbox, str(patch), "--repo-path", str(gitrepo), "--eval-script", gating])
        check("sandbox_evaluator : gating passe dans le worktree", r.returncode == 0)

        r = run([sys.executable, str(SCRIPTS / "git_committer.py"), str(patch),
                 "--repo-path", str(gitrepo), "--sandbox-script", sandbox, "--gating-script", gating])
        log = git("log", "--oneline")
        check("git_committer applique et commit le patch", r.returncode == 0 and "[WikiSkill]" in log.stdout)

        # ---------- 5. Fail-closed ----------
        print("\n[5] Gating fail-closed (aucune simulation)")
        empty = work / "empty_worktree"
        empty.mkdir()
        r = run([sys.executable, gating, str(empty), "--skill", "tesla-web-raider"], expect=1)
        check("gating refuse un worktree sans SKILL (exit 1)", r.returncode == 1)

        r = run([sys.executable, gating, str(gitrepo), "--skill", "tesla-web-raider",
                 "--dataset-dir", str(work / "no_datasets")], expect=1)
        check("gating refuse l'absence de dataset (exit 1)", r.returncode == 1)

    finally:
        shutil.rmtree(work, ignore_errors=True)

    failed = [r for r in RESULTS if not r[1]]
    print("\n" + "=" * 60)
    print(f"RESULTAT SELF-TEST : {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        for name, _, detail in failed:
            print(f"  FAILED: {name} {detail}")
        return 1
    print("TOUS LES CONTRÔLES PASSENT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
