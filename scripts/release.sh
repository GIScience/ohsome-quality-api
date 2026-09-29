#!/bin/sh

set -e

if [ $# -eq 0 ]; then
    echo "Please supply one of the following values as argument:"
    echo "major, minor, patch, stable, alpha, beta, rc, post, dev"
    exit
fi

uv version --bump "$1"

NEW_VERSION=$(uv version --short)

$EDITOR CHANGELOG.md
$EDITOR ohsome_quality_api/__init__.py

pytest

git add -p pyproject.toml CHANGELOG.md ohsome_quality_api/__init__.py tests/ 
git add uv.lock

git commit -m "$NEW_VERSION"
git tag "$NEW_VERSION" -m "$NEW_VERSION"
# git push origin main
# git push origin "$NEW_VERSION"
