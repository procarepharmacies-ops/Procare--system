"""
hermes_slack_sync.py - Hermes to Slack Synchronization
Automatically pulls data from ProCare database and sends reports/alerts to Slack
This is the main integration point between Hermes (pharmacy system) and Slack
"""

import os
import sys
import pyodbc
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Slack client
from slack_client import SlackMessenger


def get_db_connection():
    """Create a database connection to ProCare Stock."""
    server = os.getenv('SQL_SERVER', 'DESKTOP-3A9JFL4')
    database = os.getenv('SQL_DATABASE', 'stock')
    driver = os.getenv('SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')
    username = os.getenv('SQL_USERNAME', '')
    password = os.getenv('SQL_PASSWORD', '')

    if username:
        conn_str = (
            f"DRIVER={driver};SERVER={server},1433;DATABASE={database};"
            f"UID={username};PWD={password};TrustServerCertificate=yes;"
        )
    else:
        # Windows Authentication (only works on domain-joined Windows machines)
        conn_str = f"DRIVER={driver};SERVER={server},1433;DATABASE={database};Trusted_Connection=yes;"

    return pyodbc.connect(conn_str, timeout=10)


def fetch_yesterday_sales():
    """Fetch yesterday's sales by branch."""
    conn = get_db_connection()
    cursor = conn.cursor()
    yesterday = (datetime.now().date() - timedelta(days=1))

    cursor.execute("""
        SELECT b.branch_name, COUNT(*) AS tx,
               ISNULL(SUM(s.total_bill_net),0) AS total,
               ISNULL(SUM(s.total_disc_money),0) AS disc
        FROM Branches_sales_header s
        LEFT JOIN Branches b ON b.branch_id=s.branch_id
        WHERE CAST(s.insert_date AS DATE)=?
        GROUP BY b.branch_name
        ORDER BY total DESC
    """, yesterday)

    branches = []
    for row in cursor.fetchall():
        branches.append({
            'name': row.branch_name or 'Unknown',
            'tx': int(row.tx or 0),
            'total': float(row.total or 0),
            'disc': float(row.disc or 0)
        })

    conn.close()
    return branches, yesterday


def fetch_top_products():
    """Fetch top 5 products by revenue yesterday."""
    conn = get_db_connection()
    cursor = conn.cursor()
    yesterday = (datetime.now().date() - timedelta(days=1))

    cursor.execute("""
        SELECT TOP 5
            p.product_name_ar, p.product_name_en,
            SUM(d.amount) AS qty,
            ISNULL(SUM(d.total_sell),0) AS revenue
        FROM Branches_sales_details d
        JOIN Branches_sales_header s ON s.sales_id=d.sales_id AND s.branch_id=d.branch_id
        JOIN Products p ON p.product_id=d.product_id
        WHERE CAST(s.insert_date AS DATE)=?
        GROUP BY p.product_name_ar, p.product_name_en
        ORDER BY revenue DESC
    """, yesterday)

    products = []
    for row in cursor.fetchall():
        products.append({
            'name': row.product_name_ar or row.product_name_en or 'Unknown',
            'qty': float(row.qty or 0),
            'revenue': float(row.revenue or 0)
        })

    conn.close()
    return products


def fetch_expiry_items():
    """Fetch items expiring in next 60 days."""
    conn = get_db_connection()
    cursor = conn.cursor()
    expiry_days = int(os.getenv('ALERT_EXPIRY_DAYS', '60'))

    cursor.execute(f"""
        SELECT TOP 20
            p.product_name_ar, p.product_name_en,
            pa.exp_date, pa.amount,
            DATEDIFF(day, GETDATE(), pa.exp_date) AS days_left
        FROM Product_Amount pa
        JOIN Products p ON p.product_id=pa.product_id
        WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,{expiry_days},GETDATE())
        AND pa.amount>0 AND p.deleted!='Y'
        ORDER BY pa.exp_date ASC
    """)

    items = []
    for row in cursor.fetchall():
        items.append({
            'name': row.product_name_ar or row.product_name_en or 'Unknown',
            'qty': float(row.amount or 0),
            'exp_date': str(row.exp_date)[:10] if row.exp_date else '',
            'days_left': int(row.days_left or 0),
            'urgent': int(row.days_left or 0) <= 14
        })

    conn.close()
    return items


def send_daily_report_to_slack(slack_messenger):
    """Generate and send daily report to Slack."""
    print("📊 Generating daily report...")

    try:
        branches, report_date = fetch_yesterday_sales()
        products = fetch_top_products()
        expiry_items = fetch_expiry_items()

        total_sales = sum(b['total'] for b in branches)
        total_tx = sum(b['tx'] for b in branches)

        print(f"  Total Sales: EGP {total_sales:,.2f}")
        print(f"  Transactions: {total_tx}")
        print(f"  Branches: {len(branches)}")
        print(f"  Top Products: {len(products)}")
        print(f"  Expiry Items: {len(expiry_items)}")

        success = slack_messenger.send_daily_report(
            branches=branches,
            top_products=products,
            expiry_items=expiry_items,
            total_sales=total_sales,
            total_tx=total_tx,
            report_date=str(report_date)
        )

        if success:
            print("✅ Daily report sent to Slack")
        else:
            print("❌ Failed to send daily report")

        return success

    except Exception as e:
        print(f"❌ Error generating daily report: {e}")
        return False


def send_urgent_expiry_alerts(slack_messenger):
    """Send alerts for items expiring in next 7 days."""
    print("🚨 Checking for urgent expiry alerts...")

    try:
        items = fetch_expiry_items()
        urgent_items = [item for item in items if item['days_left'] <= 7 and item['days_left'] > 0]

        if not urgent_items:
            print("  ✅ No urgent expiries")
            return True

        print(f"  Found {len(urgent_items)} urgent item(s)")

        for item in urgent_items:
            slack_messenger.send_expiry_alert(
                product_name=item['name'],
                days_left=item['days_left'],
                qty=item['qty'],
                exp_date=item['exp_date']
            )

        print(f"✅ Sent {len(urgent_items)} expiry alert(s)")
        return True

    except Exception as e:
        print(f"❌ Error checking expiry alerts: {e}")
        return False


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("  HERMES ↔ SLACK SYNCHRONIZATION")
    print("="*60)

    try:
        # Initialize Slack messenger
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        if not slack_token:
            print("❌ SLACK_BOT_TOKEN not set in .env")
            print("   Set it in your .env file before running this script")
            return False

        slack_messenger = SlackMessenger(bot_token=slack_token)

        # Test connection
        if not slack_messenger.test_connection():
            print("❌ Failed to connect to Slack")
            return False

        print("✅ Connected to Slack\n")

        # Send daily report
        send_daily_report_to_slack(slack_messenger)

        # Send urgent expiry alerts
        send_urgent_expiry_alerts(slack_messenger)

        print("\n" + "="*60)
        print("  SYNC COMPLETE")
        print("="*60)
        return True

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
