#!/usr/bin/env bash
# wiki-lint.sh — Lightweight LLM-wiki integrity check
# Verifies wiki pages exist, internal links resolve, and raw assets are present.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
errors=0
warnings=0

echo "=== LLM Wiki Lint ==="
echo "Repo: $REPO_ROOT"

# 1. Check required top-level wiki files
for f in index.md log.md docs/LLM-WIKI-PLAN.md; do
  if [ ! -f "$REPO_ROOT/$f" ]; then
    echo "MISSING: $f"
    ((errors++))
  else
    echo "OK: $f"
  fi
done

# 2. Check wiki directories exist and count pages
for d in wiki/entities wiki/concepts wiki/synthesis raw/assets; do
  if [ ! -d "$REPO_ROOT/$d" ]; then
    echo "MISSING DIR: $d"
    ((errors++))
  else
    count=$(find "$REPO_ROOT/$d" -name '*.md' | wc -l | tr -d ' ')
    echo "OK: $d ($count .md files)"
  fi
done

# 3. Check internal links in index.md resolve to actual files
if [ -f "$REPO_ROOT/index.md" ]; then
  while IFS= read -r link; do
    if [ ! -f "$REPO_ROOT/$link" ]; then
      echo "ORPHAN LINK: $link in index.md"
      ((warnings++))
    fi
  done < <(grep -oE '\(wiki/[^)]+\.md\)' "$REPO_ROOT/index.md" | sed 's/(//;s/)//' | sort -u)
fi

# 4. Check raw/assets have required sources
if [ -d "$REPO_ROOT/raw/assets" ]; then
  for f in README.md AGENTS.md DIAGNOSTIC_ENGINE_V1.md upstream-sources.md; do
    if [ ! -f "$REPO_ROOT/raw/assets/$f" ]; then
      echo "MISSING RAW: raw/assets/$f"
      ((warnings++))
    else
      echo "OK RAW: raw/assets/$f"
    fi
  done
  # Check example files exist
  for ext in run.in nep.in; do
    if [ -f "$REPO_ROOT/raw/assets/$ext" ]; then
      echo "OK RAW: raw/assets/$ext"
    else
      echo "MISSING RAW: raw/assets/$ext"
      ((warnings++))
    fi
  done
fi

# 5. Check wiki pages have cross-references
if [ -d "$REPO_ROOT/wiki/entities" ]; then
  for f in "$REPO_ROOT"/wiki/entities/*.md; do
    base=$(basename "$f")
    if ! grep -qE '\[.*\]|相关|Related|See also|参考|wiki/' "$f" 2>/dev/null; then
      echo "NO XREF: $base has no cross-references"
      ((warnings++))
    fi
  done
fi

echo ""
echo "=== Summary ==="
echo "Errors: $errors"
echo "Warnings: $warnings"
if [ "$errors" -gt 0 ]; then
  exit 1
fi
exit 0
