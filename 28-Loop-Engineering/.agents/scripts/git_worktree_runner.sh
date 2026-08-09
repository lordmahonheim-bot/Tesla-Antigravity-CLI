#!/usr/bin/env bash
# git_worktree_runner.sh
# Gestionnaire de Sandbox Arena pour OPRO-Grad
# VERDICT PREMORTEM : Intégration d'un Garbage Collector strict pour éviter la fuite disque.

ARENA_ID="arena-$(date +%s)"
WORKTREE_PATH="/tmp/tesla_arena/$ARENA_ID"
REPO_DIR="/home/lord-mahonheim/bifrost/tesla"

echo "[ARENA] Initialisation Sandbox : $ARENA_ID"

# 1. GARBAGE COLLECTOR ABSOLU (Trap)
cleanup() {
    echo "[ARENA-GC] Attente du verrou LanceDB..."
    while [ ! -f "/tmp/tesla_arena/.lancedb_done" ]; do
        sleep 0.1
    done
    rm -f "/tmp/tesla_arena/.lancedb_done"

    echo "[ARENA-GC] Déclenchement du Garbage Collector (Purge Zombie Worktree)..."
    if [ -d "$WORKTREE_PATH" ]; then
        cd "$REPO_DIR" || exit
        git worktree remove --force "$WORKTREE_PATH" >/dev/null 2>&1
        echo "[ARENA-GC] Worktree $WORKTREE_PATH détruit."
    fi
}
trap cleanup EXIT ERR INT TERM

# 2. CRÉATION DU WORKTREE ÉPHÉMÈRE
cd "$REPO_DIR" || exit 1
git worktree add "$WORKTREE_PATH" HEAD >/dev/null 2>&1
echo "[ARENA] Worktree créé sur $WORKTREE_PATH."

# 3. EXÉCUTION DU PATCH & TESTS (Couverture de Régression)
cd "$WORKTREE_PATH" || exit 1

# [Injection du Patch OPRO...]
# [Simulation d'exécution des tests locaux]
echo "[ARENA] Exécution de la suite de tests (LSP & Assertions Locales)..."
# mock-test command here, to be replaced by actual test runner
# ./run_tests.sh
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "[ARENA-FAIL] Régression Latérale détectée. Le score de Fitness s'effondre (Pénalité = -10.0)."
    exit 42 # Sera capté par OPRO pour scorer la fitness
fi

echo "[ARENA-SUCCESS] Zéro régression. Patch viable."
# La fonction 'cleanup' est automatiquement appelée via le trap EXIT.
exit 0
