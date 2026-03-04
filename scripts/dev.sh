#!/usr/bin/env sh
set -eu

# dev.sh - small helper for local dev tasks:
# - format/lint (if configured)
# - run tests
#
# Usage:
#   ./scripts/dev.sh fmt
#   ./scripts/dev.sh lint
#   ./scripts/dev.sh test
#   ./scripts/dev.sh check
#   ./scripts/dev.sh all
#
# Notes:
# - This script is intentionally lightweight and safe if tools aren't installed.
# - It assumes a Python-based LLM project layout; adjust commands as your stack evolves.

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

say() { printf "%s\n" "$*"; }
run() { say "+ $*"; "$@"; }

need_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

usage() {
  cat <<'USAGE'
scripts/dev.sh - local dev helper

Commands:
  fmt     Run formatter(s)
  lint    Run linter(s)
  test    Run tests
  check   Run minimal sanity checks (fmt + lint + test where available)
  all     Same as check

Examples:
  ./scripts/dev.sh fmt
  ./scripts/dev.sh test
USAGE
}

fmt() {
  cd "$ROOT_DIR"

  if need_cmd ruff; then
    run ruff format .
  else
    say "ruff not found; skipping ruff format."
  fi

  if need_cmd black; then
    run black .
  else
    say "black not found; skipping black."
  fi
}

lint() {
  cd "$ROOT_DIR"

  if need_cmd ruff; then
    run ruff check .
  else
    say "ruff not found; skipping ruff check."
  fi

  if need_cmd mypy; then
    run mypy src || true
  else
    say "mypy not found; skipping mypy."
  fi
}

test_cmd() {
  cd "$ROOT_DIR"

  if need_cmd pytest; then
    run pytest -q
  else
    say "pytest not found; skipping tests."
  fi
}

check() {
  fmt
  lint
  test_cmd
  say "Done."
}

cmd="${1:-}"
case "$cmd" in
  fmt) fmt ;;
  lint) lint ;;
  test) test_cmd ;;
  check|all) check ;;
  -h|--help|help|"") usage ;;
  *)
    say "Unknown command: $cmd"
    say ""
    usage
    exit 2
    ;;
esac
