# 🤖 Claude Code Prompt - ProCare Slack Channel Automation

## Use This Prompt in Claude Code to Auto-Create Channels

Copy and paste this prompt into Claude Code or Slack integration to automatically create all ProCare pharmacy channels:

---

## **PROMPT: Create ProCare Pharmacy Slack Channels**

```
You are the ProCare Pharmacy Slack Channel Generator. Your task is to create 
ALL Slack channels for the ProCare Pharmacy Intelligence System.

CHANNELS TO CREATE (15 total):

CORE ALERT CHANNEL:
  1. #pharmacy-alerts
     Purpose: Critical pharmacy alerts only (expiry, low stock, compliance)
     Type: Public
     Topic: "Critical pharmacy alerts - expiry items, low stock, compliance issues"

ROLE-BASED CHANNELS (4):
  2. #managers-dashboard
     Purpose: Management oversight and reporting
     Type: Public
     Topic: "Manager dashboards - daily reports, KPIs, branch performance"
  
  3. #pharmacist-team
     Purpose: Medication safety and compliance
     Type: Public
     Topic: "Pharmacist communications - medication safety, compliance, audits"
  
  4. #cashier-operations
     Purpose: POS and cash handling
     Type: Public
     Topic: "Cashier operations - POS transactions, cash reconciliation"
  
  5. #admin-support
     Purpose: System and infrastructure
     Type: Public
     Topic: "Admin and support - system status, infrastructure, backups"

BRANCH-BASED CHANNELS (3):
  6. #elsanta-branch
     Purpose: Elsanta location operations
     Type: Public
     Topic: "Elsanta branch - daily operations, local alerts, staff updates"
  
  7. #mashala-branch
     Purpose: Mashala location operations
     Type: Public
     Topic: "Mashala branch - daily operations, local alerts, staff updates"
  
  8. #branch-comparison
     Purpose: Inter-branch performance analysis
     Type: Public
     Topic: "Branch comparison - performance metrics, competitive analysis"

OPERATIONS CHANNELS (3):
  9. #inventory-management
     Purpose: Stock management and ordering
     Type: Public
     Topic: "Inventory management - stock levels, reorders, discrepancies"
  
  10. #treasury-operations
      Purpose: Cash management and reconciliation
      Type: Public
      Topic: "Treasury operations - cash close, reconciliation, variances"
  
  11. #compliance-audit
      Purpose: Audit trail and compliance
      Type: Public
      Topic: "Compliance and audit - regulatory requirements, audit logs"

EMPLOYEE COORDINATION CHANNELS (4):
  12. #shift-schedule
      Purpose: Daily shift assignments
      Type: Public
      Topic: "Shift schedule - daily assignments, time-off requests"
  
  13. #training-development
      Purpose: Staff training and development
      Type: Public
      Topic: "Training and development - courses, skills, certifications"
  
  14. #announcements
      Purpose: Company-wide announcements
      Type: Public
      Topic: "Announcements - company news, policy updates, celebrations"
  
  15. #general
      Purpose: Social interaction
      Type: Public
      Topic: "General discussion - casual chat, watercooler conversation"

INSTRUCTIONS:
1. Create each channel in the order listed above
2. Set the channel topic and description as specified
3. Add the ProCare bot (@ProCare Pharmacy) to ALL channels
4. Set channel visibility to PUBLIC (searchable)
5. After all channels created, respond with a summary table showing:
   - Channel name
   - Purpose
   - Creation status (✅ Created or ❌ Failed)
   - Bot status (✅ Invited or ❌ Not invited)

VERIFICATION:
After creation, test by:
  1. Run: curl http://localhost:5000/api/slack/test
  2. Send test message to #pharmacy-alerts
  3. Verify bot appears in all channels
  4. Check that messages format correctly

COMPLETION:
When all channels are created and bot is invited to each:
  1. Respond with creation summary
  2. Confirm all tests pass
  3. Provide: "✅ SLACK CHANNELS READY FOR PRODUCTION"
```

---

## How to Use This Prompt

### **Option 1: Direct to Claude Code**
```bash
# Copy the prompt above and paste into Claude Code:
/help
# Then provide the full prompt to create the channels
```

### **Option 2: Via Slack Bot Commands**
```
In Slack, message @ProCare Pharmacy:
  "Create all ProCare pharmacy channels"
  
Or provide the prompt text directly.
```

### **Option 3: Programmatic (Python)**
```python
from tools.slack_client import SlackMessenger

messenger = SlackMessenger()

channels_to_create = [
    {
        "name": "pharmacy-alerts",
        "topic": "Critical pharmacy alerts - expiry items, low stock, compliance issues",
        "purpose": "Critical alerts only"
    },
    {
        "name": "managers-dashboard",
        "topic": "Manager dashboards - daily reports, KPIs, branch performance",
        "purpose": "Management oversight"
    },
    # ... all 15 channels
]

for channel_config in channels_to_create:
    # Use Slack API to create channels
    # messenger.client.conversations_create(**channel_config)
    pass
```

---

## After Channels Are Created

### Step 1: Verify All Channels Exist
```bash
curl http://localhost:5000/api/slack/test
```

Expected response:
```json
{
  "ok": true,
  "user_id": "U...",
  "user_name": "ProCare Pharmacy Bot",
  "team_id": "T...",
  "team_name": "Your Workspace"
}
```

### Step 2: Test Message Sending
```bash
python tools/hermes_slack_sync.py
```

Should send:
- ✅ Daily report to #managers-dashboard
- ✅ Expiry alerts to #pharmacy-alerts
- ✅ Low stock alerts to #inventory-management

### Step 3: Verify Bot Permissions
Bot should have:
- ✅ chat:write scope
- ✅ chat:write.public scope
- ✅ Invited to all 15 channels
- ✅ Can post messages

### Step 4: Test Each Channel Type

**Core Channel Test:**
```bash
curl -X POST http://localhost:5000/api/slack/test \
  -H "Content-Type: application/json" \
  -d '{"channel": "#pharmacy-alerts"}'
```

**Daily Report Test:**
```bash
curl -X POST http://localhost:5000/api/slack/daily-report \
  -H "Content-Type: application/json" \
  -d '{
    "branches": [{"name": "Elsanta", "total": 9000, "tx": 52}],
    "top_products": [{"name": "Paracetamol", "sales": 1500}],
    "expiry_items": [{"name": "Aspirin", "days_left": 5}],
    "total_sales": 15000,
    "total_tx": 84,
    "report_date": "2026-06-06"
  }'
```

---

## Production Deployment Checklist

After channels are created and tested:

### Pre-Production Verification
- [ ] All 15 channels created
- [ ] Bot invited to all channels
- [ ] Bot has chat:write permissions
- [ ] Test messages send successfully
- [ ] Daily sync script runs without errors
- [ ] API endpoints all respond correctly
- [ ] .env has valid SLACK_BOT_TOKEN

### Production Readiness
- [ ] All tests pass (run: python test_slack_integration.py)
- [ ] Documentation reviewed
- [ ] Team trained on channels
- [ ] Escalation paths verified
- [ ] Emergency contact numbers posted in #admin-support
- [ ] Daily backup scheduled
- [ ] Monitoring alerts configured

### Go-Live Steps
1. **Confirm all channels created:** ✅
2. **Confirm bot permissions:** ✅
3. **Confirm test messages send:** ✅
4. **Enable daily scheduling:**
   ```bash
   # Windows Task Scheduler:
   # Task: "ProCare Daily Slack Report"
   # Trigger: Daily at 7:00 AM
   # Action: python C:\path\to\tools\hermes_slack_sync.py
   ```

5. **Monitor first 24 hours:**
   - [ ] First daily report arrives at 7:00 AM
   - [ ] Expiry alerts fire correctly
   - [ ] Low stock alerts appear
   - [ ] No errors in logs
   - [ ] Team can access channels

6. **Production Status:** 🚀 LIVE

---

## Troubleshooting During Setup

| Issue | Solution |
|-------|----------|
| Channel already exists | Use existing channel, skip creation |
| Bot can't be invited | Check bot token, verify in Slack workspace |
| Messages not sending | Verify SLACK_BOT_TOKEN in .env |
| Rate limiting | Wait 60 seconds, then retry |
| Topic not updating | Check channel permissions in Slack |

---

## Final Confirmation

Once channels are created, send this confirmation to confirm production readiness:

```
✅ PROCARE SLACK INTEGRATION - PRODUCTION READY

Channels Created: 15/15 ✅
Bot Invited: 15/15 ✅
Tests Passing: 8/8 ✅
Documentation: Complete ✅

🚀 READY FOR PRODUCTION DEPLOYMENT
```

---

**Status**: Ready to Deploy
**Date**: 2026-06-06
**Version**: 1.0
