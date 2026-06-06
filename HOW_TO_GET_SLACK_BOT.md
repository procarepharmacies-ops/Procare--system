# 🤖 How to Get Slack Bot Token

**Complete Guide to Creating and Configuring ProCare Pharmacy Slack Bot**

---

## ⚡ Quick Summary

1. **Go to**: https://api.slack.com/apps
2. **Create**: New app "ProCare Pharmacy"
3. **Add Scopes**: `chat:write`, `chat:write.public`
4. **Copy Token**: `Bot User OAuth Token` (starts with `xoxb-`)
5. **Save**: Add to `.env` file as `SLACK_BOT_TOKEN=xoxb-...`
6. **Invite Bot**: Add to all Slack channels

---

## Step 1: Visit Slack API Website

**Website**: https://api.slack.com/apps

- Open the link in your browser
- Log in with your Slack account
- Make sure you're in the correct workspace

---

## Step 2: Create New App

1. Click **"Create New App"** button (green button at top)
2. Select **"From scratch"**
3. Fill in the form:
   - **App Name**: `ProCare Pharmacy`
   - **Workspace**: Select your workspace from dropdown
4. Click **"Create App"**

---

## Step 3: Add Bot Permissions (OAuth Scopes)

1. In the **left menu**, click **"OAuth & Permissions"**

2. Scroll down to **"Scopes"** section

3. Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"**

4. Add these **two scopes**:
   - `chat:write` — Allows bot to send messages
   - `chat:write.public` — Allows bot to write in public channels

5. After adding scopes, you'll see an **"Install to Workspace"** button

6. Click it and authorize the app

---

## Step 4: Get Your Bot Token

1. You're still on **"OAuth & Permissions"** page

2. Look at the **TOP** of the page for **"Bot User OAuth Token"**

3. It looks like a long string starting with `xoxb-`

4. Click **"Copy"** button next to it

5. Save it somewhere safe (you'll need it next)

---

## Step 5: Save Token to .env File

On your **RedHat local machine**:

```bash
# Navigate to repository
cd /path/to/Procare--system

# Open .env file
nano .env

# Find this line:
SLACK_BOT_TOKEN=

# Paste your token after equals sign (no spaces):
SLACK_BOT_TOKEN=[your-token-starting-with-xoxb]

# Save file (Ctrl+O, Enter, Ctrl+X)

# Verify it was saved:
cat .env | grep SLACK_BOT_TOKEN
```

**Should output:**
```
SLACK_BOT_TOKEN=xoxb-... (your actual token)
```

---

## Step 6: Invite Bot to Slack Channels

For **each channel** you created, invite the bot:

1. Open the channel in Slack
2. Click the **channel name** at the top
3. Go to **"Integrations"** or **"Apps"** tab
4. Click **"Add an app"**
5. Search for **"ProCare Pharmacy"**
6. Click **"Add"**

**Channels to add bot to:**

**Core:**
- #pharmacy-alerts

**Role-Based:**
- #managers-dashboard
- #pharmacist-team
- #cashier-operations
- #admin-support

**Branch-Based:**
- #elsanta-branch
- #mashala-branch
- #branch-comparison

**Operations:**
- #inventory-management
- #treasury-operations
- #compliance-audit

**Employee:**
- #shift-schedule
- #training-development
- #announcements

---

## ✅ You're Done!

Your bot is now:
- ✅ Created
- ✅ Has correct permissions
- ✅ Token saved to .env
- ✅ Added to all channels

**Now run:**
```bash
python3 tools/hermes_slack_sync.py
```

Your bot will send messages to Slack!

---

## 🔍 Troubleshooting

### Problem: Bot not sending messages

**Solution:**
```bash
# 1. Check .env has correct token
cat .env | grep SLACK_BOT_TOKEN

# 2. Verify bot is in channel (in Slack):
/invite @ProCare Pharmacy

# 3. Check scopes
# Go to: https://api.slack.com/apps → OAuth & Permissions
# Should show: chat:write ✓, chat:write.public ✓

# 4. Run test
python3 tools/hermes_slack_sync.py
```

### Problem: Token not found error

**Solution:**
```bash
# 1. Verify .env file exists
ls -la .env

# 2. Check token is in file
grep SLACK_BOT_TOKEN .env

# 3. Make sure NO SPACES around token
# Should be: SLACK_BOT_TOKEN=xoxb-...
# NOT: SLACK_BOT_TOKEN = xoxb-... (spaces break it)
```

### Problem: Channel not found

**Solution:**
1. Make sure bot is invited to channel
2. Check channel name matches exactly (lowercase, hyphens)
3. Create channel if it doesn't exist

---

## 📝 Quick Reference

| Item | Value |
|------|-------|
| Website | https://api.slack.com/apps |
| Create App | Click "Create New App" → "From scratch" |
| App Name | ProCare Pharmacy |
| Scopes | chat:write, chat:write.public |
| Token Location | Bot User OAuth Token (top of OAuth & Permissions) |
| Save Location | .env file → SLACK_BOT_TOKEN=xoxb-... |
| Invite Bot | Add app to each channel |

---

## 🎯 Next Steps

1. ✅ Create bot (follow steps above)
2. ✅ Copy token to .env
3. ✅ Add bot to all channels
4. Run test: `python3 tools/hermes_slack_sync.py`
5. Start API: `python3 app.py`
6. Schedule cron: `crontab -e`

---

**For more help**: See `EXECUTION_PLAN.md`

