import pyodbc
import os
from datetime import datetime

SERVER   = "DESKTOP-3A9JFL4"
DATABASE = "stock"

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

print("=" * 50)
print("ProCare Pharmacy - DB Connection Test")
print(f"Server:   {SERVER}")
print(f"Database: {DATABASE}")
print(f"Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    table_count = cursor.fetchone()[0]
    cursor.execute("SELECT TOP 10 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
    tables = [row[0] for row in cursor.fetchall()]
    print("\nCONNECTION SUCCESSFUL!")
    print(f"Total tables: {table_count}")
    for t in tables:
        print(f"  -> {t}")
    conn.close()
except Exception as e:
    print(f"\nCONNECTION FAILED: {e}")
