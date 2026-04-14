import pyodbc

SERVER="DESKTOP-3A9JFL4"; DATABASE="stock"
conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
conn=pyodbc.connect(conn_str,timeout=10); cursor=conn.cursor()

# Check actual columns in Branches_sales_header
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='Branches_sales_header'
    ORDER BY ORDINAL_POSITION
""")
print("COLUMNS IN Branches_sales_header:")
for r in cursor.fetchall():
    print(f"  {r.COLUMN_NAME} ({r.DATA_TYPE})")

# Peek at 3 real rows
cursor.execute("SELECT TOP 3 * FROM Branches_sales_header")
cols=[d[0] for d in cursor.description]
print(f"\nSAMPLE ROW COLUMNS: {cols}")
rows=cursor.fetchall()
for row in rows:
    for col,val in zip(cols,row):
        print(f"  {col}: {val}")
    print("---")

conn.close()
