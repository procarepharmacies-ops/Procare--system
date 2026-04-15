"""
app.py - ProCare Pharmacy Intelligence API
Flask server that connects to ProCare Stock SQL Server
and serves live data to the dashboard
READ-ONLY - Never writes to database
Run: py app.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import pyodbc
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='dashboard')
CORS(app)

# ── DB Connection ─────────────────────────────────────
def get_conn():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-3A9JFL4;'
        'DATABASE=stock;'
        'Trusted_Connection=yes;',
        timeout=10
    )

# ── Dashboard HTML ────────────────────────────────────
@app.route('/')
def dashboard():
    return send_from_directory('dashboard', 'index.html')

# ── API: Summary ──────────────────────────────────────
@app.route('/api/summary')
def api_summary():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Today sales
        cursor.execute("""
            SELECT COUNT(*) AS tx, ISNULL(SUM(total_bill_net),0) AS total
            FROM Branches_sales_header
            WHERE CAST(insert_date AS DATE)=?
        """, today)
        r = cursor.fetchone()
        today_tx    = int(r.tx)
        today_sales = float(r.total)

        # Yesterday sales
        cursor.execute("""
            SELECT COUNT(*) AS tx, ISNULL(SUM(total_bill_net),0) AS total
            FROM Branches_sales_header
            WHERE CAST(insert_date AS DATE)=?
        """, yesterday)
        r = cursor.fetchone()
        yest_sales = float(r.total)
        yest_tx    = int(r.tx)

        # Expiry count
        cursor.execute("""
            SELECT COUNT(*) FROM Product_Amount pa
            JOIN Products p ON p.product_id=pa.product_id
            WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,60,GETDATE())
            AND pa.amount>0 AND p.deleted!='Y'
        """)
        expiry_count = int(cursor.fetchone()[0])

        # Treasury total — real current balances from Cash_depots
        cursor.execute("""
            SELECT ISNULL(SUM(cash_depot_current_money),0)
            FROM Branches_cash_depots
            WHERE cash_depot_name_ar != 'cancel'
            AND ISNULL(cash_depot_current_money,0) > 0
        """)
        treasury = float(cursor.fetchone()[0])

        conn.close()
        return jsonify({
            'today_sales':   today_sales,
            'today_tx':      today_tx,
            'yesterday_sales': yest_sales,
            'yesterday_tx':  yest_tx,
            'expiry_alerts': expiry_count,
            'treasury_total': treasury,
            'generated_at':  datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Branches ─────────────────────────────────────
@app.route('/api/branches')
def api_branches():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        yesterday = datetime.now().date() - timedelta(days=1)

        cursor.execute("""
            SELECT b.branch_name,
                   COUNT(s.sales_id)           AS tx,
                   ISNULL(SUM(s.total_bill_net),0) AS total,
                   ISNULL(SUM(s.total_disc_money),0) AS disc
            FROM Branches_sales_header s
            LEFT JOIN Branches b ON b.branch_id=s.branch_id
            WHERE CAST(s.insert_date AS DATE)=?
            GROUP BY b.branch_name ORDER BY total DESC
        """, yesterday)
        rows = cursor.fetchall()
        conn.close()

        total = sum(float(r.total) for r in rows)
        branches = []
        for r in rows:
            val = float(r.total)
            branches.append({
                'name':    r.branch_name or 'Branch',
                'tx':      int(r.tx),
                'total':   val,
                'disc':    float(r.disc),
                'share':   round(val/total*100, 1) if total > 0 else 0
            })
        return jsonify({'branches': branches, 'total': total, 'date': str(yesterday)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Weekly ───────────────────────────────────────
@app.route('/api/weekly')
def api_weekly():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 7
                CAST(insert_date AS DATE) AS day,
                COUNT(*) AS tx,
                ISNULL(SUM(total_bill_net),0) AS total
            FROM Branches_sales_header
            WHERE insert_date >= DATEADD(day,-7,GETDATE())
            GROUP BY CAST(insert_date AS DATE)
            ORDER BY day ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({
            'days': [str(r.day) for r in rows],
            'sales': [float(r.total) for r in rows],
            'transactions': [int(r.tx) for r in rows],
            'week_total': sum(float(r.total) for r in rows),
            'week_tx': sum(int(r.tx) for r in rows)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Treasury ─────────────────────────────────────
@app.route('/api/treasury')
def api_treasury():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        # Use Branches_cash_depots — real current balances
        # class: 1=POS, 2=Treasury/Safe, 3=Bank Account, 4=Other
        cursor.execute("""
            SELECT b.branch_name, b.branch_id,
                   cd.cash_depot_name_ar, cd.cash_depot_name_en,
                   cd.cash_depot_class,
                   ISNULL(cd.cash_depot_current_money,0) AS balance,
                   cd.update_date
            FROM Branches_cash_depots cd
            JOIN Branches b ON b.branch_id=cd.branch_id
            WHERE ISNULL(cd.cash_depot_current_money,0) >= 0
            AND cd.cash_depot_name_ar != 'cancel'
            ORDER BY b.branch_name, cd.cash_depot_class, cd.cash_depot_id
        """)
        rows = cursor.fetchall()
        conn.close()

        class_names = {1:'POS', 2:'Treasury', 3:'Bank', 4:'Other'}
        branches = {}
        for r in rows:
            b = r.branch_name or 'Branch'
            if b not in branches:
                branches[b] = {'branch': b, 'accounts': [], 'total': 0}
            bal = float(r.balance)
            branches[b]['accounts'].append({
                'name':    r.cash_depot_name_en or r.cash_depot_name_ar or '?',
                'name_ar': r.cash_depot_name_ar or '',
                'type':    class_names.get(r.cash_depot_class, 'Other'),
                'class':   r.cash_depot_class,
                'balance': bal,
                'updated': str(r.update_date)[:16] if r.update_date else ''
            })
            branches[b]['total'] += bal

        result = list(branches.values())
        grand_total = sum(b['total'] for b in result)
        return jsonify({
            'branches': result,
            'grand_total': grand_total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Expiry ───────────────────────────────────────
@app.route('/api/expiry')
def api_expiry():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 15
                p.product_name_ar, p.product_name_en,
                pa.exp_date, pa.amount,
                DATEDIFF(day, GETDATE(), pa.exp_date) AS days_left
            FROM Product_Amount pa
            JOIN Products p ON p.product_id=pa.product_id
            WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,60,GETDATE())
            AND pa.amount>=0 AND p.deleted!='Y'
            ORDER BY pa.exp_date ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'items': [{
            'name_ar':   r.product_name_ar or '',
            'name_en':   r.product_name_en or '',
            'exp_date':  str(r.exp_date)[:10] if r.exp_date else '',
            'qty':       float(r.amount),
            'days_left': int(r.days_left),
            'urgent':    int(r.days_left) <= 14
        } for r in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Top Products ─────────────────────────────────
@app.route('/api/top_products')
def api_top_products():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        yesterday = datetime.now().date() - timedelta(days=1)
        cursor.execute("""
            SELECT TOP 5
                p.product_name_ar, p.product_name_en,
                SUM(d.amount) AS qty,
                ISNULL(SUM(d.total_sell),0) AS revenue
            FROM Branches_sales_details d
            JOIN Branches_sales_header s ON s.sales_id=d.sales_id AND s.branch_id=d.branch_id
            JOIN Products p ON p.product_id=d.product_id
            WHERE CAST(s.insert_date AS DATE)=?
            GROUP BY p.product_name_ar, p.product_name_en
            ORDER BY revenue DESC
        """, yesterday)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'products': [{
            'name':    r.product_name_ar or r.product_name_en or 'Unknown',
            'qty':     float(r.qty),
            'revenue': float(r.revenue)
        } for r in rows], 'date': str(yesterday)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Purchases ────────────────────────────────────
@app.route('/api/purchases')
def api_purchases():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 7
                CAST(insert_date AS DATE) AS day,
                COUNT(*) AS bills,
                ISNULL(SUM(total_bill),0) AS total
            FROM Branches_purchase_header
            WHERE back='0' AND insert_date >= DATEADD(day,-7,GETDATE())
            GROUP BY CAST(insert_date AS DATE)
            ORDER BY day DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'purchases': [{
            'day':   str(r.day),
            'bills': int(r.bills),
            'total': float(r.total)
        } for r in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Health Check ─────────────────────────────────
@app.route('/api/health')
def api_health():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Branches")
        branches = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            'status':   'ok',
            'database': 'connected',
            'branches': branches,
            'time':     datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("="*55)
    print("  ProCare Pharmacy Intelligence API")
    print("  http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("="*55)
    app.run(debug=False, host='0.0.0.0', port=5000)
