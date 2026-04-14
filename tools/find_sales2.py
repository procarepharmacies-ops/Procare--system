import pyodbc

SERVER="DESKTOP-3A9JFL4"; DATABASE="stock"
conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn=pyodbc.connect(conn_str,timeout=10); cursor=conn.cursor()

# Check branches table
cursor.execute("SELECT branch_id, branch_name, branch_ip1, branch_ip2, is_server FROM Branches")
print("BRANCHES:")
for r in cursor.fetchall():
    print(f"  ID:{r.branch_id} | {r.branch_name} | IP:{r.branch_ip1} | Server:{r.is_server}")

# Check Branches_sales_header (has 245,704 rows!)
cursor.execute("""
    SELECT TOP 5 CAST(bill_date AS DATE) AS day, COUNT(*) AS tx, SUM(total_bill_net) AS total
    FROM Branches_sales_header WHERE back!='Y'
    GROUP BY CAST(bill_date AS DATE) ORDER BY day DESC
""")
print("\nBRANCHES_SALES_HEADER (last 5 days):")
for r in cursor.fetchall():
    print(f"  {r.day}  |  {r.tx} tx  |  EGP {r.total:,.2f}")

# Raw count check
cursor.execute("SELECT COUNT(*) FROM Sales_header")
print(f"\nSales_header total rows: {cursor.fetchone()[0]:,}")
cursor.execute("SELECT COUNT(*) FROM Sales_header WHERE bill_date >= DATEADD(month,-1,GETDATE())")
print(f"Sales_header last 30 days: {cursor.fetchone()[0]:,}")

conn.close()
