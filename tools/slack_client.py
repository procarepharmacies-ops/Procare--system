"""
slack_client.py - ProCare Slack Integration
Sends pharmacy alerts and reports to Slack channel
Uses slack_templates.py for message formatting
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_templates import SlackTemplates


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
        self.templates = SlackTemplates()

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
        report_date: str,
        prev_sales: float = 0,
        channel: Optional[str] = None,
        treasury: float = 0,
        discrepancies: int = 0
    ) -> bool:
        """Send formatted daily report to Slack using templates."""
        expiry_count = len([e for e in expiry_items if e['days_left'] <= 60])
        low_stock_count = len([e for e in expiry_items if 'low_stock' in e and e['low_stock']])

        blocks = self.templates.daily_summary(
            date=report_date,
            total_sales=total_sales,
            prev_sales=prev_sales or total_sales,
            transaction_count=total_tx,
            top_product=top_products[0]['name'] if top_products else 'N/A',
            branches=branches,
            treasury=treasury,
            expiry_count=expiry_count,
            low_stock_count=low_stock_count,
            discrepancies=discrepancies
        )

        return self.send_block_message(blocks, channel=channel or self.channel)

    def send_expiry_alert(
        self,
        product_name: str,
        days_left: int,
        qty: float,
        exp_date: str,
        branch: str = "All",
        channel: Optional[str] = None
    ) -> bool:
        """Send urgent expiry alert to Slack using templates."""
        blocks = self.templates.expiry_alert(
            product_name=product_name,
            days_left=days_left,
            qty=qty,
            exp_date=exp_date,
            branch=branch
        )

        return self.send_block_message(blocks, channel=channel or self.channel)

    def send_low_stock_alert(
        self,
        product_name: str,
        current_qty: float,
        reorder_point: int,
        branch: str,
        channel: Optional[str] = None
    ) -> bool:
        """Send low stock alert to Slack using templates."""
        blocks = self.templates.low_stock_alert(
            product_name=product_name,
            current_qty=current_qty,
            reorder_point=reorder_point,
            branch=branch
        )

        return self.send_block_message(blocks, channel=channel or self.channel)

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
