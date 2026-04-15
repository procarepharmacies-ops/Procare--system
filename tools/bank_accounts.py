import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()

# All drawer IDs ever used
cursor.execute("""
    SELECT b.branch_name, c.cdc_cash_id, 
           MAX(c.insert_date) AS last_date,
           MAX(c.cdc_curr_cash) AS last_cash
    FROM Branches_Cash_disk_close c
    JOIN Branches b ON b.branch_id=c.branch_id
    GROUP BY b.branch_name, c.branch_id, c.cdc_cash_id
    ORDER BY b.branch_name, c.cdc_cash_id
""")
print("ALL DRAWERS:")
for r in cursor.fetchall():
    print(f"  {r.branch_name:<20} DrawerID:{r.cdc_cash_id}  Last:{str(r.last_date)[:16]}  EGP {r.last_cash:,.2f}")

# Find bank/account tables
cursor.execute("""
    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE='BASE TABLE'
    AND (TABLE_NAME LIKE '%bank%' OR TABLE_NAME LIKE '%account%'
    OR TABLE_NAME LIKE '%depot%' OR TABLE_NAME LIKE '%cheque%'
    OR TABLE_NAME LIKE '%check%' OR TABLE_NAME LIKE '%transfer%')
    ORDER BY TABLE_NAME
""")
print("\nBANK/ACCOUNT TABLES:")
for r in cursor.fetchall(): print(f"  -> {r[0]}")

# Check cash_depots (found earlier - 5 rows)
cursor.execute("SELECT * FROM Cash_depots")
cols=[d[0] for d in cursor.description]
print("\nCASH_DEPOTS TABLE:")
for row in cursor.fetchall():
    for col,val in zip(cols,row):
        if val not in (None,0,'0',''):
            print(f"  {col}: {val}")
    print("---")

# Check Branches_cash_depots (14 rows)
cursor.execute("SELECT * FROM Branches_cash_depots")
cols=[d[0] for d in cursor.description]
print("\nBRANCHES_CASH_DEPOTS TABLE:")
for row in cursor.fetchall():
    for col,val in zip(cols,row):
        if val not in (None,0,'0',''):
            print(f"  {col}: {val}")
    print("---")

conn.close()
