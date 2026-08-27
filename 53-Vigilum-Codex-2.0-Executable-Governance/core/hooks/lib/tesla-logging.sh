#!/usr/bin/env bash
tesla_log() {
  local level="$1"
  shift
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  printf '[%s] [%s] %s\n' "$timestamp" "$level" "$*"
}
