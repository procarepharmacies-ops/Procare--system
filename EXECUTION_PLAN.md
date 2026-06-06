# 🚀 SLACK INTEGRATION EXECUTION PLAN

**Location**: Clone/pull this repository to your RedHat local machine
**Status**: Ready to execute immediately
**Time Required**: 30 minutes to full deployment

---

## PHASE 1: ENVIRONMENT SETUP (5 minutes)

### Step 1.1: Clone/Update Repository
```bash
# If you don't have it yet:
git clone https://github.com/procarepharmacies-ops/Procare--system.git
cd Procare--system

# If you already have it:
cd /path/to/Procare--system
git pull origin main
```

### Step 1.2: Verify Branch
```bash
git branch -a
# Should show: main (latest merged code)
```

### Step 1.3: Check Python Version
```bash
python3 --version
# Need: Python 3.8+
```

---

## PHASE 2: INSTALL DEPENDENCIES (5 minutes)

### Step 2.1: Install Requirements
```bash
pip3 install -r requirements.txt
```

**What gets installed:**
- flask==3.0.0
- flask-cors==4.0.0
- pyodbc==5.1.0
- slack-sdk==3.27.1
- python-dotenv==1.0.0

### Step 2.2: Verify Installation
```bash
python3 -c "import slack_sdk; print('✅ Slack SDK installed')"
python3 -c "import pyodbc; print('✅ ODBC driver loaded')"
python3 -c "import flask; print('✅ Flask installed')"
```

---

## PHASE 3: CONFIGURE SLACK BOT (5 minutes)

### Step 3.1: Create Slack Bot
**Website**: https://api.slack.com/apps

1. Click "Create New App"
2. Select "From scratch"
3. **App Name**: ProCare Pharmacy
4. **Workspace**: Select your workspace
5. Click "Create App"

### Step 3.2: Add OAuth Scopes
1. Left menu → "OAuth & Permissions"
2. Under "Bot Token Scopes", add:
   - `chat:write`
   - `chat:write.public`
3. Click "Install to Workspace" → "Allow"

### Step 3.3: Copy Bot Token
1. From "OAuth & Permissions" page
2. Copy "Bot User OAuth Token" (starts with `xoxb-`)
3. Save it

### Step 3.4: Configure .env File
```bash
cd /path/to/Procare--system
nano .env
```

**Add this line:**
```
SLACK_BOT_TOKEN=xoxb-[paste-your-token-here]
```

Save file (Ctrl+O, Enter, Ctrl+X)

### Step 3.5: Verify Configuration
```bash
grep SLACK_BOT_TOKEN .env
# Should show: SLACK_BOT_TOKEN=xoxb-...
```

---

## PHASE 4: CREATE SLACK CHANNELS (5 minutes)

Create these channels in your Slack workspace:

**Core Channel:**
- #pharmacy-alerts

**Role-Based (4):**
- #managers-dashboard
- #pharmacist-team
- #cashier-operations
- #admin-support

**Branch-Based (3):**
- #elsanta-branch
- #mashala-branch
- #branch-comparison

**Operations (3):**
- #inventory-management
- #treasury-operations
- #compliance-audit

**Employee (3+):**
- #shift-schedule
- #training-development
- #announcements

**For each channel:**
1. In Slack workspace → "+" button
2. Create channel with exact name above
3. In channel settings → "Add apps to this channel"
4. Search for "ProCare Pharmacy" bot
5. Add bot to channel

---

## PHASE 5: TEST INTEGRATION (5 minutes)

### Test 5.1: Run Test Suite
```bash
python3 test_slack_integration.py
```

**Should see:**
- ✅ Module Imports
- ✅ Template Generation (9/9)
- ✅ Block Structure Validation
- ✅ Message Content Validation
- ✅ Configuration Validation
- ✅ File Structure Verification
- ✅ Documentation Quality

### Test 5.2: Test Slack Connection
```bash
python3 tools/hermes_slack_sync.py
```

**Should see:**
```
✅ Connected to Slack
Generating daily report...
  Total Sales: EGP ...
  Transactions: ...
  ✅ Daily report sent to Slack
✅ No urgent expiries
SYNC COMPLETE
```

### Test 5.3: Check Slack Message
1. Go to Slack workspace
2. Open #managers-dashboard
3. Should see message like:
```
📊 PROCARE DAILY REPORT
Date: [date]
Total Sales: EGP ...
```

---

## PHASE 6: START FLASK API (2 minutes)

### Step 6.1: Start Flask Server
```bash
python3 app.py
```

**Should see:**
```
======================================================
  ProCare Pharmacy Intelligence API
  http://localhost:5000
  Press Ctrl+C to stop
======================================================
```

### Step 6.2: Test API Endpoints (in another terminal)
```bash
# Test Slack endpoint
curl http://localhost:5000/api/slack/test

# Test health check
curl http://localhost:5000/api/health

# Test summary
curl http://localhost:5000/api/summary
```

---

## PHASE 7: SCHEDULE AUTOMATION (3 minutes)

### For Linux/RedHat with Cron:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 7:00 AM):
0 7 * * * cd /path/to/Procare--system && python3 tools/hermes_slack_sync.py >> /var/log/procare_slack.log 2>&1
```

### Verify cron job:
```bash
crontab -l
# Should show your job
```

---

## PHASE 8: MONITOR & VERIFY (Ongoing)

### Check Daily Logs
```bash
tail -f /var/log/procare_slack.log
```

### Monitor Slack Messages
- Check #managers-dashboard at 7:00 AM
- Should see daily sales report
- Check other channels for alerts

### Verify Database Connection
```bash
python3 tools/test_sql_connection.py
```

---

## 📊 EXPECTED RESULTS

### After Deployment:

**Day 1:**
- ✅ Slack bot online
- ✅ API endpoints responding
- ✅ First daily report at 7 AM
- ✅ All channels populated

**Week 1:**
- ✅ Daily reports arriving on schedule
- ✅ Expiry alerts triggering
- ✅ Low stock alerts appearing
- ✅ Cash reconciliation working
- ✅ Staff responding to alerts

**Month 1:**
- ✅ Full pharmacy team using Slack
- ✅ Real-time alert response
- ✅ Data-driven decisions
- ✅ Streamlined operations

---

## 🔧 TROUBLESHOOTING

### Problem: "pyodbc.Error: ODBC driver not found"
**Solution:**
```bash
# Install ODBC driver for SQL Server
sudo yum install unixODBC-devel
# Or on Ubuntu:
sudo apt-get install unixodbc-dev
```

### Problem: "SLACK_BOT_TOKEN not set"
**Solution:**
```bash
# Verify .env file
cat .env | grep SLACK_BOT_TOKEN
# Should show: SLACK_BOT_TOKEN=xoxb-...
```

### Problem: "Slack message not appearing"
**Solution:**
1. Check bot is in channel: `/invite @ProCare`
2. Check token is valid at https://api.slack.com/apps
3. Check scope permissions (chat:write added)
4. Run test: `python3 tools/hermes_slack_sync.py`

### Problem: "Cannot connect to database"
**Solution:**
```bash
# Test connection
python3 tools/test_sql_connection.py
# Should show: ✅ Connected to ProCare database
```

---

## 📝 QUICK REFERENCE COMMANDS

```bash
# Install deps
pip3 install -r requirements.txt

# Test everything
python3 test_slack_integration.py

# Run sync manually
python3 tools/hermes_slack_sync.py

# Start Flask API
python3 app.py

# Check cron jobs
crontab -l

# View logs
tail -f /var/log/procare_slack.log

# Test Slack endpoint
curl http://localhost:5000/api/slack/test

# Check configuration
grep SLACK_BOT_TOKEN .env
```

---

## 📋 CHECKLIST

- [ ] Repository cloned/pulled
- [ ] Python 3.8+ verified
- [ ] Dependencies installed (pip3 install -r requirements.txt)
- [ ] Slack bot created at api.slack.com/apps
- [ ] OAuth scopes added (chat:write, chat:write.public)
- [ ] Bot token copied to .env (SLACK_BOT_TOKEN)
- [ ] Slack channels created (15+ channels)
- [ ] Bot invited to all channels
- [ ] Test suite runs: `python3 test_slack_integration.py`
- [ ] Sync script runs: `python3 tools/hermes_slack_sync.py`
- [ ] Message appears in #managers-dashboard
- [ ] Flask API starts: `python3 app.py`
- [ ] API endpoints respond: `curl http://localhost:5000/api/slack/test`
- [ ] Cron job added: `crontab -e`
- [ ] Daily log file set up: `/var/log/procare_slack.log`

---

## 🎯 GO LIVE CHECKLIST

Once all above is working:

- [ ] All team channels created and configured
- [ ] Bot permissions verified
- [ ] Database connection tested
- [ ] First daily report received at 7 AM
- [ ] Staff trained on channel usage
- [ ] Escalation procedures communicated
- [ ] Monitoring set up
- [ ] Support contact documented

---

## 📞 SUPPORT

**Code Issues:**
- See: `architecture/slack_integration.md`

**User Questions:**
- See: `architecture/dashboard_operations_guide.md`

**Channel Setup:**
- See: `architecture/slack_channels_setup.md`

**Deployment Help:**
- See: `DEPLOYMENT_READY.md`

---

**Status: ✅ READY TO EXECUTE**

All code is in repository main branch.
Ready to deploy on your RedHat local machine.

Execute the plan above to go live!

