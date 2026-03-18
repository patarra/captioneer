#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"

if [[ -z "$VERSION" ]]; then
    echo "Usage: scripts/release.sh <version>"
    echo "Example: scripts/release.sh 0.2.0"
    exit 1
fi

# Must be on main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" ]]; then
    echo "Error: must be on main (currently on '$BRANCH')"
    exit 1
fi

# Working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: working tree is not clean — commit or stash your changes first"
    exit 1
fi

echo "=> Updating version to $VERSION"
sed -i.bak "s/^version = .*/version = \"$VERSION\"/" pyproject.toml && rm pyproject.toml.bak

echo "=> Running checks"
uv run ruff check .
uv run ruff format --check .
uv run pytest

echo "=> Committing and tagging"
git add pyproject.toml
git commit -m "release $VERSION"
git tag "v$VERSION"

echo "=> Pushing"
git push
git push origin "v$VERSION"

echo "Done — v$VERSION is on its way to PyPI"
