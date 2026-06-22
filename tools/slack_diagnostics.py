"""
slack_diagnostics.py - Why didn't Slack receive anything from Hermes?

Run this whenever Slack is NOT receiving reports/alerts from Hermes.
It checks every link in the chain, one by one, and tells you in plain
language exactly which step is broken and how to fix it.

    python tools/slack_diagnostics.py

Chain that must work for a message to arrive:
    .env token  ->  Slack auth  ->  channel exists  ->  bot in channel  ->  send

This script is READ-ONLY for your data. The only message it sends is an
optional test message (you are asked first).
"""

import os
import sys

# ── Make sibling modules importable when run from repo root or tools/ ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _load_env():
    """Load .env if python-dotenv is available (non-fatal if missing)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        return False


def _line(char="─", n=60):
    print(char * n)


def _fail(step, problem, fix):
    print(f"\n❌ STEP {step} FAILED: {problem}")
    print(f"   FIX: {fix}")


def _ok(step, msg):
    print(f"✅ STEP {step}: {msg}")


def check_dependencies():
    """STEP 0 — required Python packages are installed."""
    missing = []
    try:
        import slack_sdk  # noqa: F401
    except ImportError:
        missing.append("slack-sdk")
    if missing:
        _fail(
            "0",
            f"Missing Python package(s): {', '.join(missing)}",
            "Run:  pip install -r requirements.txt",
        )
        return False
    _ok("0", "Required packages installed (slack-sdk)")
    return True


def check_token():
    """STEP 1 — bot token is present in the environment / .env."""
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        _fail(
            "1",
            "SLACK_BOT_TOKEN is empty or not set.",
            "Open the .env file and set SLACK_BOT_TOKEN=xoxb-...  "
            "(create the bot + token at https://api.slack.com/apps, then "
            "OAuth & Permissions -> Bot User OAuth Token). "
            "THIS IS THE #1 REASON SLACK RECEIVES NOTHING.",
        )
        return None
    if not token.startswith("xoxb-"):
        print(
            "⚠️  STEP 1: SLACK_BOT_TOKEN is set but does NOT start with 'xoxb-'.\n"
            "   A Bot User OAuth Token is expected. If you pasted a different "
            "token (e.g. xoxp- user token or a webhook URL), Slack calls will fail."
        )
    else:
        _ok("1", f"SLACK_BOT_TOKEN is set (xoxb-…{token[-4:]})")
    return token


def check_auth(token):
    """STEP 2 — the token actually authenticates against Slack."""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    client = WebClient(token=token)
    try:
        resp = client.auth_test()
        _ok(
            "2",
            f"Authenticated as bot '{resp.get('user')}' "
            f"in workspace '{resp.get('team')}'",
        )
        return client
    except SlackApiError as e:
        err = e.response.get("error", "unknown")
        fixes = {
            "invalid_auth": "Token is wrong or was revoked. Re-copy the Bot "
                            "User OAuth Token and reinstall the app to the workspace.",
            "account_inactive": "The bot/app was deactivated. Re-enable it at "
                                "https://api.slack.com/apps.",
            "token_revoked": "Token was revoked. Reinstall the app and copy the new token.",
        }
        _fail("2", f"Slack rejected the token ({err}).",
              fixes.get(err, "Verify the token and reinstall the Slack app."))
        return None


def check_channel(client, target):
    """STEP 3 — the configured channel exists and we can find its ID.

    Needs the 'channels:read' (public) / 'groups:read' (private) scope.
    Returns the resolved channel id, or None.
    """
    from slack_sdk.errors import SlackApiError

    target_name = target.lstrip("#")
    print(f"\nLooking for channel '{target}' …")
    try:
        found = []
        cursor = None
        while True:
            resp = client.conversations_list(
                types="public_channel,private_channel",
                limit=200,
                cursor=cursor,
            )
            for ch in resp.get("channels", []):
                found.append(ch)
                if ch.get("name") == target_name or ch.get("id") == target_name:
                    _ok("3", f"Channel found: #{ch['name']}  (ID: {ch['id']})")
                    print(f"   👉 Put this CHANNEL ID in Hermes: {ch['id']}")
                    return ch["id"]
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        _fail(
            "3",
            f"Channel '{target}' was not found among "
            f"{len(found)} channel(s) the bot can see.",
            "Create the channel in Slack, or fix SLACK_CHANNEL in .env. "
            "Available channels are listed below.",
        )
        if found:
            print("\n   Channels the bot can currently see:")
            for ch in sorted(found, key=lambda c: c.get("name", "")):
                priv = " (private)" if ch.get("is_private") else ""
                print(f"     • #{ch.get('name')}  ->  {ch.get('id')}{priv}")
        return None
    except SlackApiError as e:
        err = e.response.get("error", "unknown")
        if err == "missing_scope":
            _fail(
                "3",
                "Bot is missing the 'channels:read' scope, so it cannot list "
                "channels to resolve the channel ID.",
                "Add scopes 'channels:read' and 'groups:read' under OAuth & "
                "Permissions, then reinstall the app. "
                "(Sending still works with chat:write even without this — "
                "this step is only needed to auto-discover the channel ID.)",
            )
        else:
            _fail("3", f"Could not list channels ({err}).",
                  "Check the bot scopes and reinstall the app.")
        return None


def check_send(client, channel):
    """STEP 4 — actually deliver a test message to the channel."""
    from slack_sdk.errors import SlackApiError

    ans = input(
        f"\nSend a test message to '{channel}' now to confirm delivery? [y/N] "
    ).strip().lower()
    if ans != "y":
        print("   Skipped sending a test message.")
        return None
    try:
        client.chat_postMessage(
            channel=channel,
            text="🧪 Hermes → Slack diagnostic test. If you can read this, "
                 "the connection works and Hermes can deliver reports here.",
        )
        _ok("4", f"Test message delivered to {channel}. Check Slack now.")
        return True
    except SlackApiError as e:
        err = e.response.get("error", "unknown")
        fixes = {
            "not_in_channel": "The bot is NOT a member of this channel. In Slack, "
                              "open the channel and type:  /invite @ProCare Pharmacy",
            "channel_not_found": "Channel name/ID is wrong, or it's a private "
                                 "channel the bot hasn't been invited to. "
                                 "Invite the bot, or use the channel ID.",
            "is_archived": "The channel is archived. Un-archive it or pick another.",
            "missing_scope": "Bot is missing the 'chat:write' scope. Add it under "
                             "OAuth & Permissions and reinstall the app.",
        }
        _fail("4", f"Could not send the message ({err}).",
              fixes.get(err, "See https://api.slack.com/methods/chat.postMessage"))
        return False


def check_database():
    """STEP 5 (informational) — can Hermes reach the SQL Server?

    Even with Slack working, the DAILY REPORT needs the database. If this
    fails, Slack stays silent because there's no data to send.
    """
    try:
        import pyodbc  # noqa: F401
    except ImportError:
        print("\nℹ️  STEP 5 (data source): pyodbc not installed in THIS "
              "environment — skipping DB check. The daily report needs it on "
              "the machine that runs the sync.")
        return None

    import pyodbc
    server = os.getenv("SQL_SERVER", "DESKTOP-3A9JFL4")
    database = os.getenv("SQL_DATABASE", "stock")
    driver = os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}")
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        conn.close()
        _ok("5", f"Database reachable ({server}/{database}).")
        return True
    except Exception as e:  # noqa: BLE001 - report any driver/connection error
        print(f"\nℹ️  STEP 5 (data source): Could NOT reach the database "
              f"({server}/{database}).\n   {e}\n   The Slack link can still work; "
              "but the DAILY REPORT will be empty until the DB is reachable "
              "from the machine running Hermes.")
        return False


def main():
    print()
    _line("=")
    print("  HERMES → SLACK DIAGNOSTICS")
    print("  Checking why Slack did not receive messages from Hermes")
    _line("=")

    env_loaded = _load_env()
    print(f"\n.env loaded: {'yes' if env_loaded else 'no (python-dotenv not installed)'}")
    print(f"SLACK_CHANNEL configured as: {os.getenv('SLACK_CHANNEL', '#pharmacy-alerts')}")
    _line()

    if not check_dependencies():
        _summary(["Install dependencies, then re-run this diagnostic."])
        return False

    token = check_token()
    if not token:
        _summary([
            "Slack received nothing because SLACK_BOT_TOKEN is not set.",
            "Set it in .env and re-run this diagnostic.",
        ])
        return False

    client = check_auth(token)
    if not client:
        _summary(["The bot token is invalid. Fix the token and re-run."])
        return False

    target = os.getenv("SLACK_CHANNEL", "#pharmacy-alerts")
    channel_id = check_channel(client, target)

    # Sending can work via channel name even if listing failed (scope),
    # so attempt the send against the resolved id or the configured name.
    check_send(client, channel_id or target)

    check_database()

    _line("=")
    print("  DIAGNOSTIC COMPLETE")
    _line("=")
    print(
        "\nReminder of the full chain:\n"
        "  .env token → Slack auth → channel exists → bot invited → send\n"
        "Fix any ❌ above (top-down), then run:\n"
        "  python tools/hermes_slack_sync.py\n"
    )
    return True


def _summary(lines):
    print()
    _line("=")
    print("  RESULT")
    _line("=")
    for ln in lines:
        print(f"  • {ln}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
