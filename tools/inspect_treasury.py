import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()

for table in ["Gedo_Financial","Branches_Cash_disk_close","Branches_purchase_header","Branch_money_convert"]:
    cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table}' ORDER BY ORDINAL_POSITION")
    cols=cursor.fetchall()
    print(f"\n[{table}]")
    for c in cols: print(f"  - {c[0]} ({c[1]})")

# Sample rows from Gedo_Financial
cursor.execute("SELECT TOP 3 * FROM Gedo_Financial ORDER BY gf_id DESC")
cols=[d[0] for d in cursor.description]
print(f"\nGEDO_FINANCIAL SAMPLE (latest 3 rows):")
for row in cursor.fetchall():
    for col,val in zip(cols,row):
        if val not in (None, 0, '0', ''): print(f"  {col}: {val}")
    print("---")

conn.close()
