import pyodbc
from datetime import datetime, timedelta

SERVER = "DESKTOP-3A9JFL4"
DATABASE = "stock"
SLACK_TOKEN = ""
SLACK_CHANNEL = "C0AP0NL9BE3"

conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str, timeout=10)
cursor = conn.cursor()
today = datetime.now().date()
yesterday = today - timedelta(days=1)

cursor.execute("""
    SELECT b.branch_name, COUNT(*) AS tx, SUM(s.total_bill_net) AS total, SUM(s.total_disc_money) AS disc
    FROM Branches_sales_header s LEFT JOIN Branches b ON b.branch_id=s.branch_id
    WHERE CAST(s.insert_date AS DATE)=? 
    GROUP BY b.branch_name ORDER BY total DESC
""", yesterday)
branches = cursor.fetchall()

cursor.execute("""
    SELECT TOP 5 p.product_name_ar, p.product_name_en, SUM(d.amount) AS qty, SUM(d.total_sell) AS rev
    FROM Branches_sales_details d
    JOIN Branches_sales_header s ON s.sales_id=d.sales_id AND s.branch_id=d.branch_id
    JOIN Products p ON p.product_id=d.product_id
    WHERE CAST(s.insert_date AS DATE)=?
    GROUP BY p.product_name_ar, p.product_name_en ORDER BY rev DESC
""", yesterday)
top5 = cursor.fetchall()

cursor.execute("""
    SELECT TOP 10 p.product_name_ar, p.product_name_en, pa.exp_date, pa.amount,
    DATEDIFF(day, GETDATE(), pa.exp_date) AS days_left
    FROM Product_Amount pa JOIN Products p ON p.product_id=pa.product_id
    WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,60,GETDATE())
    AND pa.amount>0 AND p.deleted!='Y' ORDER BY pa.exp_date ASC
""")
expiry = cursor.fetchall()
conn.close()

total = sum(r.total or 0 for r in branches)
txs   = sum(r.tx or 0 for r in branches)

print("="*55)
print(f"  PROCARE PHARMACY - DAILY REPORT")
print(f"  {yesterday.strftime('%A, %d %B %Y')}")
print("="*55)
print(f"\n  TOTAL SALES:    EGP {total:>10,.2f}")
print(f"  TRANSACTIONS:   {txs:>10,}")
print(f"\n  BY BRANCH:")
for r in branches:
    print(f"    {r.branch_name or 'Branch':<20} EGP {r.total or 0:>10,.2f}  ({r.tx} tx)")

print(f"\n  TOP 5 PRODUCTS:")
for i,p in enumerate(top5,1):
    name = p.product_name_ar or p.product_name_en or "?"
    print(f"    {i}. {name:<35} EGP {p.rev:>8,.2f}  (qty:{p.qty:.0f})")

print(f"\n  EXPIRY ALERTS (next 60 days):")
if expiry:
    for e in expiry:
        flag = "URGENT" if e.days_left<=14 else "WARN  "
        name = e.product_name_ar or e.product_name_en or "?"
        print(f"    {flag} | {name:<35} | {e.days_left}d | qty:{e.amount:.0f}")
else:
    print("    No alerts.")
print("="*55)