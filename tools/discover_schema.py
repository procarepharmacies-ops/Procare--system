import pyodbc
from datetime import datetime

SERVER   = "DESKTOP-3A9JFL4"
DATABASE = "stock"
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str, timeout=10)
cursor = conn.cursor()

cursor.execute("""
    SELECT t.TABLE_NAME, p.rows AS ROW_COUNT
    FROM INFORMATION_SCHEMA.TABLES t
    JOIN sys.partitions p ON p.object_id = OBJECT_ID(t.TABLE_NAME)
    WHERE t.TABLE_TYPE = 'BASE TABLE' AND p.index_id IN (0,1)
    ORDER BY p.rows DESC
""")
tables = cursor.fetchall()

print("=" * 60)
print("TOP 20 TABLES BY ROW COUNT")
print("=" * 60)
for table, rows in tables[:20]:
    print(f"  {table:<40} {rows:>10,} rows")

key = ['Sales_header','Sales_details','Sales_Detail','Purchase_header',
       'Purchase_details','Products','Items','Branches','Suppliers']
print("\nKEY TABLES FOUND:")
for t, r in tables:
    if any(k.lower() == t.lower() for k in key):
        print(f"  -> {t:<40} {r:>10,} rows")

conn.close()
