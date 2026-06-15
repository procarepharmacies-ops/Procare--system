# 🔗 Hermes ↔ Slack Integration

> Link ProCare Pharmacy Intelligence System (Hermes) with Slack for real-time alerts and daily reports

---

## 📋 Overview

The Hermes-Slack integration connects your ProCare pharmacy data directly to Slack, enabling:

- 📊 **Daily Reports** — Sales, branch comparison, top products, expiry alerts
- 🚨 **Urgent Alerts** — Products expiring in next 7 days
- 🟠 **Low Stock Alerts** — When inventory drops below reorder point
- 🔔 **Real-time Notifications** — Via Flask API endpoints

---

## 🚀 Setup (5 Steps)

### Step 1: Create a Slack Bot

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App name: `ProCare Pharmacy`
4. Select your workspace
5. Click "Create App"

### Step 2: Configure Bot Permissions

1. In the left menu, click "OAuth & Permissions"
2. Under "Scopes" → "Bot Token Scopes", add:
   - `chat:write` — Send messages
   - `chat:write.public` — Send messages to public channels
3. Click "Install to Workspace" → "Allow"

### Step 3: Copy Bot Token

1. From "OAuth & Permissions" page, copy the **Bot User OAuth Token**
2. It starts with `xoxb-`

### Step 4: Configure Environment

1. Open `.env` in the repository root
2. Paste your bot token:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_CHANNEL=#pharmacy-alerts
   ```
3. Save the file

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `slack-sdk` and other dependencies.

---

## 📡 API Endpoints

The Flask API exposes these Slack endpoints:

### Test Slack Connection
```
GET /api/slack/test
Response: { "status": "ok", "message": "Test message sent to Slack" }
```

### Send Daily Report
```
POST /api/slack/daily-report
Body: {
  "branches": [{"name": "Elsanta", "tx": 42, "total": 5000.00}],
  "top_products": [{"name": "Paracetamol", "qty": 15, "revenue": 450.00}],
  "expiry_items": [{"name": "Aspirin", "qty": 5, "exp_date": "2026-07-15", "days_left": 40}],
  "total_sales": 10500.00,
  "total_tx": 84,
  "report_date": "2026-06-04"
}
Response: { "status": "ok", "message": "Daily report sent to Slack" }
```

### Send Expiry Alert
```
POST /api/slack/expiry-alert
Body: {
  "product_name": "Aspirin 500mg",
  "days_left": 5,
  "qty": 12,
  "exp_date": "2026-06-10"
}
Response: { "status": "ok", "message": "Expiry alert sent to Slack" }
```

### Send Low Stock Alert
```
POST /api/slack/low-stock-alert
Body: {
  "product_name": "Ibuprofen 200mg",
  "current_qty": 3,
  "reorder_point": 10,
  "branch": "Elsanta"
}
Response: { "status": "ok", "message": "Low stock alert sent to Slack" }
```

---

## 🤖 Automated Sync Script

Run the sync script to pull data and send reports automatically:

```bash
python tools/hermes_slack_sync.py
```

This script:
1. ✅ Tests Slack connection
2. 📊 Fetches yesterday's sales data
3. 📤 Sends daily report to Slack
4. 🚨 Sends urgent expiry alerts (≤ 7 days)

### Schedule with Windows Task Scheduler

To run automatically every morning:

1. Open "Task Scheduler"
2. Create Basic Task:
   - **Name:** ProCare Daily Slack Report
   - **Trigger:** Daily at 7:00 AM
   - **Action:** Start a program
     - Program: `python`
     - Arguments: `C:\path\to\tools\hermes_slack_sync.py`
     - Start in: `C:\path\to\Procare--system`
3. Click OK

---

## 🏗️ Architecture

```
Hermes (ProCare Database)
    ↓
SQL Server (DESKTOP-3A9JFL4)
    ↓
Python Layer
    ├── app.py (Flask API)
    ├── tools/slack_client.py (Slack SDK wrapper)
    └── tools/hermes_slack_sync.py (Automated sync)
    ↓
Slack API
    ↓
#pharmacy-alerts Channel
```

### Code Flow

1. **slack_client.py** — SlackMessenger class handles all Slack communication
2. **app.py** — Flask endpoints expose Slack integration via HTTP
3. **hermes_slack_sync.py** — Automated script pulls data and sends alerts
4. **.env** — Stores credentials (NEVER commit this file)

---

## 🔐 Security Rules

1. **NEVER** commit `.env` — It contains your bot token
2. **NEVER** paste bot tokens in code — Use environment variables only
3. **READ-ONLY** — This system never writes to the database
4. Use `Trusted_Connection=yes` for Windows Authentication (no passwords in logs)

---

## 🧪 Testing

### Test 1: Flask API Running
```bash
python app.py
# Then in another terminal:
curl http://localhost:5000/api/health
```

### Test 2: Slack Connection
```bash
curl http://localhost:5000/api/slack/test
# Check #pharmacy-alerts channel for test message
```

### Test 3: Direct Script Test
```bash
python tools/hermes_slack_sync.py
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `SLACK_BOT_TOKEN not set` | Add `SLACK_BOT_TOKEN=xoxb-...` to `.env` |
| `invalid_auth` error | Verify bot token is correct and not expired |
| `channel_not_found` | Ensure channel exists and bot is invited to it |
| `not_in_channel` | Go to channel → Add bot to workspace |
| `ratelimit` error | Slack API rate limit hit — wait a minute and retry |

### Check Logs

```bash
# On Windows, check Event Viewer for Task Scheduler errors
# In Python, errors are printed to console/log file
```

---

## 📊 Message Formats

### Daily Report
- Header: "📊 ProCare Daily Report"
- Sections: Sales summary, branch breakdown, top products, expiry alerts
- Color-coded by urgency

### Expiry Alert
- 🔴 URGENT (≤ 7 days)
- 🟡 WARNING (8-60 days)
- Shows product name, expiry date, days left, quantity

### Low Stock Alert
- 🟠 Warning icon
- Shows product, current qty, reorder point, branch

---

## 📚 Related Files

- `claude.md` — Project constitution and rules
- `app.py` — Main Flask API (updated with Slack endpoints)
- `tools/slack_client.py` — Slack SDK wrapper (NEW)
- `tools/hermes_slack_sync.py` — Automated sync script (NEW)
- `.env` — Environment variables (updated)
- `.env.template` — Configuration template (NEW)
- `requirements.txt` — Python dependencies (updated)

---

*Last updated: 2026-06-05*
