#!/usr/bin/env python3
"""Vigilum Codex 2.5.1 — Garde d'Usurpation Git (Phase 1 du plan V2.5.0, audité).

Verrou déterministe D-007 : l'Orchestrateur ne doit physiquement plus pouvoir
exécuter de commandes Git mutantes. La juridiction Git (add/commit/push/cp de
staging, publication) appartient EXCLUSIVEMENT à l'agent d'élite
``tesla-github-manager`` (Règle Absolue N°4 : « AGENTS délègue, il ne
réimplémente pas »).

Doctrine appliquée :
  P4  — L'IA propose, le code valide : la classification est un parseur
        déterministe, pas une consigne textuelle.
  P10 — FAIL-CLOSED : tout « git » non classé avec certitude comme lecture
        pure est rejeté (verbe inconnu, alias, occurrence non parseable,
        obfuscation via wrappers/quoting/substitution).
  P3  — UNKNOWN != PASS : un verbe non reconnu n'est jamais autorisé.

Contrat d'entrée (mode hook) : payload JSON Antigravity sur stdin —
  {"conversationId": "...", "toolCall": {"name": "run_command", "args": {...}}}
Contrat de sortie : décision JSON — {"decision": "allow"|"deny", "reason": "..."}

Identité de l'appelant (ordre de résolution déterministe) :
  1. variable d'environnement TESLA_AGENT_IDENTITY (posée par le runtime
     lors du spawn du sous-agent) ;
  2. champ payload toolCall.args.agent_id / caller.agent_id ;
  3. défaut : "orchestrator" (moindre privilège).

Performances : analyse en O(n) sur la longueur de la commande, sans réseau,
sans I/O disque ; un seul processus Python par interception.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from typing import Any

# --------------------------------------------------------------------------- #
# Constantes de juridiction                                                    #
# --------------------------------------------------------------------------- #
GIT_JURISDICTION_AGENT = "tesla-github-manager"
DEFAULT_CALLER = "orchestrator"

COMMAND_TOOLS_DEFAULT = {"run_command", "bash", "shell", "execute_command",
                         "terminal", "run_cmds", "command"}

# --------------------------------------------------------------------------- #
# Tables de verbes Git (V2.5.1 — arbitrage audit : mutation = fail-closed)     #
# --------------------------------------------------------------------------- #
GIT_READ_VERBS: frozenset[str] = frozenset({
    "status", "log", "diff", "show", "rev-parse", "ls-files", "ls-remote",
    "blame", "annotate", "shortlog", "describe", "cat-file", "name-rev",
    "check-ignore", "check-attr", "check-mailmap", "count-objects",
    "for-each-ref", "whatchanged", "verify-commit", "verify-tag",
    "merge-base", "diff-tree", "rev-list", "show-branch", "var", "help",
    "version", "archive", "bundle", "cherry", "format-patch", "grep",
    "range-diff", "patch-id", "send-email",
})

# Verbes avec sous-verbes : lecture UNIQUEMENT pour les formes listées ;
# toute autre forme est mutante (fail-closed).
GIT_SUBVERB_READ: dict[str, frozenset[str]] = {
    "stash": frozenset({"list", "show"}),
    "reflog": frozenset({"show"}),
    "remote": frozenset({"show", "get-url"}),
    "notes": frozenset({"list", "show"}),
    "worktree": frozenset({"list"}),
    "submodule": frozenset({"status"}),
    "config": frozenset({"--get", "--get-all", "--get-regexp", "--list", "-l"}),
}

# Tout verbe absent des tables ci-dessus (alias utilisateur, verbe inconnu,
# forme « git » seul qui ouvre un shell) est réputé MUTANT (P3/P10).
GIT_MUTATING_VERBS: frozenset[str] = frozenset({
    "add", "commit", "push", "pull", "fetch", "merge", "rebase", "reset",
    "checkout", "switch", "restore", "clean", "rm", "mv", "tag", "stash",
    "apply", "am", "cherry-pick", "revert", "clone", "init", "config",
    "filter-branch", "worktree", "submodule", "remote", "bisect", "gc",
    "prune", "reflog", "notes", "replace", "update-ref", "delete-ref",
    "symbolic-ref", "update-index", "read-tree", "write-tree", "commit-tree",
    "hash-object", "send-pack", "receive-pack", "update-server-info",
    "sparse-checkout", "maintenance", "repack", "multi-pack-index",
    "hook", "daemon", "instaweb", "citool", "gui", "p4", "svn", "cvs*",
    "cvsserver", "difftool--helper", "fsck", "unpacked-objects",
})

# Flags globaux de git consommant la valeur qui suit.
GIT_GLOBAL_FLAGS_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree",
                                         "--namespace", "--super-prefix",
                                         "--exec-path"})
# Flags globaux auto-suffisants (forme --clef=valeur).
GIT_GLOBAL_SELFCONTAINED_PREFIXES = ("--git-dir=", "--work-tree=",
                                     "--namespace=", "--super-prefix=",
                                     "--exec-path=")
# Flags globaux sans valeur tolérés.
GIT_GLOBAL_FLAGS_ALONE = frozenset({
    "--no-pager", "--paginate", "--no-optional-locks", "--bare",
    "--literal-pathspecs", "--glob-pathspecs", "--noglob-pathspecs",
    "--icase-pathspecs", "--no-replace-objects", "--textconv",
    "--no-textconv", "--exec-path", "--html-path", "--man-path",
    "--info-path",
})

# --------------------------------------------------------------------------- #
# Tables GitHub CLI (gh) — extension V2.5.1 : la juridiction couvre aussi       #
# les mutations d'API distantes (pr/release/repo), pas seulement git(1).       #
# --------------------------------------------------------------------------- #
GH_READ_TWO_TOKEN_VERBS: frozenset[tuple[str, str]] = frozenset({
    ("pr", "view"), ("pr", "list"), ("pr", "status"), ("pr", "checks"),
    ("pr", "diff"), ("repo", "view"), ("repo", "list"),
    ("release", "view"), ("release", "list"), ("release", "download"),
    ("run", "list"), ("run", "view"), ("run", "watch"),
    ("issue", "view"), ("issue", "list"), ("issue", "status"),
    ("auth", "status"), ("gist", "view"), ("label", "list"),
    ("secret", "list"), ("search", "prs"), ("search", "repos"),
    ("search", "issues"), ("search", "code"), ("search", "commits"),
    ("api", "GET"),
})

# --------------------------------------------------------------------------- #
# Structures de commande : séparateurs, wrappers, redirections                 #
# --------------------------------------------------------------------------- #
SEPARATOR_TOKENS = frozenset({"&&", "||", ";", "|", "&", "(", ")"})
REDIRECT_OPS = frozenset({">", ">>", "<", "<<", "&>", "&>>", "2>", "2>>",
                          "1>", "1>>", ">&"})
# Wrappers à ignorer pour atteindre la commande réelle.
# « value » : flags consommant l'argument suivant ; « alone » : flags sans
# argument ; « positional » : nombre d'arguments positionnels à sauter
# (ex: la durée de `timeout 30 <cmd>`).
WRAPPER_RULES: dict[str, dict[str, frozenset[str] | int]] = {
    "sudo": {"value": frozenset({"-u", "-g", "-p", "-C", "-r", "-t"}),
             "alone": frozenset({"-i", "-s", "-E", "-e", "-H", "-K", "-k",
                                 "-l", "-A", "-S", "-v", "-n", "--"}),
             "positional": 0},
    "env": {"value": frozenset({"-u"}),
            "alone": frozenset({"-i", "--ignore-environment"}),
            "positional": 0},
    "timeout": {"value": frozenset({"-k", "-s", "--signal", "--kill-after"}),
                "alone": frozenset({"-f", "--foreground", "--preserve-status"}),
                "positional": 1},  # la durée précède la commande
    "nice": {"value": frozenset({"-n", "--adjustment"}),
             "alone": frozenset(), "positional": 0},
    "stdbuf": {"value": frozenset({"-o", "-e", "-i", "--output", "--error",
                                   "--input"}),
               "alone": frozenset(), "positional": 0},
    "nohup": {"value": frozenset(), "alone": frozenset(), "positional": 0},
    "command": {"value": frozenset(), "alone": frozenset({"-v", "-V", "-p"}),
                "positional": 0},
    "exec": {"value": frozenset(), "alone": frozenset(), "positional": 0},
    "xargs": {"value": frozenset({"-I", "-n", "-P", "-L", "-s", "-j",
                                  "--arg-file", "--max-args", "--max-procs"}),
              "alone": frozenset({"-r", "--no-run-if-empty", "-0", "--null",
                                  "-t", "--verbose"}),
              "positional": 0},
}
ENV_VAR_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*")
# Interpréteurs dont la charge utile -c doit être analysée récursivement.
SH_WRAPPERS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "ash"})
SUBSTITUTION_HINT_RE = re.compile(r"\$\(|`")
MAX_RECURSION = 3

GIT_WORD_RE = re.compile(r"(?<![A-Za-z0-9_/.-])git(?![A-Za-z0-9_.-])")
GH_WORD_RE = re.compile(r"(?<![A-Za-z0-9_/.-])gh(?![A-Za-z0-9_.-])")


def _is_git_token(token: str) -> bool:
    return token == "git" or token.endswith("/git")


def _is_gh_token(token: str) -> bool:
    return token == "gh" or token.endswith("/gh")


# --------------------------------------------------------------------------- #
# Classification d'une exécution git isolée                                    #
# --------------------------------------------------------------------------- #
def _classify_git_run(run: list[str]) -> dict[str, Any]:
    """run commence par le token git. Retourne {verb, verdict, reason}."""
    idx = 1  # saute le token git
    verb = None
    while idx < len(run):
        tok = run[idx]
        if tok in GIT_GLOBAL_FLAGS_WITH_VALUE:
            idx += 2  # flag + valeur
            continue
        if tok.startswith(GIT_GLOBAL_SELFCONTAINED_PREFIXES):
            idx += 1
            continue
        if tok in GIT_GLOBAL_FLAGS_ALONE:
            idx += 1
            continue
        if tok.startswith("-"):
            # Flag global inconnu : non parsable avec certitude -> mutant.
            return {"verb": None, "verdict": "MUTATING",
                    "reason": f"UNKNOWN_GIT_GLOBAL_FLAG:{tok}"}
        verb = tok
        break
    if verb is None:
        # « git » sans verbe ouvre un shell interactif : mutant.
        return {"verb": None, "verdict": "MUTATING",
                "reason": "GIT_SHELL_MODE"}

    if verb in GIT_READ_VERBS:
        return {"verb": verb, "verdict": "READ", "reason": None}

    if verb in GIT_SUBVERB_READ:
        # Forme de lecture autorisée UNIQUEMENT pour le sous-verbe listé.
        sub = run[idx + 1] if idx + 1 < len(run) else None
        if sub in GIT_SUBVERB_READ[verb]:
            return {"verb": f"{verb} {sub}", "verdict": "READ", "reason": None}
        return {"verb": verb, "verdict": "MUTATING",
                "reason": "GIT_MUTATING_SUBVERB"}

    # Alias utilisateur (git config alias.*) ou verbe inconnu : fail-closed.
    return {"verb": verb, "verdict": "MUTATING", "reason": "GIT_MUTATING_VERB"}


def _classify_gh_run(run: list[str]) -> dict[str, Any]:
    """run commence par le token gh (API GitHub)."""
    rest = [t for t in run[1:] if not t.startswith("-")]
    if not rest:
        return {"verb": None, "verdict": "MUTATING", "reason": "GH_BARE"}
    if len(rest) >= 2 and (rest[0], rest[1]) in GH_READ_TWO_TOKEN_VERBS:
        return {"verb": f"{rest[0]} {rest[1]}", "verdict": "READ",
                "reason": None}
    # « gh api » arbitraire, alias, verbe inconnu : fail-closed.
    verb = " ".join(rest[:2]) if len(rest) >= 2 else rest[0]
    return {"verb": verb, "verdict": "MUTATING", "reason": "GH_MUTATING_VERB"}


# --------------------------------------------------------------------------- #
# Segmentation : découpe le flux de tokens en exécutions (runs)                #
# --------------------------------------------------------------------------- #
def _split_runs(tokens: list[str]) -> tuple[list[list[str]], int]:
    """Découpe en exécutions ; retourne (runs, nb de tokens 'git'/'gh'
    consommés comme cibles de redirection — comptabilisés, jamais exécutés)."""
    runs: list[list[str]] = []
    current: list[str] = []
    accounted_arg_git = 0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in REDIRECT_OPS:
            # La cible de redirection est un nom de fichier, pas une commande.
            if current:
                runs.append(current)
                current = []
            if i + 1 < len(tokens):
                target = tokens[i + 1]
                if _is_git_token(target) or _is_gh_token(target):
                    accounted_arg_git += 1
                i += 1  # consomme la cible
            i += 1
            continue
        if tok in SEPARATOR_TOKENS:
            if current:
                runs.append(current)
                current = []
            i += 1
            continue
        current.append(tok)
        i += 1
    if current:
        runs.append(current)
    return runs, accounted_arg_git


def _strip_wrappers(run: list[str], depth: int) -> tuple[list[str], list[str]]:
    """Retire les préfixes wrappers (sudo/env/timeout/xargs/sh -c...).

    Retourne (run_effectif, payloads_sh_c) — les charges utiles « sh -c »
    sont extraites pour analyse récursive.
    """
    payloads: list[str] = []
    idx = 0
    while idx < len(run):
        head = run[idx].rsplit("/", 1)[-1]
        rules = WRAPPER_RULES.get(head)
        if rules is not None:
            idx += 1
            value_flags = rules["value"]
            alone_flags = rules["alone"]
            positional = int(rules["positional"])
            while idx < len(run):
                tok = run[idx]
                if head == "env" and ENV_VAR_RE.fullmatch(tok):
                    idx += 1
                    continue
                if tok in value_flags:
                    idx += 2
                    continue
                if tok in alone_flags:
                    idx += 1
                    continue
                if tok.startswith("-") and tok != "--":
                    # Option du wrapper non listée : sautée (ex: --quiet).
                    idx += 1
                    continue
                break
            # Arguments positionnels du wrapper (ex: durée de timeout).
            while positional > 0 and idx < len(run) and not run[idx].startswith("-"):
                idx += 1
                positional -= 1
            continue
        if head in SH_WRAPPERS:
            # sh -c 'charge utile' : la charge est le token suivant.
            if idx + 1 < len(run) and run[idx + 1] == "-c" and idx + 2 < len(run):
                payloads.append(run[idx + 2])
                idx += 3
                continue
            if idx + 1 < len(run) and run[idx + 1].startswith("-"):
                idx += 2
                continue
            idx += 1
            continue
        break
    return run[idx:], payloads


def _classify_token_list(tokens: list[str], depth: int) -> dict[str, Any]:
    """Classifie récursivement un flux de tokens shell."""
    findings: list[dict[str, Any]] = []
    accounted_arg_git = 0

    runs, redirected_git = _split_runs(tokens)
    accounted_arg_git += redirected_git

    for run in runs:
        effective, sh_payloads = _strip_wrappers(run, depth)
        for payload in sh_payloads:
            if depth < MAX_RECURSION:
                sub = _classify_string(payload, depth + 1)
                findings.extend(sub["findings"])
                accounted_arg_git += sub["accounted_arg_git"]
            else:
                findings.append({"tool": "sh", "verb": None,
                                 "verdict": "MUTATING",
                                 "reason": "RECURSION_LIMIT"})
        if not effective:
            continue
        if _is_git_token(effective[0]):
            findings.append({"tool": "git", **_classify_git_run(effective)})
        elif _is_gh_token(effective[0]):
            findings.append({"tool": "gh", **_classify_gh_run(effective)})
        else:
            # Occurrences de git/gh en position d'ARGUMENT (ex. echo git) :
            # comptabilisées pour la réconciliation, jamais exécutées.
            for tok in effective[1:]:
                if _is_git_token(tok) or _is_gh_token(tok):
                    accounted_arg_git += 1

    return {"findings": findings, "accounted_arg_git": accounted_arg_git}


def _classify_string(command: str, depth: int = 0) -> dict[str, Any]:
    try:
        lexer = shlex.shlex(command, posix=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return {
            "verdict": "UNPARSEABLE",
            "reason": "SHELL_QUOTING_UNPARSEABLE",
            "findings": [], "accounted_arg_git": 0,
        }
    result = _classify_token_list(tokens, depth)
    result["verdict"] = "READ"
    result["reason"] = None
    if not result["findings"]:
        result["verdict"] = "NO_GIT"
    for f in result["findings"]:
        if f["verdict"] != "READ":
            result["verdict"] = "MUTATING"
            result["reason"] = f.get("reason") or f.get("verb")
            break
    return result


def classify_command(command: str) -> dict[str, Any]:
    """Classification déterministe complète d'une ligne de commande.

    Verdicts : NO_GIT | READ | MUTATING | UNPARSEABLE.
    Invariant P10 (fail-closed) : toute occurrence du mot « git »/« gh » non
    réconciliée avec une exécution classée READ rend la commande MUTATING.
    """
    command = command.strip()
    if not command:
        return {"verdict": "NO_GIT", "reason": None, "findings": [],
                "accounted_arg_git": 0, "raw_git": 0, "raw_gh": 0}

    result = _classify_string(command, 0)
    raw_git = len(GIT_WORD_RE.findall(command))
    raw_gh = len(GH_WORD_RE.findall(command))

    classified = [f for f in result["findings"]]
    n_git_runs = sum(1 for f in classified if f.get("tool") == "git")
    n_gh_runs = sum(1 for f in classified if f.get("tool") == "gh")
    accounted = result["accounted_arg_git"]

    # Réconciliation fail-closed : chaque occurrence brute doit être expliquée.
    if raw_git > n_git_runs + accounted or raw_gh > n_gh_runs + accounted:
        if result["verdict"] in ("READ", "NO_GIT"):
            result["verdict"] = "MUTATING"
            result["reason"] = "UNRECONCILED_GIT_OCCURRENCE"

    result["raw_git"] = raw_git
    result["raw_gh"] = raw_gh
    return result


# --------------------------------------------------------------------------- #
# Mode hook Antigravity                                                        #
# --------------------------------------------------------------------------- #
COMMAND_FIELDS = ("command", "cmd", "script", "shell_command", "bash_command",
                  "command_line", "commands")


def resolve_caller(payload: dict[str, Any]) -> str:
    env_identity = os.environ.get("TESLA_AGENT_IDENTITY", "").strip()
    if env_identity:
        return env_identity
    tool_call = payload.get("toolCall") or {}
    args = tool_call.get("args") or {}
    for source in (args, payload.get("caller") or {}):
        if isinstance(source, dict):
            for key in ("agent_id", "agent", "identity"):
                value = source.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return DEFAULT_CALLER


def extract_command(payload: dict[str, Any]) -> str | None:
    tool_call = payload.get("toolCall") or {}
    args = tool_call.get("args") or {}
    if isinstance(args, dict):
        for field in COMMAND_FIELDS:
            value = args.get(field)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, list):
                joined = " ".join(str(v) for v in value if isinstance(v, str))
                if joined.strip():
                    return joined
    # Repli : la commande est parfois le premier argument positionnel.
    if isinstance(args, list) and args and isinstance(args[0], str):
        return args[0]
    return None


def evaluate_hook(payload: dict[str, Any]) -> dict[str, Any]:
    tool_call = payload.get("toolCall") or {}
    tool_name = tool_call.get("name") or payload.get("tool_name") or ""
    tools = {t.strip() for t in
             os.environ.get("TESLA_COMMAND_TOOLS", "").split(",") if t.strip()}
    tools = tools or COMMAND_TOOLS_DEFAULT
    if tool_name not in tools:
        return {"decision": "allow"}

    caller = resolve_caller(payload)
    if caller == GIT_JURISDICTION_AGENT:
        return {"decision": "allow",
                "reason": f"Juridiction Git exclusive: {caller}"}

    command = extract_command(payload)
    if command is None:
        return {"decision": "deny",
                "reason": "Exit 81 (D-007): commande non extractible du "
                          "payload (fail-closed)."}

    classification = classify_command(command)
    if classification["verdict"] in ("NO_GIT", "READ"):
        return {"decision": "allow",
                "reason": f"Git lecture pure autorisee ({caller})."}

    verb = classification.get("reason") or "classification"
    return {"decision": "deny",
            "reason": f"Exit 81 (D-007 Anti-Usurpation): commande Git "
                      f"non-lecture ({verb}) reservee a "
                      f"{GIT_JURISDICTION_AGENT}. Delegation requise "
                      f"(Regle N.4)."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Vigilum Codex 2.5.1 — Garde d'usurpation Git (hook + CLI)")
    parser.add_argument("--mode", choices=("hook", "classify"), default="hook",
                        help="hook: payload stdin -> decision ; "
                             "classify: --command -> classification JSON")
    parser.add_argument("--command", help="commande à classifier (mode classify)")
    parser.add_argument("--payload-file", default="-",
                        help="fichier payload ('-' = stdin)")
    args = parser.parse_args(argv)

    if args.mode == "classify":
        if not args.command:
            print(json.dumps({"error": "USAGE: --command requis"}), file=sys.stderr)
            return 64
        print(json.dumps(classify_command(args.command), ensure_ascii=False))
        return 0

    raw = sys.stdin.read() if args.payload_file == "-" else open(
        args.payload_file, "r", encoding="utf-8").read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(json.dumps({"decision": "deny",
                          "reason": f"Exit 10 (SCHEMA): payload invalide: {exc}"}))
        return 0
    print(json.dumps(evaluate_hook(payload), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
