# 📊 ProCare Dashboard & Slack Operations Guide

> Complete workflow guide for pharmacy staff using the Hermes dashboard and Slack integration

---

## 👥 User Roles & Access

### Store Manager
**Dashboard Access**: Full read access, export reports
**Slack Channels**: 
- Primary: #managers-dashboard
- Secondary: #pharmacy-alerts, #branch-comparison, #treasury-operations

**Daily Responsibilities**:
1. 7:00 AM — Review daily report in #managers-dashboard
2. 9:00 AM — Check branch performance in #branch-comparison
3. Noon — Monitor cash reconciliation in #treasury-operations
4. 3:00 PM — Check inventory alerts in #pharmacy-alerts
5. 9:00 PM — Review end-of-day report in #managers-dashboard

### Pharmacist/Pharmacy Tech
**Dashboard Access**: Inventory, expiry, low stock views
**Slack Channels**:
- Primary: #pharmacist-team
- Secondary: #pharmacy-alerts, #inventory-management

**Daily Responsibilities**:
1. Morning — Check expiry items in dashboard & #pharmacy-alerts
2. Throughout day — Respond to low stock alerts
3. End of day — Verify removed/expired items documented
4. Escalate safety issues immediately to manager

### Cashier/POS Operator
**Dashboard Access**: Read-only sales data
**Slack Channels**:
- Primary: #cashier-operations
- Secondary: #pharmacy-alerts, #shift-schedule

**Daily Responsibilities**:
1. Shift start — Confirm attendance in #shift-schedule
2. Morning — Review cash opening checklist in #cashier-operations
3. Noon — Monitor till reconciliation alerts
4. End of shift — Complete cash close in #cashier-operations
5. Report issues immediately to supervisor

### Inventory Staff
**Dashboard Access**: Stock levels, purchases, movements
**Slack Channels**:
- Primary: #inventory-management
- Secondary: #pharmacy-alerts, #inventory-management

**Daily Responsibilities**:
1. Morning — Check dashboard for low stock items
2. Throughout day — Update stock movements
3. Process purchase orders from alerts
4. Verify received items against PO
5. Report discrepancies in #inventory-management

### Admin/Finance
**Dashboard Access**: Full read, treasury, compliance reports
**Slack Channels**:
- Primary: #admin-support, #treasury-operations
- Secondary: #pharmacy-alerts, #compliance-audit

**Daily Responsibilities**:
1. Morning — Check system status
2. Monitor database backups
3. Investigate cash/inventory discrepancies
4. Maintain audit trail in #compliance-audit
5. Generate compliance reports weekly

---

## 📱 Dashboard Overview

### Main Dashboard (Root Path: http://localhost:5000)

#### Sales Summary Panel
```
┌─────────────────────────────────┐
│ Today's Sales: EGP 12,500        │
│ Transactions: 42                 │
│ Yesterday: EGP 11,200 (↑12%)     │
│ Treasury: EGP 45,300             │
│ Expiry Alerts: 8                 │
└─────────────────────────────────┘
```

**What it shows**: Real-time sales metrics and system health
**Update frequency**: Real-time (as sales happen)
**Action**: Click to drill down into branch details

#### Branch Breakdown
```
┌─────────────────────────────────┐
│ Elsanta: EGP 7,500 (60%) 25 tx   │
│ Mashala: EGP 5,000  (40%) 17 tx  │
│ Performance: Elsanta +8%         │
└─────────────────────────────────┘
```

**What it shows**: Sales distribution by branch
**Update frequency**: Real-time
**Action**: Click to see branch-specific inventory

#### Treasury Status
```
┌─────────────────────────────────┐
│ Cash Depots:                      │
│ ├─ POS: EGP 2,100                │
│ ├─ Treasury: EGP 40,200          │
│ ├─ Bank Account: EGP 3,000       │
│ └─ TOTAL: EGP 45,300             │
│                                  │
│ Last Updated: 14:30              │
└─────────────────────────────────┘
```

**What it shows**: Real-time cash on hand by location
**Update frequency**: Hourly
**Action**: Click to see deposit history

---

## 🔔 Alert Management Workflow

### How Alerts Flow to You

```
Database Change Event
    ↓
Python Detection Script (hourly)
    ↓
Alert Threshold Check
    ├─ Expiry ≤ 7 days? → Alert
    ├─ Low Stock? → Alert
    └─ Discrepancy > 2%? → Alert
    ↓
Slack Message Posted
    ↓
Employee Notification
    ├─ Sound enabled by default
    ├─ Desktop notification
    └─ Mobile notification (if app installed)
    ↓
User Response
    ├─ Read alert
    ├─ Take action
    └─ Update status
    ↓
Task Logged
```

### Alert Response SLA

| Alert Type | Severity | Response Time | Action |
|-----------|----------|---------------|--------|
| Expiry Alert | Critical | 15 minutes | Pharmacist to verify and remove |
| Low Stock | High | 1 hour | Inventory to create PO |
| Cash Discrepancy | High | 1 hour | Manager to investigate |
| Compliance Alert | Medium | 4 hours | Admin to address |
| System Alert | Critical | 5 minutes | IT to acknowledge |

---

## 📊 Daily Report Analysis

### Morning Report (7:00 AM)
**Location**: #managers-dashboard
**Includes**:
- Yesterday's total sales + trend
- Sales by branch + performance rank
- Top 5 products by revenue
- Treasury balance
- Expiry items (next 60 days)
- Low stock items

**What to do**:
1. Compare to target KPIs
2. Note branch performance gaps
3. Check for critical alerts
4. Plan corrective actions

### Branch Performance Report
**Location**: #branch-comparison
**Includes**:
- Daily sales ranking
- Branch market share %
- Transaction count
- Discount analysis
- Trend (daily trend line)

**What to do**:
1. Identify underperforming branch
2. Investigate why (staffing, stock, promotions?)
3. Share best practices from top branch
4. Plan specific interventions

### End-of-Day Report (9:00 PM)
**Location**: #managers-dashboard
**Includes**:
- Final sales total + variance from target
- Complete branch breakdown
- Top/bottom products
- Cash reconciliation status
- Pending issues

**What to do**:
1. Verify cash reconciliation
2. Document any discrepancies
3. Flag items for next day action
4. Prepare briefing for next morning

---

## 💰 Cash Reconciliation Process

### Daily Cash Close Workflow

```
3:00 PM: First Count (Shift 1 → Shift 2)
  ├─ POS Manager counts till
  ├─ Reports in #cashier-operations
  └─ System flags any >2% variance

6:00 PM: Second Count (Shift 2 → Shift 3)
  ├─ Evening Manager counts till
  ├─ Reports in #cashier-operations
  └─ Compares to Shift 1 count

9:00 PM: Final Reconciliation
  ├─ Treasury staff counts all depots
  ├─ Compares to POS system total
  ├─ Reports in #treasury-operations
  └─ If variance >5%:
      ├─ Flag #managers-dashboard
      ├─ Assign to manager for investigation
      └─ Document root cause in #compliance-audit
```

### Expected Reconciliation Report
```
┌─────────────────────────────────────┐
│ CASH RECONCILIATION — 2026-06-04    │
├─────────────────────────────────────┤
│ Elsanta Branch                       │
│  POS Total:     EGP 7,500.00        │
│  Physical:      EGP 7,495.00        │
│  Variance:      EGP -5.00 (-0.07%)  │
│  Status:        ✅ BALANCED         │
├─────────────────────────────────────┤
│ Mashala Branch                       │
│  POS Total:     EGP 5,000.00        │
│  Physical:      EGP 5,015.00        │
│  Variance:      EGP +15.00 (+0.30%) │
│  Status:        ✅ BALANCED         │
├─────────────────────────────────────┤
│ TOTAL:          EGP 12,510.00       │
│ STATUS:         ✅ RECONCILED       │
│ SIGNED BY:      Ahmed (Manager)     │
│ TIME:           21:45:30            │
└─────────────────────────────────────┘
```

---

## 📦 Inventory Management Workflow

### Low Stock Alert Response

**Alert Format**:
```
🟠 Low Stock Alert
  Product: [NAME]
  Branch: [BRANCH]
  Current: [QTY] units
  Reorder Point: [REORDER_QTY] units
  Shortage: [DEFICIT] units below minimum
  Status: ⏳ Awaiting Reorder
```

**What to do**:
1. Click "Create Purchase Order" button
2. Enter supplier and quantity
3. Estimate delivery date
4. Submit PO
5. Update status in #inventory-management
6. Confirm receipt when items arrive
7. Update system stock levels

### Inventory Count Process

**Scheduled**: Monthly on the 15th at 8:00 AM

1. **Preparation** (7:00-8:00 AM):
   - Print current stock from dashboard
   - Divide inventory into zones
   - Assign staff to zones

2. **Count** (8:00 AM - 12:00 PM):
   - Count items in each zone
   - Record counts on forms
   - Use barcode scanner (if available)
   - Report discrepancies immediately

3. **Reconciliation** (12:00-1:00 PM):
   - Enter counts into system
   - Generate discrepancy report
   - Investigate variances >2%
   - Document root causes

4. **Reporting** (1:00 PM):
   - Post summary to #inventory-management
   - Update #compliance-audit with findings
   - Email full report to management

---

## 🚨 Critical Issue Escalation

### Expiry Alert — Immediate Action Required

**When**: Product expiring ≤7 days
**Alert**: Posted to #pharmacy-alerts + #pharmacist-team
**Response Required**: Within 15 minutes

**Steps**:
1. Pharmacist receives alert
2. Immediately verify physical location
3. Remove from shelves (if expiry ≤ 3 days)
4. Document removal:
   - Item name
   - Batch number
   - Quantity
   - Reason (expiry/damage/other)
   - Timestamp
5. Report completion in Slack thread
6. Schedule destruction/return with supplier

### Cash Discrepancy — Investigation Required

**When**: Variance > 5%
**Alert**: Posted to #treasury-operations + #managers-dashboard
**Response Required**: Within 1 hour

**Steps**:
1. Manager receives escalation
2. Investigate possible causes:
   - Till operator error
   - Unrecorded refunds
   - Damaged items
   - Till register malfunction
3. Interview cashiers
4. Review transaction logs
5. Document findings
6. Report in #managers-dashboard thread
7. File investigation in #compliance-audit

### System Down Alert

**When**: Database or API unreachable
**Alert**: Posted to #pharmacy-alerts + #admin-support
**Response Required**: Immediate (within 5 min)

**Steps**:
1. Admin receives alert
2. Check database connection
3. Check API logs
4. Try restart if applicable
5. Contact IT support if unresolved
6. Post status updates every 15 min
7. Document incident in #compliance-audit

---

## 📱 Mobile Access

### Slack Mobile App
- Download "Slack" from App Store or Google Play
- Log in with ProCare workspace
- Enable notifications for critical channels:
  - #pharmacy-alerts (All sounds)
  - #managers-dashboard (High priority only)
  - #shift-schedule (High priority + sound)

### Web Dashboard
- Access from any browser: http://localhost:5000
- Responsive design works on tablets and phones
- Offline access: Basic data cached locally
- Recommended: Bookmark on home screen

---

## 🎓 Quick Reference

### Daily Checklist for Store Manager
- [ ] 7:00 AM — Review daily report
- [ ] 9:00 AM — Check branch comparison
- [ ] 12:00 PM — Monitor alerts
- [ ] 3:00 PM — Verify inventory
- [ ] 6:00 PM — Review cash count
- [ ] 9:00 PM — Approve end-of-day report
- [ ] Respond to all escalations within SLA

### Weekly Tasks
- [ ] Monday 8:00 AM — Review weekly performance
- [ ] Wednesday — Check expiry items physically
- [ ] Friday — Plan next week's ordering
- [ ] Friday — Review compliance items

### Monthly Tasks
- [ ] 15th at 8:00 AM — Physical inventory count
- [ ] End of month — Prepare compliance report
- [ ] Generate sales analysis for month
- [ ] Staff performance review based on data

---

## 🔐 Security & Compliance

### Data Access Rules
- Only view data for your branch (except managers)
- Never share Slack messages with third parties
- Don't screenshot sensitive data
- Delete chat history per company policy

### Change Documentation
- All system changes logged in #compliance-audit
- User access changes recorded
- Manual data adjustments require approval
- Monthly audit of access logs

### Password Management
- Slack password: Use strong, unique password
- Never share login credentials
- Reset password every 90 days
- Report suspicious activity immediately

---

## 📞 Support & Help

### Getting Help
- **Dashboard Issue**: Message #admin-support
- **Slack Issue**: Message @slack-support
- **Pharmacy Question**: Post in #pharmacist-team
- **Urgent Issue**: Call store manager directly

### Feedback & Suggestions
- Suggest improvements in #general
- Vote on feature requests
- Request custom reports
- Report bugs with screenshots

---

*Last Updated: 2026-06-05*
*Version: 1.0*
