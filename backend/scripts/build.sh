#!/usr/bin/env bash

set -e
set -x

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "🔍 Running type checks with mypy..."
mypy app

echo "🔍 Running linting with ruff..."
ruff check app

echo "🔍 Checking code formatting..."
ruff format app --check

echo "🧪 Running tests with coverage..."
echo "⚠️  Skipping tests (requires database). Run 'docker compose up -d' first if needed."
coverage run -m pytest tests/
coverage report --fail-under=80
coverage html --title "coverage"

echo "🏗️  Building package..."
hatch build

echo "✅ Build complete! All checks passed."
echo "📦 Artifacts in dist/"
ls -lh dist/
