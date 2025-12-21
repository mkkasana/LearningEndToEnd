#!/bin/bash

# Script to reset git history and prepare for new repository
# This will create a fresh git history with a single commit

echo "🔄 Resetting git history for LearningEndToEnd..."

# Step 1: Remove the old git history
echo "📦 Removing old git history..."
rm -rf .git

# Step 2: Initialize a new git repository
echo "🆕 Initializing new git repository..."
git init

# Step 3: Add all files
echo "➕ Adding all files..."
git add .

# Step 4: Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: LearningEndToEnd project

Full-stack learning project with FastAPI backend and React frontend.
Based on FastAPI full-stack template, customized for learning purposes."

# Step 5: Rename branch to main (if you prefer main over master)
echo "🌿 Renaming branch to main..."
git branch -M main

echo ""
echo "✅ Git history reset complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create a new repository on GitHub named 'LearningEndToEnd'"
echo "2. Run: git remote add origin git@github.com:YOUR_USERNAME/LearningEndToEnd.git"
echo "3. Run: git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME with your GitHub username"
