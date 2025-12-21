#!/usr/bin/env bash

set -e
set -x

echo "🔍 Checking Node.js version..."
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Error: Node.js version 20.19+ or 22.12+ is required"
    echo "Current version: $(node --version)"
    echo "Please upgrade Node.js or use: mise use node@24"
    exit 1
fi
echo "✅ Node.js version: $(node --version)"

echo "📦 Installing dependencies..."
npm install

echo "🔍 Running linter..."
npm run lint

echo "🏗️  Building frontend..."
npm run build

echo "✅ Build complete!"
echo "📦 Build artifacts in dist/ ($(du -sh dist/ | cut -f1))"
ls -lh dist/
