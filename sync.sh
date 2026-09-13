#!/bin/zsh

MESSAGE="$1"

if [[ -z "$MESSAGE" ]]; then
  echo "Please provide a commit message."
  echo 'Example: ./sync.sh "Add water detection feature"'
  exit 1
fi

echo "Checking project changes..."
git status

echo "Adding changes..."
git add .

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

echo "Creating commit..."
git commit -m "$MESSAGE"

echo "Pushing to GitHub..."
git push origin main

echo "Everest Intelligence is synchronized with GitHub."
