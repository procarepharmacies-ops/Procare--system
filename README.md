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
├── claude.md              # Project Constitution (schemas, rules, invariants)
├── .env                   # ⚠️ Credentials — NEVER commit (see .gitignore)
├── .env.template          # Safe template — copy to .env and fill in values
├── architecture/          # Layer 1: SOPs (Standard Operating Procedures)
│   ├── stock_alerts.md    # How expiry & low-stock logic works
│   └── daily_report.md   # How cash close is calculated
├── tools/                 # Layer 3: Deterministic Python scripts
│   ├── test_sql_connection.py   # Phase 2: Verify DB connection
│   ├── discover_schema.py       # Phase 2: Map all table/column names
│   ├── stock_alerts.py          # Phase 3: Expiry & low stock engine
│   ├── daily_report.py          # Phase 3: Daily cash close engine
│   └── slack_sender.py          # Phase 3: Slack delivery engine
├── task_plan.md           # Phase checklist & timeline
├── findings.md            # Research & discoveries
└── progress.md            # Session log & error history
```

---

## ⚙️ Setup

### 1. Prerequisites
- Python 3.10+
- SQL Server ODBC Driver 17
- Access to ProCare Stock SQL Server (`DESKTOP-3A9JFL4`)

### 2. Install dependencies
```bash
pip install pyodbc pandas python-dotenv slack-sdk
```

### 3. Configure credentials
```bash
copy .env.template .env
# Edit .env with your actual SQL Server and Slack credentials
```

### 4. Test connection
```bash
python tools/test_sql_connection.py
```

---

## 🚦 Current Status

| Phase | Status |
|-------|--------|
| 0 — Protocol | ✅ Complete |
| 1 — Blueprint | ✅ Complete |
| 2 — Link | 🟡 In Progress |
| 3 — Architect | 🔴 Pending |
| 4 — Stylize | 🔴 Pending |
| 5 — Trigger | 🔴 Pending |

---

## ⚠️ Security Rules

1. **NEVER** commit `.env` — it contains SQL Server credentials
2. **NEVER** write to the ProCare database — READ ONLY
3. All intermediate files go to `.tmp/` (gitignored)
4. Run scripts as the pharmacy Windows user for Windows Auth to work

---

## 📞 Maintained by
Ahmed Ibrahim — ProCare Pharmacies (Elsanta & Mashala)
