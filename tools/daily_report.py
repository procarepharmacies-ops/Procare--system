import pyodbc, os
from datetime import datetime, timedelta

SERVER="DESKTOP-3A9JFL4"; DATABASE="stock"
conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn=pyodbc.connect(conn_str,timeout=10); cursor=conn.cursor()
today=datetime.now().date(); report_date=today

cursor.execute("""
    SELECT b.branch_name, COUNT(s.sales_id) AS tx_count, SUM(s.total_bill_net) AS total_sales
    FROM Sales_header s LEFT JOIN Branches b ON b.branch_id=s.store_id
    WHERE CAST(s.bill_date AS DATE)=? AND s.back!='Y'
    GROUP BY b.branch_name, s.store_id ORDER BY total_sales DESC
""", report_date)
branch_sales=cursor.fetchall()

cursor.execute("""
    SELECT TOP 5 p.product_name_ar, p.product_name_en, SUM(d.amount) AS qty, SUM(d.total_sell) AS rev
    FROM Sales_details d JOIN Sales_header s ON s.sales_id=d.sales_id JOIN Products p ON p.product_id=d.product_id
    WHERE CAST(s.bill_date AS DATE)=? AND s.back!='Y' AND d.back!='Y'
    GROUP BY p.product_name_ar, p.product_name_en ORDER BY rev DESC
""", report_date)
top5=cursor.fetchall()

cursor.execute("""
    SELECT TOP 10 p.product_name_ar, p.product_name_en, pa.exp_date, pa.amount,
    DATEDIFF(day,GETDATE(),pa.exp_date) AS days_left
    FROM Product_Amount pa JOIN Products p ON p.product_id=pa.product_id
    WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,60,GETDATE())
    AND pa.amount>0 AND p.deleted!='Y' ORDER BY pa.exp_date ASC
""")
expiry=cursor.fetchall(); conn.close()

total=sum(r.total_sales or 0 for r in branch_sales)
txs=sum(r.tx_count or 0 for r in branch_sales)
print(f"\n{'='*55}")
print(f"PROCARE PHARMACY - DAILY REPORT - {report_date}")
print(f"{'='*55}")
print(f"TOTAL SALES:  EGP {total:,.2f}  |  TRANSACTIONS: {txs:,}")
print(f"\nBY BRANCH:")
[print(f"  {r.branch_name or 'Branch':<20} EGP {r.total_sales or 0:>12,.2f}  ({r.tx_count} tx)") for r in branch_sales]
print(f"\nTOP 5 PRODUCTS:")
[print(f"  {i}. {p.product_name_ar or p.product_name_en:<35} EGP {p.rev:>10,.2f}") for i,p in enumerate(top5,1)]
print(f"\nEXPIRY ALERTS:")
[print(f"  {'URGENT' if e.days_left<=14 else 'WARN'} | {e.product_name_ar or e.product_name_en:<35} {e.days_left}d | qty:{e.amount:.0f}") for e in expiry] if expiry else print("  None")
print(f"{'='*55}")
