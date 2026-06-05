"""
slack_templates.py - ProCare Slack Message Templates
Generates formatted messages for different notification types
"""

from datetime import datetime
from typing import Dict, List, Optional


class SlackTemplates:
    """Message templates for ProCare pharmacy operations."""

    @staticmethod
    def daily_summary(
        date: str,
        total_sales: float,
        prev_sales: float,
        transaction_count: int,
        top_product: str,
        branches: List[Dict],
        treasury: float,
        expiry_count: int,
        low_stock_count: int,
        discrepancies: int
    ) -> List[Dict]:
        """Generate daily summary block message."""
        pct_change = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        change_emoji = "📈" if pct_change >= 0 else "📉"
        health_emoji = "🟢" if discrepancies == 0 else "🟡" if discrepancies < 3 else "🔴"

        branch_text = '\n'.join([
            f"  • {b['name']}: EGP {b['total']:,.0f} ({b['tx']} tx)"
            for b in branches[:3]
        ])

        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 PROCARE DAILY REPORT",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {date}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Sales*\nEGP {total_sales:,.0f}\n{change_emoji} {pct_change:+.1f}% vs yesterday"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Transactions*\n{transaction_count:,}\nAvg: EGP {total_sales/transaction_count:,.0f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Top Product*\n{top_product}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Treasury*\nEGP {treasury:,.0f}\nOn hand"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*SALES BY BRANCH*\n{branch_text}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Expiring Soon*\n{expiry_count} items ≤60d"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Low Stock*\n{low_stock_count} items"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Discrepancies*\n{discrepancies} items"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Health Status*\n{health_emoji} {'HEALTHY' if discrepancies == 0 else 'WATCH' if discrepancies < 3 else 'ACTION NEEDED'}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Full Dashboard"
                        },
                        "url": "http://localhost:5000",
                        "style": "primary"
                    }
                ]
            }
        ]

    @staticmethod
    def expiry_alert(
        product_name: str,
        days_left: int,
        qty: float,
        exp_date: str,
        branch: str = "All"
    ) -> List[Dict]:
        """Generate expiry alert block message."""
        is_urgent = days_left <= 7
        emoji = "🔴 URGENT" if is_urgent else "🟡 WARNING"
        color = "danger" if is_urgent else "warning"

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} - Medication Expiry Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Product*\n{product_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Expires*\n{exp_date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Days Left*\n{days_left}d"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quantity*\n{qty:.0f} units"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Action*\n{'Remove & Document' if is_urgent else 'Monitor for Removal'}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Alert triggered at {datetime.now().strftime('%H:%M:%S')} | Contact pharmacy manager for action"
                    }
                ]
            }
        ]

    @staticmethod
    def low_stock_alert(
        product_name: str,
        current_qty: float,
        reorder_point: int,
        branch: str
    ) -> List[Dict]:
        """Generate low stock alert block message."""
        return [
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
                        "text": f"*Product*\n{product_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Current Stock*\n{current_qty:.0f} units"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Reorder Point*\n{reorder_point} units"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Shortage*\n{reorder_point - current_qty:.0f} units below minimum"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status*\n⏳ Awaiting Reorder"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Purchase Order"
                        },
                        "value": f"reorder_{product_name}",
                        "style": "primary"
                    }
                ]
            }
        ]

    @staticmethod
    def cash_reconciliation(
        branch: str,
        date: str,
        pos_total: float,
        physical_count: float,
        variance: float,
        variance_pct: float
    ) -> List[Dict]:
        """Generate cash reconciliation block message."""
        is_balanced = abs(variance_pct) < 1.0
        is_minor = abs(variance_pct) < 2.0
        status_emoji = "✅" if is_balanced else "⚠️" if is_minor else "🔴"

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💰 *DAILY CASH RECONCILIATION*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Date*\n{date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*POS Total*\nEGP {pos_total:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Physical Count*\nEGP {physical_count:,.2f}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *Variance:* {variance:+,.2f} EGP ({variance_pct:+.2f}%)"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Status: {'✅ BALANCED' if is_balanced else '⚠️ MINOR ISSUE' if is_minor else '🔴 MAJOR DISCREPANCY - INVESTIGATION REQUIRED'}"
                    }
                ]
            }
        ]

    @staticmethod
    def shift_reminder(
        employee_name: str,
        start_time: str,
        branch: str,
        position: str,
        tasks: List[str] = None
    ) -> List[Dict]:
        """Generate shift reminder block message."""
        task_text = '\n'.join([f"  • {t}" for t in (tasks or [])]) if tasks else "  • Review day's schedule"

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📍 *SHIFT REMINDER*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Employee*\n{employee_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Start Time*\n{start_time}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Location*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Role*\n{position}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Tasks*\n{task_text}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Confirm Attendance"
                        },
                        "value": "confirm",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Call In Absence"
                        },
                        "value": "absent",
                        "style": "danger"
                    }
                ]
            }
        ]

    @staticmethod
    def system_status(
        status: str,
        database: bool,
        api: bool,
        slack: bool,
        last_backup: str,
        issues: Optional[str] = None
    ) -> List[Dict]:
        """Generate system status block message."""
        status_emoji = {"ok": "🟢", "degraded": "🟡", "down": "🔴"}
        status_text = {"ok": "OPERATIONAL", "degraded": "DEGRADED", "down": "DOWN"}

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji.get(status, '❓')} *SYSTEM STATUS*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status*\n{status_text.get(status, 'UNKNOWN')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Database*\n{'✅ Connected' if database else '❌ Disconnected'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*API*\n{'✅ Running' if api else '❌ Down'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Slack Integration*\n{'✅ Active' if slack else '❌ Inactive'}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Last Backup*\n{last_backup}"
                }
            }
        ] + (
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Issues*\n{issues}"
                    }
                }
            ] if issues else []
        )

    @staticmethod
    def compliance_alert(
        alert_type: str,
        severity: str,
        issue: str,
        affected: str,
        action_required: str,
        deadline: str,
        owner: str
    ) -> List[Dict]:
        """Generate compliance alert block message."""
        severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📋 *COMPLIANCE ALERT* — {severity_emoji.get(severity, '❓')} {severity.upper()}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Type*\n{alert_type.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Affected*\n{affected}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Owner*\n{owner}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Deadline*\n{deadline}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Issue*\n{issue}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Required*\n{action_required}"
                }
            }
        ]

    @staticmethod
    def inventory_discrepancy(
        product: str,
        branch: str,
        expected: float,
        physical: float,
        variance: float,
        last_count: str,
        status: str,
        root_cause: Optional[str] = None
    ) -> List[Dict]:
        """Generate inventory discrepancy block message."""
        variance_pct = (variance / expected * 100) if expected > 0 else 0

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *INVENTORY DISCREPANCY*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Product*\n{product}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Branch*\n{branch}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Expected*\n{expected:.0f} units"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Physical Count*\n{physical:.0f} units"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Variance*\n{variance:+.0f} units ({variance_pct:+.1f}%)"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Last Count*\n{last_count}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status*\n{status.upper()}"
                    }
                ]
            }
        ] + (
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Root Cause*\n{root_cause}"
                    }
                }
            ] if root_cause else []
        )

    @staticmethod
    def branch_comparison(
        date: str,
        branches: List[Dict],
        total_sales: float
    ) -> List[Dict]:
        """Generate branch comparison block message."""
        # Sort by sales descending
        sorted_branches = sorted(branches, key=lambda x: x['total'], reverse=True)

        branch_blocks = []
        for i, b in enumerate(sorted_branches[:5], 1):
            pct_of_total = (b['total'] / total_sales * 100) if total_sales > 0 else 0
            branch_blocks.append({
                "type": "mrkdwn",
                "text": f"{i}. {b['name']}: EGP {b['total']:,.0f} ({pct_of_total:.1f}% | {b['tx']} tx)"
            })

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📊 *BRANCH COMPARISON — {date}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Sales*\nEGP {total_sales:,.0f}"
                }
            },
            {
                "type": "section",
                "fields": branch_blocks
            }
        ]


if __name__ == '__main__':
    # Test template generation
    templates = SlackTemplates()

    # Test daily summary
    blocks = templates.daily_summary(
        date="2026-06-04",
        total_sales=15500.00,
        prev_sales=14200.00,
        transaction_count=84,
        top_product="Paracetamol 500mg",
        branches=[
            {"name": "Elsanta", "total": 9000.00, "tx": 52},
            {"name": "Mashala", "total": 6500.00, "tx": 32}
        ],
        treasury=25000.00,
        expiry_count=8,
        low_stock_count=3,
        discrepancies=0
    )
    print("Daily Summary Template Generated")

    # Test expiry alert
    blocks = templates.expiry_alert(
        product_name="Aspirin 500mg",
        days_left=5,
        qty=12,
        exp_date="2026-06-10"
    )
    print("Expiry Alert Template Generated")

    print("\n✅ All templates working correctly")
