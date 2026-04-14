import pyodbc
from datetime import datetime, timedelta
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()
today=datetime.now().date()

# 1. Cash in treasury RIGHT NOW (current cash per drawer)
cursor.execute("""
    SELECT b.branch_name, 
           SUM(c.cdc_curr_cash) AS current_cash,
           SUM(c.cdc_act_cash)  AS actual_cash,
           COUNT(*)             AS drawers,
           MAX(c.insert_date)   AS last_update
    FROM Branches_Cash_disk_close c
    LEFT JOIN Branches b ON b.branch_id=c.branch_id
    GROUP BY b.branch_name, c.branch_id
    ORDER BY current_cash DESC
""")
print("="*55)
print("TREASURY - CASH IN DRAWERS RIGHT NOW")
print("="*55)
for r in cursor.fetchall():
    print(f"  Branch:       {r.branch_name}")
    print(f"  Current Cash: EGP {r.current_cash:,.2f}")
    print(f"  Actual Cash:  EGP {r.actual_cash:,.2f}")
    print(f"  Drawers:      {r.drawers}")
    print(f"  Last Update:  {r.last_update}")
    print()

# 2. Today's financial movements
cursor.execute("""
    SELECT gf_gedo_type, COUNT(*) AS cnt, SUM(gf_value) AS total
    FROM Gedo_Financial
    WHERE CAST(insert_date AS DATE)=?
    GROUP BY gf_gedo_type ORDER BY total DESC
""", today)
print("="*55)
print(f"TODAY'S FINANCIAL MOVEMENTS ({today})")
print("="*55)
type_names = {1:'Cash In',2:'Cash Out',3:'Expense',4:'Return/Refund',
              5:'Purchase Pay',6:'Transfer',7:'Sale Cash',8:'Deposit',
              9:'Withdrawal',10:'Other',11:'Adjustment',12:'Credit'}
for r in cursor.fetchall():
    name=type_names.get(r.gf_gedo_type, f'Type {r.gf_gedo_type}')
    print(f"  {name:<20} {r.cnt:>5} tx   EGP {r.total:>12,.2f}")

# 3. Today's purchases
cursor.execute("""
    SELECT b.branch_name, COUNT(*) AS bills, SUM(p.total_bill) AS total,
           SUM(p.bill_disc_money) AS disc
    FROM Branches_purchase_header p
    LEFT JOIN Branches b ON b.branch_id=p.branch_id
    WHERE CAST(p.insert_date AS DATE)=?
    AND p.back='0'
    GROUP BY b.branch_name ORDER BY total DESC
""", today)
rows=cursor.fetchall()
print("\n"+"="*55)
print(f"TODAY'S PURCHASES ({today})")
print("="*55)
if rows:
    for r in rows:
        print(f"  {r.branch_name:<20} {r.bills} bills   EGP {r.total:,.2f}  (disc: {r.disc:,.2f})")
else:
    # try last 7 days
    cursor.execute("""
        SELECT CAST(insert_date AS DATE) AS day, COUNT(*) AS bills, SUM(total_bill) AS total
        FROM Branches_purchase_header WHERE back='0'
        GROUP BY CAST(insert_date AS DATE) ORDER BY day DESC
    """)
    rows2=cursor.fetchall()
    print("  No purchases today. Last purchase days:")
    for r in rows2[:5]: print(f"  {r.day}  {r.bills} bills  EGP {r.total:,.2f}")

# 4. Today sales so far
cursor.execute("""
    SELECT b.branch_name, COUNT(*) AS tx, SUM(s.total_bill_net) AS total
    FROM Branches_sales_header s LEFT JOIN Branches b ON b.branch_id=s.branch_id
    WHERE CAST(s.insert_date AS DATE)=?
    GROUP BY b.branch_name ORDER BY total DESC
""", today)
print("\n"+"="*55)
print(f"TODAY'S SALES SO FAR")
print("="*55)
total_today=0
for r in cursor.fetchall():
    print(f"  {r.branch_name:<20} {r.tx} tx   EGP {r.total:,.2f}")
    total_today+=(r.total or 0)
print(f"  {'TOTAL':<20}        EGP {total_today:,.2f}")

conn.close()
