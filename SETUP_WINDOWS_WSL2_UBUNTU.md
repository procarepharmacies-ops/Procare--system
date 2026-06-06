# 🚀 Setup ProCare System on Windows 11 + WSL2 + Ubuntu Server

**Environment**: Windows 11 Host → WSL2 → Ubuntu Server  
**Status**: Complete Setup Guide  
**Date**: 2026-06-06  

---

## 📋 Overview

This guide sets up the complete ProCare Pharmacy Intelligence System on your local Windows 11 machine using WSL2 and Ubuntu Server as the development environment.

**What you'll have:**
- Windows 11 (Host OS)
- WSL2 (Windows Subsystem for Linux 2)
- Ubuntu Server (Linux environment)
- ProCare System (running in Ubuntu)
- Python development environment
- SQL Server connection
- Flask web server
- Slack integration
- Dashboard access from Windows browser

**Total setup time**: ~1-2 hours

---

## 🎯 PHASE 1: Windows 11 Setup (15 minutes)

### Step 1.1: Enable WSL2

**Open PowerShell as Administrator:**
```powershell
# Right-click PowerShell → Run as Administrator
```

**Enable WSL feature:**
```powershell
wsl --install
```

This installs:
- Windows Subsystem for Linux (WSL2)
- Default Ubuntu Linux distribution
- Linux kernel

**Restart your computer** when prompted.

### Step 1.2: Verify WSL2 Installation

After restart, open PowerShell and run:
```powershell
wsl --list --verbose

# Output should show:
# NAME            STATE           VERSION
# Ubuntu          Running         2
```

**Set default version to WSL2:**
```powershell
wsl --set-default-version 2
```

### Step 1.3: Update WSL Kernel

```powershell
wsl --update
```

---

## 🎯 PHASE 2: Ubuntu Server Setup in WSL2 (20 minutes)

### Step 2.1: Launch Ubuntu

Open PowerShell and run:
```powershell
wsl
```

You're now in Ubuntu Linux environment.

### Step 2.2: Initial Ubuntu Configuration

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    unixodbc \
    unixodbc-dev
```

### Step 2.3: Install Python 3.10+

```bash
# Check Python version
python3 --version

# Should be 3.10 or higher
# If not, install:
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Make python3.10 default (optional):
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

### Step 2.4: Create Development Directory

```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Create ProCare directory
mkdir -p procare-dev
cd procare-dev

# Verify
pwd
# Output: /home/[username]/projects/procare-dev
```

---

## 🎯 PHASE 3: Clone Repository (10 minutes)

### Step 3.1: Clone ProCare Repository

```bash
cd ~/projects/procare-dev

# Clone the repository
git clone http://127.0.0.1:32925/git/procarepharmacies-ops/Procare--system.git

cd Procare--system

# Verify
ls -la

# Should show:
# START_HERE.md
# PRODUCTION_GO_LIVE.md
# CLAUDE_CODE_SLACK_PROMPT.md
# tools/
# architecture/
# app.py
# etc.
```

### Step 3.2: Checkout Production Branch

```bash
# List branches
git branch -a

# Checkout the production branch
git checkout claude/slack-session-3hNj0

# Verify
git branch

# Output should show:
# * claude/slack-session-3hNj0
```

---

## 🎯 PHASE 4: Python Virtual Environment (10 minutes)

### Step 4.1: Create Virtual Environment

```bash
cd ~/projects/procare-dev/Procare--system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify (should show "(venv)" prefix in terminal)
# (venv) user@computer:~/projects/procare-dev/Procare--system$
```

### Step 4.2: Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

### Step 4.3: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "flask|slack|pyodbc|python-dotenv"

# Should show:
# flask
# slack-sdk
# pyodbc
# python-dotenv
```

---

## 🎯 PHASE 5: Environment Configuration (10 minutes)

### Step 5.1: Create .env File

```bash
# Copy template to .env
cp .env.template .env

# Edit .env file
nano .env
```

### Step 5.2: Configure Database Connection

**Edit these lines in .env:**

```bash
# SQL SERVER CONFIGURATION
SQL_SERVER=DESKTOP-3A9JFL4
SQL_DATABASE=stock
SQL_USERNAME=[your_sql_username]
SQL_PASSWORD=[your_sql_password]
SQL_DRIVER={ODBC Driver 17 for SQL Server}
```

**Note:** On WSL2, to connect to Windows SQL Server:
- Use the Windows host IP instead of localhost
- Run this in WSL to find Windows host IP:

```bash
cat /etc/resolv.conf | grep nameserver
# Copy the IP address (usually 172.x.x.x)
```

**Update SQL_SERVER in .env:**
```bash
SQL_SERVER=172.x.x.x  # Replace with your Windows host IP
```

### Step 5.3: Configure Slack (Leave Empty For Now)

```bash
# Keep empty - will fill in later
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL=#pharmacy-alerts
```

### Step 5.4: Save and Verify

```bash
# Press Ctrl+X to exit nano
# Press Y to save
# Press Enter to confirm

# Verify .env exists
cat .env

# Should show all configuration variables
```

---

## 🎯 PHASE 6: Database Connection Test (10 minutes)

### Step 6.1: Install ODBC Driver for SQL Server

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update and install
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql17

# Verify
odbcinst -j

# Should show ODBC driver location
```

### Step 6.2: Test Database Connection

```bash
# With venv activated, run:
python tools/test_sql_connection.py

# Expected output:
# ✅ Successfully connected to SQL Server
# Database: stock
# Tables found: [list of tables]
```

**If connection fails:**
- Check SQL Server is running on Windows
- Verify SQL_SERVER IP in .env (use Windows host IP)
- Check SQL_USERNAME and SQL_PASSWORD are correct
- Verify ODBC driver is installed

---

## 🎯 PHASE 7: Run Tests (15 minutes)

### Step 7.1: Run Integration Tests

```bash
# Make sure venv is activated
source venv/bin/activate

# Run all tests
python test_slack_integration.py

# Should output:
# ✅ TEST 1: Module Imports — PASSED
# ✅ TEST 2: Template Generation — PASSED
# ✅ TEST 3: Block Structure — PASSED
# ✅ TEST 4: Message Content — PASSED
# ✅ TEST 5: Configuration — PASSED
# ✅ TEST 6: API Endpoints — PASSED
# ✅ TEST 7: File Structure — PASSED
# ✅ TEST 8: Documentation — PASSED
# 
# ✅ ALL TESTS PASSED
```

### Step 7.2: Check File Structure

```bash
# Verify all required files exist
ls -la tools/slack_*.py
ls -la architecture/slack_*.md
ls -la START_HERE.md PRODUCTION_GO_LIVE.md

# All should exist without errors
```

---

## 🎯 PHASE 8: Flask Application Setup (15 minutes)

### Step 8.1: Review Flask Configuration

```bash
# Check app.py exists and has Slack endpoints
grep -n "def api_slack" app.py

# Should show:
# 309: def api_slack_test():
# 322: def api_slack_daily_report():
# 350: def api_slack_expiry_alert():
# 374: def api_slack_low_stock_alert():
```

### Step 8.2: Test Flask Application

```bash
# Start Flask server
python app.py

# Output should show:
# * Running on http://127.0.0.1:5000
# * Press CTRL+C to quit
```

### Step 8.3: Test API Endpoints (in New Terminal)

**Open a new Ubuntu/WSL terminal:**

```bash
# Activate venv in new terminal
cd ~/projects/procare-dev/Procare--system
source venv/bin/activate

# Test connection endpoint
curl http://localhost:5000/api/slack/test

# Expected output:
# {"ok": false, "error": "SLACK_BOT_TOKEN not set"}
# This is OK - we haven't set the token yet

# Test health endpoint
curl http://localhost:5000/api/health

# Should return JSON with system status
```

### Step 8.4: Stop Flask Server

```bash
# In the Flask terminal, press CTRL+C to stop
```

---

## 🎯 PHASE 9: Slack Bot Setup (15 minutes)

### Step 9.1: Create Slack Bot

**On Windows browser (Windows 11 host):**

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "ProCare Pharmacy"
4. Select your workspace
5. Click "Create App"

### Step 9.2: Configure OAuth Scopes

1. Left sidebar: "OAuth & Permissions"
2. "Bot Token Scopes" section:
   - Click "Add an OAuth Scope"
   - Add: `chat:write`
   - Add: `chat:write.public`
3. Click "Install to Workspace"
4. Click "Allow"

### Step 9.3: Get Bot Token

1. From "OAuth & Permissions" page
2. Copy "Bot User OAuth Token" (starts with `xoxb-`)
3. **Keep this safe** - you'll need it next

### Step 9.4: Add Token to .env

**In WSL terminal:**

```bash
# Edit .env file
nano .env

# Find this line:
# SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Replace with your actual token:
# SLACK_BOT_TOKEN=xoxb-[paste-your-token-here]

# Save (Ctrl+X → Y → Enter)
```

### Step 9.5: Test Slack Connection

```bash
# Start Flask server
python app.py

# In new terminal, test Slack connection
curl http://localhost:5000/api/slack/test

# Expected output:
# {"ok": true, "user_id": "U...", "team_name": "Your Workspace"}
```

---

## 🎯 PHASE 10: Create Slack Channels (20 minutes)

### Step 10.1: Automated Channel Creation

**Use the Claude Code prompt:**

1. Open: `CLAUDE_CODE_SLACK_PROMPT.md`
2. Copy the complete prompt
3. Go to Claude Code (https://claude.ai/code)
4. Paste the prompt
5. Let Claude Code create all 15 channels

Or manually create these 15 channels in Slack:

```
CORE (1):
  #pharmacy-alerts

ROLE-BASED (4):
  #managers-dashboard
  #pharmacist-team
  #cashier-operations
  #admin-support

BRANCH-BASED (3):
  #elsanta-branch
  #mashala-branch
  #branch-comparison

OPERATIONS (3):
  #inventory-management
  #treasury-operations
  #compliance-audit

EMPLOYEE (4):
  #shift-schedule
  #training-development
  #announcements
  #general
```

### Step 10.2: Invite Bot to Channels

For each channel:
1. Go to channel
2. Click channel name → Members
3. Click "Add members"
4. Search for "@ProCare Pharmacy"
5. Add the bot

---

## 🎯 PHASE 11: Pharmacy Dashboard (15 minutes)

### Step 11.1: Access Dashboard

**On Windows browser (Windows 11 host):**

```
http://localhost:5000
```

Should show:
- ProCare Pharmacy Intelligence Dashboard
- Daily metrics
- Sales data
- Branch information

### Step 11.2: Test Dashboard Features

1. Check "Daily Report" section
2. Look for "Expiry Items"
3. Check "Branch Comparison"
4. Verify data loads from database

### Step 11.3: Verify API Endpoints

```bash
# Test each endpoint:

# 1. Health check
curl http://localhost:5000/api/health

# 2. Slack test
curl http://localhost:5000/api/slack/test

# 3. Daily report
curl -X POST http://localhost:5000/api/slack/daily-report \
  -H "Content-Type: application/json" \
  -d '{
    "branches": [{"name": "Elsanta", "total": 9000, "tx": 52}],
    "top_products": [{"name": "Paracetamol", "sales": 1500}],
    "expiry_items": [],
    "total_sales": 15000,
    "total_tx": 84,
    "report_date": "2026-06-06"
  }'
```

---

## 🎯 PHASE 12: Automated Sync Script (10 minutes)

### Step 12.1: Test Manual Sync

```bash
# With Flask running in one terminal, in another run:
python tools/hermes_slack_sync.py

# Expected output:
# Connecting to SQL Server...
# ✅ Connected to stock database
# Fetching yesterday's sales...
# Sending daily report to #managers-dashboard...
# ✅ Daily report sent successfully
```

### Step 12.2: Schedule Daily Automation

**Option A: Using cron (Linux/Ubuntu):**

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 7:00 AM):
0 7 * * * cd ~/projects/procare-dev/Procare--system && source venv/bin/activate && python tools/hermes_slack_sync.py >> logs/sync.log 2>&1

# Save (Ctrl+X → Y → Enter)

# Verify:
crontab -l
```

**Option B: Using Windows Task Scheduler (recommended):**

1. On Windows 11, open Task Scheduler
2. Create Basic Task:
   - Name: "ProCare Daily Sync"
   - Trigger: Daily at 7:00 AM
   - Action: Start Program
     - Program: `C:\Windows\System32\wsl.exe`
     - Arguments: `cd ~/projects/procare-dev/Procare--system && source venv/bin/activate && python tools/hermes_slack_sync.py`
     - Start in: (leave blank)

---

## 🎯 PHASE 13: Development Workflow (Ongoing)

### Step 13.1: Start Development Session

Every time you want to work:

```bash
# 1. Open Windows PowerShell or Terminal

# 2. Launch WSL
wsl

# 3. Navigate to project
cd ~/projects/procare-dev/Procare--system

# 4. Activate virtual environment
source venv/bin/activate

# 5. Start Flask server
python app.py

# 6. In new terminal, activate venv and run other commands
```

### Step 13.2: Access Services

**From Windows 11 browser:**

```
Dashboard:     http://localhost:5000
API:           http://localhost:5000/api/...
Slack:         https://app.slack.com
Health Check:  http://localhost:5000/api/health
```

### Step 13.3: Making Changes

```bash
# Edit files
nano app.py
nano tools/slack_client.py
# etc.

# Install new packages
pip install [package-name]

# Run tests
python test_slack_integration.py

# Commit changes
git add .
git commit -m "Description of changes"
git push origin claude/slack-session-3hNj0
```

---

## 🎯 PHASE 14: Troubleshooting

### Issue: WSL2 Ubuntu Can't Connect to Windows SQL Server

**Solution:**
```bash
# Get Windows host IP
cat /etc/resolv.conf | grep nameserver

# Update .env with this IP instead of "DESKTOP-3A9JFL4"
nano .env
# SQL_SERVER=172.x.x.x
```

### Issue: Port 5000 Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 [PID]

# Or use different port in app.py:
# app.run(port=5001)
```

### Issue: Python Modules Not Found

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: ODBC Driver Not Found

```bash
# Reinstall ODBC driver
sudo apt remove -y msodbcsql17
sudo ACCEPT_EULA=Y apt install -y msodbcsql17

# Verify
odbcinst -j
```

### Issue: Slack Bot Not Sending Messages

```bash
# Test bot token
curl http://localhost:5000/api/slack/test

# Should return:
# {"ok": true, ...}

# If false, check:
# 1. Token is correct in .env
# 2. Bot is invited to channels
# 3. Bot has chat:write permissions
```

---

## 📋 Quick Reference Commands

```bash
# WSL/Ubuntu
wsl                                    # Launch WSL from Windows
cd ~/projects/procare-dev/Procare--system  # Navigate to project
source venv/bin/activate              # Activate virtual environment
deactivate                             # Deactivate virtual environment

# Git
git status                             # Check changes
git add .                              # Stage changes
git commit -m "message"                # Commit
git push origin claude/slack-session-3hNj0  # Push

# Testing
python test_slack_integration.py       # Run all tests
python tools/test_sql_connection.py    # Test DB connection
python tools/hermes_slack_sync.py      # Run sync manually

# Flask
python app.py                          # Start server (http://localhost:5000)

# API Testing
curl http://localhost:5000/api/health  # Health check
curl http://localhost:5000/api/slack/test  # Slack test
```

---

## ✅ Verification Checklist

After completing all phases:

- [ ] Windows 11 + WSL2 installed
- [ ] Ubuntu Server running in WSL2
- [ ] Python 3.10+ installed
- [ ] Repository cloned
- [ ] Virtual environment created & activated
- [ ] Dependencies installed
- [ ] .env configured with SQL Server
- [ ] Database connection tested ✓
- [ ] All tests passing (8/8) ✓
- [ ] Flask server running ✓
- [ ] Dashboard accessible at http://localhost:5000 ✓
- [ ] Slack bot created
- [ ] Slack bot token added to .env
- [ ] 15 Slack channels created
- [ ] Bot invited to all channels
- [ ] Slack connection test passing ✓
- [ ] Manual sync test passing ✓
- [ ] Daily automation scheduled ✓

---

## 🎯 Next Steps

1. **Follow the 14 phases above** in order
2. **Test each phase** before moving to next
3. **Monitor logs** for errors
4. **Use troubleshooting section** if issues arise
5. **Commit your configuration** to git when complete

---

## 📚 Documentation Reference

For more details, see:

- **Setup Guide**: `architecture/slack_integration.md`
- **Channel Structure**: `architecture/slack_channels_setup.md`
- **User Workflows**: `architecture/dashboard_operations_guide.md`
- **Deployment**: `PRODUCTION_GO_LIVE.md`
- **Automation Prompt**: `CLAUDE_CODE_SLACK_PROMPT.md`
- **Quick Start**: `START_HERE.md`

---

**Status**: ✅ Complete Setup Guide  
**Total Time**: ~1-2 hours  
**Difficulty**: Intermediate  

🚀 **Ready to set up your development environment!**
