import pyodbc
conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-3A9JFL4;DATABASE=stock;Trusted_Connection=yes;')
cursor=conn.cursor()
cursor.execute('SELECT TOP 5 CAST(insert_date AS DATE) AS day, COUNT(*) AS tx, SUM(total_bill_net) AS total FROM Branches_sales_header GROUP BY CAST(insert_date AS DATE) ORDER BY day DESC')
[print(f'  {r.day} | {r.tx} tx | EGP {r.total:,.2f}') for r in cursor.fetchall()]
conn.close()
