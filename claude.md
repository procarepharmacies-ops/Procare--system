# 📜 claude.md — ProCare Pharmacy Intelligence System
## Project Constitution (Law File — Only Update When Schema/Rules Change)

---

## 🏥 Project Identity
- **Client:** Ahmed Ibrahim — Pharmacist & Business Developer
- **System:** ProCare Stock v1.5.9.501 (E-Stock SQL Server backend)
- **Branches:** Elsanta (Main) | Mashala
- **Database:** SQL Server | DB Name: `stock` | Server: `DESKTOP-3A9JFL4`
- **Auth:** Windows Authentication
- **Project Folder:** `D:\procare-pharmacy`
- **GitHub Repo:** `https://github.com/procarepharmacies-ops/Procare--system.git`

---

## 🎯 North Star
Connect to the live ProCare Stock SQL Server database and deliver:
1. Real-time stock alerts (expiry, low stock)
2. Daily cash close reports
3. Branch comparison dashboard
4. Slack notifications for critical events

---

## 📊 Data Schema

### Input: ProCare Stock SQL Tables (Known)
```
Products        → SKU, Name, Category, CostPrice, PharmacyPrice, SellPrice, ExpiryDate
Sales_header    → SaleID, BranchID, Date, Total, PaymentType
Sales_detail    → SaleID, ProductID, Qty, Price
Purchase_header → PurchaseID, SupplierID, BranchID, Date, Total
Purchase_detail → PurchaseID, ProductID, Qty, CostPrice
Suppliers       → SupplierID, Name, Phone
Branches        → BranchID, Name
```

### Output: Payload Shapes
```json
// Stock Alert
{
  "alert_type": "EXPIRY|LOW_STOCK",
  "branch": "Elsanta|Mashala",
  "product_name": "string",
  "days_to_expiry": 45,
  "qty_on_hand": 12,
  "reorder_point": 10
}

// Daily Cash Close
{
  "branch": "string",
  "date": "YYYY-MM-DD",
  "total_sales": 0.00,
  "transaction_count": 0,
  "top_product": "string"
}
```

---

## 🚦 Behavioral Rules
1. NEVER write to the ProCare database — READ ONLY
2. All intermediate data goes to `.tmp/`
3. Slack alerts fire only when thresholds are crossed
4. Arabic + English in all output messages
5. `.env` holds ALL credentials — never hardcode
6. Self-heal: on any tool failure → log → fix → update architecture SOP

---

## 🔑 Environment Variables (.env)
```
SQL_SERVER=DESKTOP-3A9JFL4
SQL_DATABASE=stock
SQL_DRIVER={ODBC Driver 17 for SQL Server}
SLACK_BOT_TOKEN=[from Slack]
SLACK_CHANNEL=C0AP0NL9BE3
ALERT_EXPIRY_DAYS=60
BRANCH_MAIN=Elsanta
BRANCH_SECOND=Mashala
```

---

## 🏗️ Architecture Invariants
- Layer 1: `architecture/` = SOPs in Markdown
- Layer 2: Navigation = Claude reasoning layer
- Layer 3: `tools/` = Deterministic Python scripts only
- `.tmp/` = All temp files, logs, intermediate outputs
- Cloud payload = Slack channel + future Google Sheets

---
*Last updated: 2026-04-14 | Version: 1.0*
