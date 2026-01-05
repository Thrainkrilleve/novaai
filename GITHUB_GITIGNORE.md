# Files to exclude from Git
# Copy this to h:\TheAI\.gitignore

# Environment files (NEVER commit these!)
.env
.env.local
.env.production
backend/.env

# Database files
*.db
*.sqlite
*.sqlite3
backend/chatbot.db
chatbot.db

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments
venv/
env/
ENV/
.venv

# Build artifacts
build/
dist/
*.spec
backend/build/
backend/dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Node modules
node_modules/
frontend/node_modules/
frontend/dist/

# Test files
test_*.py
test_*.txt

# Backup folders
*backup/
*.bak

# Large model files
models/
*.gguf
*.bin

# EVE SDE (too large - download separately)
EveSDE/

# User data
data/*.json
backend/data/*.json

# Temporary files
*.tmp
*.temp
.cache/

# Playwright (not needed in VPS mode)
.playwright/
