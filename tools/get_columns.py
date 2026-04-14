import pyodbc

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

for table in ["Sales_header", "Sales_details", "Products", "Branches", "Purchase_header"]:
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION
    """)
    cols = cursor.fetchall()
    print(f"\n[{table}]")
    for col, dtype in cols:
        print(f"  - {col} ({dtype})")

conn.close()
