"""
app.py - ProCare Pharmacy Intelligence API
Flask server that connects to ProCare Stock SQL Server
and serves live data to the dashboard
READ-ONLY - Never writes to database
Run: py app.py
Open: http://localhost:5000
"""

from flask import Flask, jsonify, render_template_string, send_from_directory, request
from flask_cors import CORS
import pyodbc
from datetime import datetime, timedelta
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
from slack_client import SlackMessenger

app = Flask(__name__, static_folder='dashboard')
CORS(app)

# ── Slack Messenger ───────────────────────────────────
try:
    slack_messenger = SlackMessenger()
    slack_enabled = slack_messenger.test_connection()
    if slack_enabled:
        print("✅ Slack integration enabled")
    else:
        print("⚠️  Slack connection test failed")
except Exception as e:
    print(f"⚠️  Slack disabled: {e}")
    slack_messenger = None
    slack_enabled = False

# ── Login Protection ─────────────────────────────────
from functools import wraps
from flask import request, session, redirect

app.secret_key = 'procare2026secure'
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'procare2026')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form.get('password') == DASHBOARD_PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        error = 'Wrong password'
    err_html = f'<div style="color:#ff4d6d;font-size:12px;margin-bottom:12px;">{error}</div>' if error else ""
    return f"""<!DOCTYPE html><html><head><title>ProCare Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
    <style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#080f1a;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'DM Sans',sans-serif}}
    .box{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:40px;width:340px;text-align:center}}
    .logo{{font-family:'Syne',sans-serif;font-size:24px;font-weight:700;color:#00d4a8;margin-bottom:8px}}
    .sub{{font-size:12px;color:rgba(232,240,254,0.4);letter-spacing:2px;text-transform:uppercase;margin-bottom:32px}}
    input{{width:100%;padding:12px 16px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#e8f0fe;font-size:14px;outline:none;margin-bottom:12px}}
    button{{width:100%;padding:12px;background:rgba(0,212,168,0.15);border:1px solid rgba(0,212,168,0.3);color:#00d4a8;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer}}</style></head>
    <body><div class="box"><div class="logo">ProCare</div><div class="sub">Intelligence Dashboard</div>
    <form method="post">{err_html}<input type="password" name="password" placeholder="Enter password" autofocus>
    <button type="submit">Access Dashboard</button></form></div></body></html>"""

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ── DB Connection ─────────────────────────────────────
def get_conn():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-3A9JFL4;'
        'DATABASE=stock;'
        'Trusted_Connection=yes;',
        timeout=10
    )


# ── Filter helpers ───────────────────────────────────
# Maps the branch keyword from the URL to LIKE patterns for Branches.branch_name
# (eStock stores names in Arabic — we accept Arabic or English keywords just in case).
BRANCH_PATTERNS = {
    'elsanta': ['%السنطة%', '%Elsanta%', '%santa%'],
    'mashala': ['%مسهل%',  '%Mashala%', '%mashal%'],
}

def _parse_iso(s):
    """Parse YYYY-MM-DD or return None."""
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def get_filters():
    """
    Read ?from=&to=&branch= from the current request and return a normalized
    dict the endpoints can splice into their SQL.

    Returns:
        {
            'from':         date,
            'to':           date,
            'range_label':  'Today' | 'Yesterday' | 'Last 7 days' | 'This month' | '2026-04-01 → 2026-04-15',
            'branch_key':   'all' | 'elsanta' | 'mashala',
            'branch_sql':   ' AND (b.branch_name LIKE ? OR ...)' or '',
            'branch_params': [..],   # patterns for the placeholders
        }
    """
    from flask import request as _req
    today = datetime.now().date()

    f = _parse_iso(_req.args.get('from'))
    t = _parse_iso(_req.args.get('to'))
    range_kw = (_req.args.get('range') or '').lower()

    # Map range keyword if explicit dates weren't provided
    if not f or not t:
        if range_kw == 'today':
            f = t = today
        elif range_kw == 'yesterday':
            f = t = today - timedelta(days=1)
        elif range_kw == 'week':
            f = today - timedelta(days=6); t = today  # 7 days inclusive
        elif range_kw == 'month':
            f = today.replace(day=1); t = today
        else:
            f = t = today  # safe default — preserves old single-day behavior

    if f > t:
        f, t = t, f  # swap if reversed

    # Friendly label
    if f == t == today:                                 label = 'Today'
    elif f == t == today - timedelta(days=1):           label = 'Yesterday'
    elif f == today - timedelta(days=6) and t == today: label = 'Last 7 days'
    elif f == today.replace(day=1) and t == today:      label = 'This month'
    else:                                               label = f'{f} → {t}'

    # Branch filter
    branch_kw     = (_req.args.get('branch') or 'all').lower()
    branch_sql    = ''
    branch_params = []
    patterns = BRANCH_PATTERNS.get(branch_kw)
    if patterns:
        branch_sql    = ' AND (' + ' OR '.join(['b.branch_name LIKE ?'] * len(patterns)) + ')'
        branch_params = patterns

    return {
        'from':          f,
        'to':            t,
        'range_label':   label,
        'branch_key':    branch_kw if patterns else 'all',
        'branch_sql':    branch_sql,
        'branch_params': branch_params,
    }

# ── Dashboard HTML ────────────────────────────────────
@app.route('/')
@login_required
def dashboard():
    return send_from_directory('dashboard', 'index.html')

# ── API: Summary (CEO Hero — extended with YoY, Outlook, Profit, Customers, Cash) ─
@app.route('/api/summary')
def api_summary():
    """
    Hero KPIs for the CEO dashboard.
    Backwards-compatible: keeps original keys, adds new ones.
    All numbers safe-defaulted to 0 so the frontend never crashes.
    """
    try:
        import calendar
        conn = get_conn()
        cursor = conn.cursor()
        now            = datetime.now()
        today          = now.date()
        yesterday      = today - timedelta(days=1)
        last_week_same = today - timedelta(days=7)
        last_year_same = today.replace(year=today.year - 1)
        first_of_month = today.replace(day=1)
        days_in_month  = calendar.monthrange(today.year, today.month)[1]
        day_of_month   = today.day

        # Read filter bar selection (range + branch)
        flt = get_filters()

        def sales_for(day):
            cursor.execute("""
                SELECT COUNT(*) AS tx,
                       ISNULL(SUM(total_bill_net),0) AS total,
                       COUNT(DISTINCT NULLIF(LTRIM(RTRIM(ISNULL(cust_name,''))),'')) AS customers
                FROM Branches_sales_header s
                LEFT JOIN Branches b ON b.branch_id = s.branch_id
                WHERE CAST(s.insert_date AS DATE) = ?
            """ + flt['branch_sql'], [day] + flt['branch_params'])
            r = cursor.fetchone()
            return int(r.tx or 0), float(r.total or 0), int(r.customers or 0)

        def sales_in_range(d_from, d_to):
            cursor.execute("""
                SELECT COUNT(*) AS tx,
                       ISNULL(SUM(total_bill_net),0) AS total,
                       COUNT(DISTINCT NULLIF(LTRIM(RTRIM(ISNULL(cust_name,''))),'')) AS customers
                FROM Branches_sales_header s
                LEFT JOIN Branches b ON b.branch_id = s.branch_id
                WHERE s.insert_date >= ? AND s.insert_date < DATEADD(day,1,?)
            """ + flt['branch_sql'], [d_from, d_to] + flt['branch_params'])
            r = cursor.fetchone()
            return int(r.tx or 0), float(r.total or 0), int(r.customers or 0)

        # Same-day comparisons (always fixed reference points — independent of range)
        today_tx, today_sales, today_customers = sales_for(today)
        yest_tx,  yest_sales,  _               = sales_for(yesterday)
        lw_tx,    lw_sales,    _               = sales_for(last_week_same)
        ly_tx,    ly_sales,    _               = sales_for(last_year_same)

        # Range aggregate (honors the filter bar's range + branch selection)
        range_tx, range_sales, range_customers = sales_in_range(flt['from'], flt['to'])

        # Month-to-date sales + projected end-of-month (linear projection)
        cursor.execute("""
            SELECT ISNULL(SUM(total_bill_net),0) AS mtd
            FROM Branches_sales_header
            WHERE insert_date >= ? AND insert_date < DATEADD(day,1,?)
        """, first_of_month, today)
        mtd_sales = float(cursor.fetchone().mtd or 0)
        # Projection = MTD ÷ days_elapsed × days_in_month  (today still in progress, count it)
        days_elapsed = max(day_of_month, 1)
        monthly_outlook = (mtd_sales / days_elapsed) * days_in_month if days_elapsed > 0 else 0

        # Today purchases (cost of goods received today)
        cursor.execute("""
            SELECT ISNULL(SUM(total_bill),0) AS total
            FROM Branches_purchase_header
            WHERE back='0' AND CAST(insert_date AS DATE)=?
        """, today)
        today_purchases = float(cursor.fetchone().total or 0)

        # Today financial movements: cash in, cash out, expenses (best effort — table may differ)
        today_cash_in = today_cash_out = today_expenses = 0.0
        try:
            cursor.execute("""
                SELECT gf_gedo_type, ISNULL(SUM(gf_value),0) AS total
                FROM Gedo_Financial
                WHERE CAST(insert_date AS DATE)=?
                GROUP BY gf_gedo_type
            """, today)
            for r in cursor.fetchall():
                t = int(r.gf_gedo_type or 0); v = float(r.total or 0)
                if t == 1: today_cash_in  = v          # 1 = Cash In
                elif t == 2: today_cash_out = v        # 2 = Cash Out
                elif t == 3: today_expenses = v        # 3 = Expense
        except Exception:
            pass  # table or column name differs in some installs — non-fatal

        # Rough net daily profit estimate (sales − purchases − expenses)
        today_profit_est = today_sales - today_purchases - today_expenses

        # Expiry count (next 60 days)
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

        # Helper: % change vs reference (None when reference is 0 to avoid div-by-zero noise)
        def pct(curr, ref):
            if not ref:
                return None
            return round((curr - ref) / ref * 100, 1)

        conn.close()
        return jsonify({
            # — original fields (DON'T REMOVE — frontend depends on them) —
            'today_sales':       today_sales,
            'today_tx':          today_tx,
            'yesterday_sales':   yest_sales,
            'yesterday_tx':      yest_tx,
            'expiry_alerts':     expiry_count,
            'treasury_total':    treasury,
            'generated_at':      now.strftime('%H:%M:%S'),

            # — new CEO hero fields —
            'today_customers':   today_customers,
            'today_purchases':   today_purchases,
            'today_expenses':    today_expenses,
            'today_profit_est':  today_profit_est,
            'today_cash_in':     today_cash_in,
            'today_cash_out':    today_cash_out,

            # comparisons
            'last_week_sales':   lw_sales,
            'last_week_tx':      lw_tx,
            'last_year_sales':   ly_sales,
            'last_year_tx':      ly_tx,
            'pct_vs_yesterday':  pct(today_sales, yest_sales),
            'pct_vs_last_week':  pct(today_sales, lw_sales),
            'pct_vs_last_year':  pct(today_sales, ly_sales),

            # monthly outlook
            'mtd_sales':         mtd_sales,
            'monthly_outlook':   monthly_outlook,
            'day_of_month':      day_of_month,
            'days_in_month':     days_in_month,
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

# ── API: Top Products (date=today|yesterday|YYYY-MM-DD, default=yesterday, limit=5) ─
@app.route('/api/top_products')
def api_top_products():
    try:
        from flask import request as _req
        date_arg = (_req.args.get('date') or 'yesterday').lower()
        try:
            limit = max(1, min(50, int(_req.args.get('limit', 5))))
        except ValueError:
            limit = 5

        if date_arg == 'today':
            target = datetime.now().date()
        elif date_arg == 'yesterday':
            target = datetime.now().date() - timedelta(days=1)
        else:
            try:
                target = datetime.strptime(date_arg, '%Y-%m-%d').date()
            except ValueError:
                target = datetime.now().date() - timedelta(days=1)

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT TOP {limit}
                p.product_name_ar, p.product_name_en,
                SUM(d.amount) AS qty,
                ISNULL(SUM(d.total_sell),0) AS revenue
            FROM Branches_sales_details d
            JOIN Branches_sales_header s ON s.sales_id=d.sales_id AND s.branch_id=d.branch_id
            JOIN Products p ON p.product_id=d.product_id
            WHERE CAST(s.insert_date AS DATE)=?
            GROUP BY p.product_name_ar, p.product_name_en
            ORDER BY revenue DESC
        """, target)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'products': [{
            'name':    r.product_name_ar or r.product_name_en or 'Unknown',
            'qty':     float(r.qty or 0),
            'revenue': float(r.revenue or 0)
        } for r in rows], 'date': str(target)})
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

# ── API: Slack Test ──────────────────────────────────
@app.route('/api/slack/test', methods=['GET'])
def api_slack_test():
    if not slack_enabled:
        return jsonify({'status': 'disabled', 'message': 'Slack not configured'}), 503
    try:
        if slack_messenger.send_message("🧪 ProCare Slack integration test"):
            return jsonify({'status': 'ok', 'message': 'Test message sent to Slack'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send test message'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ── API: Send Daily Report to Slack ────────────────
@app.route('/api/slack/daily-report', methods=['POST'])
def api_slack_daily_report():
    if not slack_enabled:
        return jsonify({'status': 'disabled', 'message': 'Slack not configured'}), 503
    try:
        data = request.get_json() or {}
        branches = data.get('branches', [])
        top_products = data.get('top_products', [])
        expiry_items = data.get('expiry_items', [])
        total_sales = data.get('total_sales', 0)
        total_tx = data.get('total_tx', 0)
        report_date = data.get('report_date', datetime.now().strftime('%Y-%m-%d'))

        if slack_messenger.send_daily_report(
            branches=branches,
            top_products=top_products,
            expiry_items=expiry_items,
            total_sales=total_sales,
            total_tx=total_tx,
            report_date=report_date
        ):
            return jsonify({'status': 'ok', 'message': 'Daily report sent to Slack'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send report'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ── API: Send Expiry Alert to Slack ────────────────
@app.route('/api/slack/expiry-alert', methods=['POST'])
def api_slack_expiry_alert():
    if not slack_enabled:
        return jsonify({'status': 'disabled', 'message': 'Slack not configured'}), 503
    try:
        data = request.get_json() or {}
        product_name = data.get('product_name', 'Unknown')
        days_left = int(data.get('days_left', 0))
        qty = float(data.get('qty', 0))
        exp_date = data.get('exp_date', '')

        if slack_messenger.send_expiry_alert(
            product_name=product_name,
            days_left=days_left,
            qty=qty,
            exp_date=exp_date
        ):
            return jsonify({'status': 'ok', 'message': 'Expiry alert sent to Slack'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send alert'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ── API: Send Low Stock Alert to Slack ─────────────
@app.route('/api/slack/low-stock-alert', methods=['POST'])
def api_slack_low_stock_alert():
    if not slack_enabled:
        return jsonify({'status': 'disabled', 'message': 'Slack not configured'}), 503
    try:
        data = request.get_json() or {}
        product_name = data.get('product_name', 'Unknown')
        current_qty = float(data.get('current_qty', 0))
        reorder_point = int(data.get('reorder_point', 0))
        branch = data.get('branch', 'Unknown')

        if slack_messenger.send_low_stock_alert(
            product_name=product_name,
            current_qty=current_qty,
            reorder_point=reorder_point,
            branch=branch
        ):
            return jsonify({'status': 'ok', 'message': 'Low stock alert sent to Slack'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send alert'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
            'slack':    'connected' if slack_enabled else 'disconnected',
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

# ── API: Suppliers ────────────────────────────────────
@app.route('/api/suppliers')
def api_suppliers():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 10
                v.vendor_name, COUNT(p.purchase_id) AS bills,
                ISNULL(SUM(p.total_bill),0) AS total_spend,
                MAX(p.insert_date) AS last_order
            FROM Branches_purchase_header p
            JOIN Gedo_Vendors v ON v.vendor_id=p.vendor_id
            WHERE p.back='0'
            GROUP BY v.vendor_name ORDER BY total_spend DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'suppliers': [{
            'name':       r.vendor_name or 'Unknown',
            'bills':      int(r.bills),
            'total_spend': float(r.total_spend),
            'last_order': str(r.last_order)[:10] if r.last_order else ''
        } for r in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── API: Slack Alert ──────────────────────────────────
@app.route('/api/send_alert', methods=['POST'])
def api_send_alert():
    try:
        from datetime import timedelta
        conn = get_conn()
        cursor = conn.cursor()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        cursor.execute("""
            SELECT b.branch_name, COUNT(*) AS tx, ISNULL(SUM(s.total_bill_net),0) AS total
            FROM Branches_sales_header s LEFT JOIN Branches b ON b.branch_id=s.branch_id
            WHERE CAST(s.insert_date AS DATE)=? GROUP BY b.branch_name ORDER BY total DESC
        """, yesterday)
        branches = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) FROM Product_Amount pa JOIN Products p ON p.product_id=pa.product_id
            WHERE pa.exp_date BETWEEN GETDATE() AND DATEADD(day,60,GETDATE())
            AND pa.amount>0 AND p.deleted!='Y'
        """)
        expiry_count = int(cursor.fetchone()[0])

        cursor.execute("""
            SELECT ISNULL(SUM(cash_depot_current_money),0) FROM Branches_cash_depots
            WHERE cash_depot_name_ar!='cancel' AND ISNULL(cash_depot_current_money,0)>0
        """)
        treasury = float(cursor.fetchone()[0])
        conn.close()

        total = sum(float(r.total) for r in branches)
        total_tx = sum(int(r.tx) for r in branches)
        branch_lines = "\n".join(f"  {r.branch_name}: EGP {float(r.total):,.0f} ({r.tx} tx)" for r in branches)

        msg = f"""ProCare Pharmacy Daily Report
{yesterday.strftime('%A, %d %B %Y')}
{'='*40}
SALES: EGP {total:,.0f} ({total_tx} tx)
{branch_lines}
TREASURY: EGP {treasury:,.0f}
EXPIRY ALERTS: {expiry_count} items
{'='*40}
Dashboard: https://dashboard.prospices.net"""

        slack_token = os.getenv("SLACK_BOT_TOKEN", "")
        if slack_token:
            import urllib.request as ur
            payload = json.dumps({"channel": "C0AAAQL6QNB", "text": msg}).encode()
            req = ur.Request("https://slack.com/api/chat.postMessage", data=payload,
                headers={"Authorization": f"Bearer {slack_token}", "Content-Type": "application/json"})
            res = json.loads(ur.urlopen(req).read())
            return jsonify({'ok': res.get('ok'), 'message': msg})
        return jsonify({'ok': False, 'error': 'No SLACK_BOT_TOKEN in environment'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ══════════════════════════════════════════════════════
# EXTENDED API — 11 MODULE PAGES
# ══════════════════════════════════════════════════════

# ── Products Page ─────────────────────────────────────
@app.route('/api/products')
def api_products():
    try:
        conn = get_conn(); cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 50 p.product_name_ar, p.product_name_en,
                   p.sell_price, p.buy_price,
                   ISNULL(pa.amount,0) AS stock,
                   p.product_has_expire,
                   (p.sell_price - p.buy_price) AS profit,
                   CASE WHEN p.buy_price>0 THEN ROUND((p.sell_price-p.buy_price)/p.buy_price*100,1) ELSE 0 END AS margin_pct
            FROM Products p
            LEFT JOIN (SELECT product_id, SUM(amount) AS amount FROM Product_Amount GROUP BY product_id) pa ON pa.product_id=p.product_id
            WHERE p.deleted!='Y' AND p.active='Y' AND p.sell_price>0
            ORDER BY margin_pct DESC
        """)
        rows = cursor.fetchall()

        # Stats
        cursor.execute("SELECT COUNT(*) FROM Products WHERE deleted!='Y' AND active='Y'")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT product_id) FROM Product_Amount WHERE amount<=0")
        zero = cursor.fetchone()[0]
        cursor.execute("""
            SELECT AVG(CASE WHEN buy_price>0 THEN (sell_price-buy_price)/buy_price*100.0 ELSE NULL END)
            FROM Products WHERE deleted!='Y' AND sell_price>0 AND buy_price>0
        """)
        avg_margin = float(cursor.fetchone()[0] or 0)
        conn.close()
        return jsonify({
            'stats': {'total': total, 'zero_stock': zero, 'avg_margin': round(avg_margin,1)},
            'products': [{'name': r.product_name_ar or r.product_name_en,
                          'sell_price': float(r.sell_price or 0), 'buy_price': float(r.buy_price or 0),
                          'stock': float(r.stock or 0), 'profit': float(r.profit or 0),
                          'margin_pct': float(r.margin_pct or 0)} for r in rows]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── Sales Intelligence ────────────────────────────────
@app.route('/api/sales_intelligence')
def api_sales_intelligence():
    try:
        conn = get_conn(); cursor = conn.cursor()
        # Monthly sales last 12 months
        cursor.execute("""
            SELECT YEAR(insert_date) AS yr, MONTH(insert_date) AS mo,
                   COUNT(*) AS tx, SUM(total_bill_net) AS total
            FROM Branches_sales_header
            WHERE insert_date >= DATEADD(month,-12,GETDATE())
            GROUP BY YEAR(insert_date), MONTH(insert_date)
            ORDER BY yr, mo
        """)
        monthly = cursor.fetchall()

        # Top customers
        cursor.execute("""
            SELECT TOP 10 cust_name, COUNT(*) AS visits, SUM(total_bill_net) AS spent
            FROM Branches_sales_header
            WHERE cust_name IS NOT NULL AND cust_name!=''
            AND insert_date >= DATEADD(month,-3,GETDATE())
            GROUP BY cust_name ORDER BY spent DESC
        """)
        customers = cursor.fetchall()

        # Peak hours
        cursor.execute("""
            SELECT DATEPART(hour, insert_date) AS hr, COUNT(*) AS tx
            FROM Branches_sales_header
            WHERE insert_date >= DATEADD(day,-30,GETDATE())
            GROUP BY DATEPART(hour, insert_date) ORDER BY hr
        """)
        hours = cursor.fetchall()

        # Peak days of week
        cursor.execute("""
            SELECT DATEPART(weekday, insert_date) AS wd,
                   DATENAME(weekday, insert_date) AS day_name,
                   COUNT(*) AS tx, AVG(total_bill_net) AS avg_sale
            FROM Branches_sales_header
            WHERE insert_date >= DATEADD(month,-3,GETDATE())
            GROUP BY DATEPART(weekday,insert_date), DATENAME(weekday,insert_date)
            ORDER BY wd
        """)
        weekdays = cursor.fetchall()
        conn.close()

        import calendar
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        return jsonify({
            'monthly': [{'label': f"{month_names[r.mo-1]} {r.yr}", 'tx': int(r.tx), 'total': float(r.total)} for r in monthly],
            'customers': [{'name': r.cust_name, 'visits': int(r.visits), 'spent': float(r.spent)} for r in customers],
            'peak_hours': [{'hour': int(r.hr), 'tx': int(r.tx)} for r in hours],
            'weekdays': [{'day': r.day_name, 'tx': int(r.tx), 'avg': float(r.avg_sale or 0)} for r in weekdays]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── Smart Purchase Order Engine ───────────────────────
@app.route('/api/smart_order')
def api_smart_order():
    try:
        conn = get_conn(); cursor = conn.cursor()

        # Step 1: Products sold in last 7 days with current stock
        cursor.execute("""
            SELECT
                p.product_id, p.product_name_ar, p.product_name_en,
                p.buy_price, p.sell_price,
                ISNULL(SUM(pa.amount),0) AS current_stock,

                -- Daily avg sales last 7 days
                ISNULL((
                    SELECT SUM(d2.amount)/7.0
                    FROM Branches_sales_details d2
                    JOIN Branches_sales_header s2 ON s2.sales_id=d2.sales_id AND s2.branch_id=d2.branch_id
                    WHERE d2.product_id=p.product_id
                    AND s2.insert_date >= DATEADD(day,-7,GETDATE())
                ),0) AS avg_daily_7d,

                -- Daily avg sales last 90 days (seasonality base)
                ISNULL((
                    SELECT SUM(d3.amount)/90.0
                    FROM Branches_sales_details d3
                    JOIN Branches_sales_header s3 ON s3.sales_id=d3.sales_id AND s3.branch_id=d3.branch_id
                    WHERE d3.product_id=p.product_id
                    AND s3.insert_date >= DATEADD(day,-90,GETDATE())
                ),0) AS avg_daily_90d,

                -- Best supplier
                (
                    SELECT TOP 1 v.vendor_name
                    FROM Branches_purchase_details pd2
                    JOIN Branches_purchase_header ph2 ON ph2.purchase_id=pd2.purchase_id AND ph2.branch_id=pd2.branch_id
                    JOIN Gedo_Vendors v ON v.vendor_id=ph2.vendor_id
                    WHERE pd2.product_id=p.product_id AND ph2.back='0'
                    GROUP BY v.vendor_name ORDER BY COUNT(*) DESC
                ) AS best_supplier,

                -- Last purchase price
                (
                    SELECT TOP 1 pd3.buy_price
                    FROM Branches_purchase_details pd3
                    JOIN Branches_purchase_header ph3 ON ph3.purchase_id=pd3.purchase_id AND ph3.branch_id=pd3.branch_id
                    WHERE pd3.product_id=p.product_id AND ph3.back='0'
                    ORDER BY ph3.insert_date DESC
                ) AS last_buy_price

            FROM Products p
            LEFT JOIN Product_Amount pa ON pa.product_id=p.product_id
            WHERE p.deleted!='Y' AND p.active='Y'
            GROUP BY p.product_id, p.product_name_ar, p.product_name_en, p.buy_price, p.sell_price
            HAVING ISNULL(SUM(pa.amount),0) <= 0
               OR ISNULL((
                    SELECT SUM(d2.amount)/7.0 FROM Branches_sales_details d2
                    JOIN Branches_sales_header s2 ON s2.sales_id=d2.sales_id AND s2.branch_id=d2.branch_id
                    WHERE d2.product_id=p.product_id AND s2.insert_date>=DATEADD(day,-7,GETDATE())
                  ),0) > 0
            ORDER BY avg_daily_7d DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        orders = []
        for r in rows:
            stock = float(r.current_stock or 0)
            avg7  = float(r.avg_daily_7d or 0)
            avg90 = float(r.avg_daily_90d or 0)
            if avg7 <= 0 and avg90 <= 0: continue

            # Use higher of 7d or 90d avg (seasonality)
            daily_demand = max(avg7, avg90 * 1.1) if avg7 > avg90 else avg7

            # 7-day stock target
            target_stock = daily_demand * 7
            order_qty = max(0, target_stock - stock)
            if order_qty < 1: continue

            buy_price = float(r.last_buy_price or r.buy_price or 0)
            sell_price = float(r.sell_price or 0)
            margin = round((sell_price - buy_price) / buy_price * 100, 1) if buy_price > 0 else 0

            # Priority: 0 stock = URGENT, <3 days = HIGH, <7 days = MEDIUM
            days_left = stock / daily_demand if daily_demand > 0 else 999
            if stock <= 0: priority = 'URGENT'
            elif days_left < 3: priority = 'HIGH'
            elif days_left < 7: priority = 'MEDIUM'
            else: priority = 'LOW'

            orders.append({
                'name':          r.product_name_ar or r.product_name_en or '?',
                'current_stock': round(stock, 1),
                'daily_demand':  round(daily_demand, 2),
                'days_left':     round(days_left, 1) if days_left < 999 else 0,
                'order_qty':     round(order_qty),
                'target_stock':  round(target_stock),
                'buy_price':     buy_price,
                'order_cost':    round(order_qty * buy_price, 2),
                'margin_pct':    margin,
                'supplier':      r.best_supplier or 'Unknown',
                'priority':      priority
            })

        # Sort by priority
        priority_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        orders.sort(key=lambda x: (priority_order.get(x['priority'], 4), -x['daily_demand']))

        total_cost = sum(o['order_cost'] for o in orders)
        urgent = len([o for o in orders if o['priority'] == 'URGENT'])
        high   = len([o for o in orders if o['priority'] == 'HIGH'])

        return jsonify({
            'orders': orders[:50],
            'summary': {
                'total_items': len(orders),
                'urgent': urgent,
                'high': high,
                'total_cost': round(total_cost, 2),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── Warehouses / Stock ────────────────────────────────
@app.route('/api/warehouses')
def api_warehouses():
    try:
        conn = get_conn(); cursor = conn.cursor()
        cursor.execute("""
            SELECT p.product_name_ar, p.product_name_en,
                   SUM(pa.amount) AS total_stock,
                   pa.exp_date,
                   p.sell_price, p.buy_price,
                   SUM(pa.amount) * p.buy_price AS stock_value
            FROM Product_Amount pa
            JOIN Products p ON p.product_id=pa.product_id
            WHERE pa.amount>0 AND p.deleted!='Y'
            GROUP BY p.product_name_ar, p.product_name_en, pa.exp_date, p.sell_price, p.buy_price
            ORDER BY stock_value DESC
        """)
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT SUM(pa.amount*p.buy_price) AS cost_value,
                   SUM(pa.amount*p.sell_price) AS sell_value,
                   COUNT(DISTINCT pa.product_id) AS sku_count
            FROM Product_Amount pa JOIN Products p ON p.product_id=pa.product_id
            WHERE pa.amount>0 AND p.deleted!='Y'
        """)
        totals = cursor.fetchone()
        conn.close()
        return jsonify({
            'stats': {
                'cost_value':  float(totals.cost_value or 0),
                'sell_value':  float(totals.sell_value or 0),
                'sku_count':   int(totals.sku_count or 0)
            },
            'items': [{'name': r.product_name_ar or r.product_name_en,
                       'stock': float(r.total_stock or 0),
                       'exp_date': str(r.exp_date)[:10] if r.exp_date else '',
                       'sell_price': float(r.sell_price or 0),
                       'stock_value': float(r.stock_value or 0)} for r in rows[:100]]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── HR / Staff ────────────────────────────────────────
@app.route('/api/staff')
def api_staff():
    try:
        conn = get_conn(); cursor = conn.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='Gedo_employee' ORDER BY ORDINAL_POSITION
        """)
        cols = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT TOP 20 * FROM Gedo_employee")
        rows = cursor.fetchall()

        # Cashier performance
        cursor.execute("""
            SELECT TOP 10 s.cashier_id, COUNT(*) AS tx, SUM(s.total_bill_net) AS total
            FROM Branches_sales_header s
            WHERE s.insert_date >= DATEADD(month,-1,GETDATE())
            GROUP BY s.cashier_id ORDER BY total DESC
        """)
        cashiers = cursor.fetchall()
        conn.close()

        return jsonify({
            'staff_count': len(rows),
            'staff': [{cols[i]: str(v) if v is not None else '' for i,v in enumerate(row)} for row in rows],
            'cashier_performance': [{'id': r.cashier_id, 'tx': int(r.tx), 'total': float(r.total)} for r in cashiers]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── Customers ─────────────────────────────────────────
@app.route('/api/customers')
def api_customers():
    try:
        conn = get_conn(); cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 20 COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='Gedo_customers' ORDER BY ORDINAL_POSITION
        """)
        cols = [r[0] for r in cursor.fetchall()]

        cursor.execute("""
            SELECT TOP 50
                cust_name,
                COUNT(*) AS visits,
                SUM(total_bill_net) AS lifetime_spend,
                AVG(total_bill_net) AS avg_basket,
                MAX(insert_date) AS last_visit,
                SUM(total_disc_money) AS total_disc
            FROM Branches_sales_header
            WHERE cust_name IS NOT NULL AND cust_name!='' AND cust_name!='0'
            GROUP BY cust_name
            ORDER BY lifetime_spend DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({
            'customers': [{
                'name': r.cust_name, 'visits': int(r.visits),
                'lifetime_spend': float(r.lifetime_spend or 0),
                'avg_basket': float(r.avg_basket or 0),
                'last_visit': str(r.last_visit)[:10] if r.last_visit else '',
                'total_disc': float(r.total_disc or 0)
            } for r in rows]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── Daily Accounts ────────────────────────────────────
@app.route('/api/daily_accounts')
def api_daily_accounts():
    try:
        conn = get_conn(); cursor = conn.cursor()
        today = datetime.now().date()

        # Today's financial movements by type
        cursor.execute("""
            SELECT gf_gedo_type, COUNT(*) AS cnt, SUM(gf_value) AS total
            FROM Gedo_Financial
            WHERE CAST(insert_date AS DATE)=?
            GROUP BY gf_gedo_type ORDER BY total DESC
        """, today)
        movements = cursor.fetchall()

        # Last 7 days daily totals
        cursor.execute("""
            SELECT CAST(insert_date AS DATE) AS day,
                   COUNT(*) AS tx, SUM(total_bill_net) AS sales,
                   SUM(total_disc_money) AS discounts
            FROM Branches_sales_header
            WHERE insert_date >= DATEADD(day,-7,GETDATE())
            GROUP BY CAST(insert_date AS DATE) ORDER BY day DESC
        """)
        daily = cursor.fetchall()
        conn.close()

        type_names = {1:'Cash In', 2:'Cash Out', 3:'Expense', 4:'Return',
                      5:'Purchase Pay', 6:'Transfer', 7:'Sale Cash', 8:'Deposit',
                      9:'Withdrawal', 10:'Other', 11:'Adjustment', 12:'Credit'}
        return jsonify({
            'today_movements': [{'type': type_names.get(r.gf_gedo_type, f'Type {r.gf_gedo_type}'),
                                  'count': int(r.cnt), 'total': float(r.total)} for r in movements],
            'daily_summary': [{'date': str(r.day), 'tx': int(r.tx),
                               'sales': float(r.sales), 'discounts': float(r.discounts or 0)} for r in daily]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

# ── General Accounts ──────────────────────────────────
@app.route('/api/general_accounts')
def api_general_accounts():
    try:
        conn = get_conn(); cursor = conn.cursor()

        # Full financial snapshot
        cursor.execute("""
            SELECT b.branch_name, cd.cash_depot_name_ar, cd.cash_depot_name_en,
                   cd.cash_depot_class, cd.cash_depot_current_money, cd.update_date
            FROM Branches_cash_depots cd JOIN Branches b ON b.branch_id=cd.branch_id
            WHERE cd.cash_depot_current_money>0 AND cd.cash_depot_name_ar!='cancel'
            ORDER BY b.branch_name, cd.cash_depot_class
        """)
        accounts = cursor.fetchall()

        # Monthly P&L approximation
        cursor.execute("""
            SELECT YEAR(s.insert_date) AS yr, MONTH(s.insert_date) AS mo,
                   SUM(s.total_bill_net) AS revenue,
                   ISNULL((
                       SELECT SUM(p.total_bill)
                       FROM Branches_purchase_header p
                       WHERE YEAR(p.insert_date)=YEAR(s.insert_date)
                       AND MONTH(p.insert_date)=MONTH(s.insert_date)
                       AND p.back='0'
                   ),0) AS purchases
            FROM Branches_sales_header s
            WHERE s.insert_date >= DATEADD(month,-6,GETDATE())
            GROUP BY YEAR(s.insert_date), MONTH(s.insert_date)
            ORDER BY yr, mo
        """)
        pnl = cursor.fetchall()
        conn.close()

        class_names = {1:'POS', 2:'Treasury', 3:'Bank Account', 4:'Other'}
        month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        return jsonify({
            'accounts': [{'branch': r.branch_name, 'name': r.cash_depot_name_en or r.cash_depot_name_ar,
                          'type': class_names.get(r.cash_depot_class,'Other'),
                          'balance': float(r.cash_depot_current_money),
                          'updated': str(r.update_date)[:16]} for r in accounts],
            'total': sum(float(r.cash_depot_current_money) for r in accounts),
            'monthly_pnl': [{'month': f"{month_names[r.mo-1]} {r.yr}",
                             'revenue': float(r.revenue), 'purchases': float(r.purchases),
                             'gross': float(r.revenue) - float(r.purchases)} for r in pnl]
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

