#!/bin/bash

# Build and publish afcli package to PyPI
# Requires PYPI_AUTH_TOKEN environment variable to be set

set -e  # Exit on any error

echo "🔍 Checking git status..."
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: There are unstaged changes in the git repository"
    echo "   Please commit or stash your changes before publishing"
    git status --porcelain
    exit 1
fi

echo "🔨 Building afcli package..."
uv build

echo "📦 Publishing to PyPI..."
if [ -z "$PYPI_AUTH_TOKEN" ]; then
    echo "❌ Error: PYPI_AUTH_TOKEN environment variable is not set"
    echo "   Please set it with: export PYPI_AUTH_TOKEN=your_token_here"
    exit 1
fi

uv publish --token "$PYPI_AUTH_TOKEN"

echo "✅ Package published successfully!"
echo "   Install with: pip install afcli"
echo "   or: uv add afcli"