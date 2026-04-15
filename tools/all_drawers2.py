import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()

# Get all unique drawer IDs per branch with their last known balance
cursor.execute("""
    SELECT b.branch_name, c.cdc_cash_id, 
           MAX(c.insert_date) AS last_date,
           MAX(c.cdc_curr_cash) AS last_cash
    FROM Branches_Cash_disk_close c
    JOIN Branches b ON b.branch_id=c.branch_id
    GROUP BY b.branch_name, c.branch_id, c.cdc_cash_id
    ORDER BY b.branch_name, c.cdc_cash_id
""")
print("ALL DRAWER IDs EVER USED:")
for r in cursor.fetchall():
    print(f"  {r.branch_name:<20} DrawerID:{r.cdc_cash_id}  Last: {str(r.last_date)[:16]}  Cash: EGP {r.last_cash:,.2f}")

conn.close()
