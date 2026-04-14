import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()
cursor.execute("""
    SELECT t.TABLE_NAME, p.rows 
    FROM INFORMATION_SCHEMA.TABLES t
    JOIN sys.partitions p ON p.object_id=OBJECT_ID(t.TABLE_NAME)
    WHERE t.TABLE_TYPE='BASE TABLE' AND p.index_id IN(0,1)
    AND (t.TABLE_NAME LIKE '%cash%' OR t.TABLE_NAME LIKE '%financial%' 
    OR t.TABLE_NAME LIKE '%gedo%' OR t.TABLE_NAME LIKE '%purchase%'
    OR t.TABLE_NAME LIKE '%vendor%' OR t.TABLE_NAME LIKE '%money%'
    OR t.TABLE_NAME LIKE '%safe%' OR t.TABLE_NAME LIKE '%fund%')
    ORDER BY p.rows DESC
""")
print("CASH & PURCHASE TABLES:")
for r in cursor.fetchall(): print(f"  {r[0]:<45} {r[1]:>10,} rows")
conn.close()
