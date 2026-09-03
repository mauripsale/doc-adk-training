#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting publish process to 'main' (Student Branch)...${NC}"

# 1. Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Error: You have uncommitted changes. Please commit or stash them first.${NC}"
    exit 1
fi

# Save current branch name to switch back later
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "solution" ]; then
     echo -e "${YELLOW}⚠️ You are not on the 'solution' branch. Switching to 'solution' first to ensure we have the latest source.${NC}"
     git checkout solution
     git pull origin solution
fi

# 2. Switch to main and update
echo -e "${GREEN}🔄 Switching to 'main' and merging changes from 'solution'...${NC}"
git checkout main
git pull origin main

# Merge solution into main with -X theirs strategy to accept solution as single source of truth
git merge solution -X theirs --no-commit --no-edit || {
    echo -e "${YELLOW}⚠️ Handling conflict cleanup automatically...${NC}"
    git checkout --theirs . 2>/dev/null || true
}

# 3. Clean up solution files
echo -e "${YELLOW}🧹 Ensuring no solution files exist in 'main'...${NC}"
find . -name "lab-solution.md" -type f -delete
git add -A
git commit -m "chore: sync updates from solution to main without solutions" || echo "Nothing to commit"

# 4. Push to origin
echo -e "${GREEN}⬆️ Pushing 'main' to origin...${NC}"
git push origin main

# 6. Return to original branch
echo -e "${GREEN}🔙 Returning to branch '$CURRENT_BRANCH'...${NC}"
git checkout $CURRENT_BRANCH

echo -e "${GREEN}✅ Done! Students branch 'main' is up to date and clean.${NC}"
