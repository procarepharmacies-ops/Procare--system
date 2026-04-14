import pyodbc
from datetime import datetime, timedelta

SERVER="DESKTOP-3A9JFL4"; DATABASE="stock"
conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn=pyodbc.connect(conn_str,timeout=10); cursor=conn.cursor()

# Check last 7 days to find when sales actually exist
cursor.execute("""
    SELECT CAST(bill_date AS DATE) AS day, COUNT(*) AS tx, SUM(total_bill_net) AS total
    FROM Sales_header WHERE back!='Y' AND bill_date >= DATEADD(day,-7,GETDATE())
    GROUP BY CAST(bill_date AS DATE) ORDER BY day DESC
""")
rows=cursor.fetchall()
print("LAST 7 DAYS SALES:")
for r in rows:
    print(f"  {r.day}  |  {r.tx} transactions  |  EGP {r.total:,.2f}")

conn.close()
