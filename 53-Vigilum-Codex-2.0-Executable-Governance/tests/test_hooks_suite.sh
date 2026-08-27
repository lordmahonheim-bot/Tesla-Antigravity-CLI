#!/usr/bin/env bash
set -eu

root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

export GIT_CONFIG_NOSYSTEM=1
export HOME="$tmp/home"
mkdir -p "$HOME"

git -C "$tmp" init -q
git -C "$tmp" config user.email test@example.invalid
git -C "$tmp" config user.name test
git -C "$tmp" config core.hooksPath "$root/core/hooks"

# Test 1: Valid schema pass
printf '{"ok":true}\n' > "$tmp/good.json"
git -C "$tmp" add good.json
(cd "$tmp" && "$root/core/hooks/pre-commit/tesla-pre-commit-main.sh")

# Test 2: Invalid JSON syntax (Exit 10)
printf '{not-json}\n' > "$tmp/bad.json"
git -C "$tmp" add bad.json
set +e
(cd "$tmp" && "$root/core/hooks/pre-commit/tesla-pre-commit-main.sh")
status=$?
set -e
[ "$status" -eq 10 ] || { echo "expected schema exit 10, got $status" >&2; exit 1; }

# Test 3: Secret scanner (Exit 20)
git -C "$tmp" reset -q
printf 'api_key="sk-test-01234567890123456789"\n' > "$tmp/secret.txt"
git -C "$tmp" add secret.txt
set +e
(cd "$tmp" && "$root/core/hooks/pre-commit/tesla-pre-commit-main.sh")
status=$?
set -e
[ "$status" -eq 20 ] || { echo "expected secret exit 20, got $status" >&2; exit 1; }

# Test 4: Unset push auth file (Exit 70)
set +e
(cd "$tmp" && "$root/core/hooks/pre-push/tesla-pre-push-main.sh")
status=$?
set -e
[ "$status" -eq 70 ] || { echo "expected push exit 70, got $status" >&2; exit 1; }

# Test 5: Valid push authorization token (Exit 0)
auth_file="$tmp/push_auth.json"
cat > "$auth_file" <<JSON
{
  "authorized": true,
  "mission_id": "SGC-EXEC-GOV-03",
  "repository": "lordmahonheim-bot/Tesla-Antigravity-CLI",
  "ref": "refs/heads/master",
  "expires_at": $(($(date +%s) + 3600)),
  "nonce": "test-nonce-12345"
}
JSON

export TESLA_PUSH_AUTH_FILE="$auth_file"
(cd "$tmp" && "$root/core/hooks/pre-push/tesla-pre-push-main.sh")

# Test 6: Anti-Replay Invariant A-003 (Replay of same nonce must FAIL with Exit 70)
set +e
(cd "$tmp" && "$root/core/hooks/pre-push/tesla-pre-push-main.sh")
replay_status=$?
set -e
[ "$replay_status" -eq 70 ] || { echo "expected anti-replay exit 70, got $replay_status" >&2; exit 1; }

echo "Hook suite passed completely (All 6 tests OK, including A-003 anti-replay)."
