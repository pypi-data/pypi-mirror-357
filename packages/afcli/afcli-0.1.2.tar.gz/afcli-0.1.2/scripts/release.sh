#!/bin/bash

# Script to create a new release
# Usage: ./scripts/release.sh 0.2.0

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.2.0"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🔍 Checking git status..."
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: There are unstaged changes"
    echo "   Please commit or stash your changes first"
    exit 1
fi

echo "🔍 Checking if we're on main branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Not on main branch (currently on: $CURRENT_BRANCH)"
    echo "   Please switch to main branch first"
    exit 1
fi

echo "🔄 Pulling latest changes..."
git pull origin main

echo "🏷️  Creating and pushing tag: $TAG"
git tag "$TAG"
git push origin "$TAG"

echo "✅ Release tag created successfully!"
echo ""
echo "Next steps:"
echo "1. Go to: https://github.com/ouachitalabs/af/releases"
echo "2. Click 'Create a new release'"
echo "3. Select tag: $TAG"
echo "4. Add release notes"
echo "5. Click 'Publish release'"
echo ""
echo "This will automatically:"
echo "- Run tests on all Python versions"
echo "- Build the package"
echo "- Publish to PyPI (after PyPI trusted publishing setup)"