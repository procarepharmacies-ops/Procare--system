import pyodbc
from datetime import datetime, timedelta

SERVER="DESKTOP-3A9JFL4"; DATABASE="stock"
conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn=pyodbc.connect(conn_str,timeout=10); cursor=conn.cursor()

# Find real date range
cursor.execute("""
    SELECT TOP 5 CAST(bill_date AS DATE) AS day, COUNT(*) AS tx, SUM(total_bill_net) AS total
    FROM Branches_sales_header WHERE back!='Y' AND bill_date IS NOT NULL
    GROUP BY CAST(bill_date AS DATE) ORDER BY day DESC
""")
print("REAL SALES (last 5 days):")
for r in cursor.fetchall():
    print(f"  {r.day}  |  {r.tx} tx  |  EGP {r.total:,.2f}")

# Branch breakdown
cursor.execute("""
    SELECT b.branch_name, COUNT(*) AS tx, SUM(s.total_bill_net) AS total
    FROM Branches_sales_header s LEFT JOIN Branches b ON b.branch_id=s.store_id
    WHERE CAST(s.bill_date AS DATE) >= DATEADD(day,-7,GETDATE()) AND s.back!='Y'
    GROUP BY b.branch_name ORDER BY total DESC
""")
print("\nLAST 7 DAYS BY BRANCH:")
for r in cursor.fetchall():
    print(f"  {r.branch_name:<20} | {r.tx} tx | EGP {r.total:,.2f}")

conn.close()
