#!/bin/bash

# Script to prepare the repository for GitHub

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Preparing Farmora repository for GitHub...${NC}"

# Make sure we don't include .env files
echo -e "${GREEN}Checking for .env files...${NC}"
find . -name ".env" -type f | while read file; do
  echo "Warning: .env file found: $file - ensure this is in .gitignore"
done

# Clean up Python cache files
echo -e "${GREEN}Cleaning up Python cache files...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

echo -e "${GREEN}Repository is ready for upload!${NC}"
echo -e "Suggested commit message: \"Implement Appwrite authentication for Farmora backend\""
echo -e "Use the following command to push to GitHub:"
echo -e "git add ."
echo -e "git commit -m \"Implement Appwrite authentication for Farmora backend\""
echo -e "git push origin main"
