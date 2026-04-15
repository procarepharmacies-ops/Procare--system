import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()

cursor.execute("""
    SELECT b.branch_name, c.cdc_cash_id, c.cdc_curr_cash, c.cdc_act_cash, c.insert_date
    FROM Branches_Cash_disk_close c
    JOIN Branches b ON b.branch_id=c.branch_id
    WHERE c.insert_date IN (
        SELECT MAX(c2.insert_date) FROM Branches_Cash_disk_close c2
        WHERE c2.branch_id=c.branch_id AND c2.cdc_cash_id=c.cdc_cash_id
        GROUP BY c2.cdc_cash_id
    )
    ORDER BY b.branch_name, c.cdc_cash_id
""")
print("ALL DRAWERS - LATEST BALANCE:")
for r in cursor.fetchall():
    print(f"  {r.branch_name:<20} DrawerID:{r.cdc_cash_id}  Current: EGP {r.cdc_curr_cash:,.2f}  Actual: EGP {r.cdc_act_cash:,.2f}  Date: {str(r.insert_date)[:16]}")

conn.close()
