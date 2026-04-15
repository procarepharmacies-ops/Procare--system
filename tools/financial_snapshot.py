"""
tools/financial_snapshot.py
Real financial snapshot from Cash_depots
Classes: 1=POS, 2=Treasury/Safe, 3=Bank Account, 4=Other
READ-ONLY
"""
import pyodbc
from datetime import datetime

conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()

cursor.execute("""
    SELECT b.branch_name, cd.cash_depot_name_ar, cd.cash_depot_name_en,
           cd.cash_depot_class, cd.cash_depot_current_money,
           cd.update_date
    FROM Branches_cash_depots cd
    JOIN Branches b ON b.branch_id=cd.branch_id
    WHERE cd.cash_depot_current_money > 0
    AND cd.cash_depot_name_ar != 'cancel'
    ORDER BY b.branch_name, cd.cash_depot_class, cd.cash_depot_id
""")
rows=cursor.fetchall()
conn.close()

class_names={1:'POS',2:'Treasury/Safe',3:'Bank Account',4:'Other'}
branches={}
for r in rows:
    b=r.branch_name
    if b not in branches: branches[b]=[]
    branches[b].append(r)

print("="*60)
print("PROCARE PHARMACY - FINANCIAL SNAPSHOT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("="*60)
grand_total=0
for branch, accounts in branches.items():
    total=sum(a.cash_depot_current_money or 0 for a in accounts)
    grand_total+=total
    print(f"\n{branch}")
    print(f"{'─'*50}")
    for a in accounts:
        cls=class_names.get(a.cash_depot_class,'Other')
        name=a.cash_depot_name_en or a.cash_depot_name_ar
        updated=str(a.update_date)[:16] if a.update_date else '?'
        print(f"  [{cls:<14}] {name:<20} EGP {a.cash_depot_current_money:>10,.2f}  (updated: {updated})")
    print(f"  {'─'*48}")
    print(f"  {'Branch Total':<36} EGP {total:>10,.2f}")

print(f"\n{'='*60}")
print(f"  {'GRAND TOTAL':<36} EGP {grand_total:>10,.2f}")
print(f"{'='*60}")
