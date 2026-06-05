# 🏥 ProCare Pharmacy Intelligence System

> **READ-ONLY** intelligence layer on top of ProCare Stock v1.5.9.501
> Branches: **Elsanta (Main)** | **Mashala**

---

## 🎯 What This Does

Connects to the live ProCare Stock SQL Server database and delivers:
- 🔔 Real-time expiry & low-stock alerts → Slack
- 📊 Daily cash close reports → Slack
- 🏪 Branch comparison dashboard
- 🤖 Automated via Windows Task Scheduler

**CRITICAL:** This system is READ-ONLY. It NEVER writes to the ProCare database.

---

## 🏗️ Architecture (B.L.A.S.T. Protocol)

```
├── claude.md                       # Project Constitution (schemas, rules, invariants)
├── .env                            # ⚠️ Credentials — NEVER commit (see .gitignore)
├── .env.template                   # Safe template — copy to .env and fill in values
├── app.py                          # Flask API + Slack endpoints (UPDATED)
├── dashboard/                      # Web dashboard (HTML/CSS/JS)
├── architecture/                   # Layer 1: SOPs (Standard Operating Procedures)
│   ├── slack_integration.md        # 🔗 Hermes ↔ Slack technical setup
│   ├── slack_channels_setup.md     # 🎯 Channel architecture for pharmacy operations
│   ├── dashboard_operations_guide.md # 📊 Complete user workflow guide
│   ├── stock_alerts.md             # How expiry & low-stock logic works
│   └── daily_report.md             # How cash close is calculated
├── tools/                          # Layer 3: Deterministic Python scripts
│   ├── slack_client.py             # 🔗 SlackMessenger class for Slack communication
│   ├── slack_templates.py          # 🎨 Message template generator (NEW)
│   ├── hermes_slack_sync.py        # 🔗 Automated daily sync & alerts
│   ├── test_sql_connection.py      # Verify DB connection
│   ├── discover_schema.py          # Map all table/column names
│   ├── daily_report.py             # Daily cash close engine
│   └── treasury_report.py          # Treasury snapshot
├── task_plan.md                    # Phase checklist & timeline
├── findings.md                     # Research & discoveries
└── progress.md                     # Session log & error history
```

---

## ⚡ Quick Start

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Configure .env (add your SLACK_BOT_TOKEN)
copy .env.template .env
# Edit .env in your editor

# 3. Run the app
python app.py

# 4. In another terminal, test Slack
curl http://localhost:5000/api/slack/test

# 5. Send a daily report
python tools/hermes_slack_sync.py
```

For detailed setup, see **Setup** section below.

---

## ⚙️ Setup

### 1. Prerequisites
- Python 3.10+
- SQL Server ODBC Driver 17
- Access to ProCare Stock SQL Server (`DESKTOP-3A9JFL4`)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure credentials
```bash
copy .env.template .env
# Edit .env with your SQL Server and Slack credentials
# IMPORTANT: Get SLACK_BOT_TOKEN from https://api.slack.com/apps
```

### 4. Test database connection
```bash
python tools/test_sql_connection.py
```

### 5. Test Slack integration
```bash
python app.py
# In another terminal:
curl http://localhost:5000/api/slack/test
```

### 6. Run automated sync (pulls data → sends to Slack)
```bash
python tools/hermes_slack_sync.py
```

---

## 🚦 Current Status

| Phase | Status |
|-------|--------|
| 0 — Protocol | ✅ Complete |
| 1 — Blueprint | ✅ Complete |
| 2 — Link (Hermes ↔ Slack) | ✅ Complete |
| 3 — Architect (Channels & Operations) | ✅ Complete |
| 4 — Stylize (UI & Templates) | ✅ Complete |
| 5 — Trigger (Automation Rules) | 🟡 In Progress |

---

## ⚠️ Security Rules

1. **NEVER** commit `.env` — it contains SQL Server credentials
2. **NEVER** write to the ProCare database — READ ONLY
3. All intermediate files go to `.tmp/` (gitignored)
4. Run scripts as the pharmacy Windows user for Windows Auth to work

---

## 📞 Maintained by
Ahmed Ibrahim — ProCare Pharmacies (Elsanta & Mashala)
