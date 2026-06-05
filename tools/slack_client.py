"""
slack_client.py - ProCare Slack Integration
Sends pharmacy alerts and reports to Slack channel
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackMessenger:
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Slack client with bot token from env or parameter."""
        token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        if not token:
            raise ValueError(
                'SLACK_BOT_TOKEN not set. Set it in .env or pass as parameter.'
            )
        self.client = WebClient(token=token)
        self.channel = os.getenv('SLACK_CHANNEL', '#pharmacy-alerts')

    def send_message(self, text: str, channel: Optional[str] = None) -> bool:
        """Send a plain text message to Slack."""
        try:
            self.client.chat_postMessage(
                channel=channel or self.channel,
                text=text
            )
            return True
        except SlackApiError as e:
            print(f"Slack error: {e.response['error']}")
            return False

    def send_block_message(
        self,
        blocks: List[Dict],
        channel: Optional[str] = None
    ) -> bool:
        """Send a formatted block message to Slack."""
        try:
            self.client.chat_postMessage(
                channel=channel or self.channel,
                blocks=blocks
            )
            return True
        except SlackApiError as e:
            print(f"Slack error: {e.response['error']}")
            return False

    def send_daily_report(
        self,
        branches: List[Dict],
        top_products: List[Dict],
        expiry_items: List[Dict],
        total_sales: float,
        total_tx: int,
        report_date: str
    ) -> bool:
        """Send formatted daily report to Slack."""
        # Build branch summary
        branch_text = '\n'.join([
            f"  • {b['name']}: EGP {b['total']:,.2f} ({b['tx']} tx)"
            for b in branches
        ])

        # Build top products
        products_text = '\n'.join([
            f"  {i}. {p['name']}: EGP {p['revenue']:,.2f} (qty: {p['qty']:.0f})"
            for i, p in enumerate(top_products[:5], 1)
        ])

        # Build expiry alerts (limit to urgent ones)
        urgent_items = [e for e in expiry_items if e['days_left'] <= 14]
        if urgent_items:
            expiry_text = '\n'.join([
                f"  🚨 {e['name']}: {e['days_left']}d left (qty: {e['qty']:.0f})"
                for e in urgent_items[:5]
            ])
        else:
            expiry_text = "  ✅ No urgent expiries"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 ProCare Daily Report",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {report_date}\n*Total Sales:* EGP {total_sales:,.2f}\n*Transactions:* {total_tx}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Sales by Branch:*\n{branch_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top Products:*\n{products_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Expiry Alerts (next 60 days):*\n{expiry_text}"
                }
            }
        ]

        return self.send_block_message(blocks)

    def send_expiry_alert(
        self,
        product_name: str,
        days_left: int,
        qty: float,
        exp_date: str
    ) -> bool:
        """Send urgent expiry alert to Slack."""
        urgency = "🔴 URGENT" if days_left <= 7 else "🟡 WARNING"

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{urgency} - Product Expiry Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Product:*\n{product_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Expires:*\n{exp_date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Days Left:*\n{days_left}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity:*\n{qty:.0f} units"
                    }
                ]
            }
        ]

        return self.send_block_message(blocks)

    def send_low_stock_alert(
        self,
        product_name: str,
        current_qty: float,
        reorder_point: int,
        branch: str
    ) -> bool:
        """Send low stock alert to Slack."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🟠 Low Stock Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Product:*\n{product_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch:*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Current:*\n{current_qty:.0f} units"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Reorder Point:*\n{reorder_point} units"
                    }
                ]
            }
        ]

        return self.send_block_message(blocks)

    def test_connection(self) -> bool:
        """Test Slack connection with auth.test."""
        try:
            response = self.client.auth_test()
            return response['ok']
        except SlackApiError as e:
            print(f"Slack connection failed: {e.response['error']}")
            return False


if __name__ == '__main__':
    # Test the Slack client
    try:
        messenger = SlackMessenger()
        if messenger.test_connection():
            print("✅ Slack connection successful")
            # Send test message
            messenger.send_message("ProCare Slack integration test - SUCCESS ✅")
        else:
            print("❌ Slack connection failed")
    except ValueError as e:
        print(f"❌ Error: {e}")
