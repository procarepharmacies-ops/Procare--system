-- ============================================================
-- ProCare Pharmacy — Complete Diagnostic Query Pack
-- Run in SQL Server Management Studio → database: stock
-- Copy ALL of this, paste into SSMS, press F5
-- ============================================================

USE stock;
GO

-- ── 1. SQL SERVER VERSION & EDITION ──────────────────────────
PRINT '=== SERVER INFO ===';
SELECT 
    @@VERSION                           AS sql_version,
    SERVERPROPERTY('Edition')           AS edition,
    SERVERPROPERTY('ProductVersion')    AS version_number,
    DB_NAME()                           AS current_database,
    SUM(size * 8.0 / 1024)             AS database_size_mb
FROM sys.database_files;
GO

-- ── 2. ROW COUNTS (how much real data you have) ──────────────
PRINT '=== ROW COUNTS ===';
SELECT 'Products'           AS table_name, COUNT(*) AS rows FROM Products        UNION ALL
SELECT 'Products_online',                  COUNT(*)        FROM Products_online   UNION ALL
SELECT 'Product_Amount',                   COUNT(*)        FROM Product_Amount    UNION ALL
SELECT 'Product_groups',                   COUNT(*)        FROM Product_groups    UNION ALL
SELECT 'Sales_header',                     COUNT(*)        FROM Sales_header      UNION ALL
SELECT 'Sales_details',                    COUNT(*)        FROM Sales_details     UNION ALL
SELECT 'Purchase_header',                  COUNT(*)        FROM Purchase_header   UNION ALL
SELECT 'Purchase_details',                 COUNT(*)        FROM Purchase_details  UNION ALL
SELECT 'Back_sales_header',                COUNT(*)        FROM Back_sales_header UNION ALL
SELECT 'Back_purchase_header',             COUNT(*)        FROM Back_purchase_header UNION ALL
SELECT 'Customer',                         COUNT(*)        FROM Customer          UNION ALL
SELECT 'Vendor',                           COUNT(*)        FROM Vendor            UNION ALL
SELECT 'Employee',                         COUNT(*)        FROM Employee          UNION ALL
SELECT 'Employee_salary',                  COUNT(*)        FROM Employee_salary   UNION ALL
SELECT 'Branches',                         COUNT(*)        FROM Branches          UNION ALL
SELECT 'Stores',                           COUNT(*)        FROM Stores            UNION ALL
SELECT 'Account_Tree',                     COUNT(*)        FROM Account_Tree      UNION ALL
SELECT 'user_login',                       COUNT(*)        FROM user_login
ORDER BY rows DESC;
GO

-- ── 3. BRANCHES (confirms Mashala + Elsanta) ─────────────────
PRINT '=== BRANCHES ===';
SELECT * FROM Branches;
GO

-- ── 4. COMPANY INFORMATION ───────────────────────────────────
PRINT '=== COMPANY INFO ===';
SELECT * FROM co_inf;
GO

-- ── 5. SALES DATE RANGE (years of history) ───────────────────
PRINT '=== SALES HISTORY ===';
SELECT
    MIN(Date_time)                              AS oldest_sale,
    MAX(Date_time)                              AS newest_sale,
    COUNT(*)                                    AS total_invoices,
    COUNT(DISTINCT CAST(Date_time AS DATE))     AS trading_days,
    COUNT(DISTINCT Customer_id)                 AS unique_customers,
    SUM(Net)                                    AS total_revenue_alltime,
    AVG(Net)                                    AS avg_invoice_value
FROM Sales_header
WHERE Is_deleted = 0;
GO

-- ── 6. THIS MONTH'S SALES BY BRANCH ──────────────────────────
PRINT '=== THIS MONTH BY BRANCH ===';
SELECT
    b.Branch_name                   AS branch,
    COUNT(sh.Bill_id)               AS invoices,
    SUM(sh.Net)                     AS revenue,
    AVG(sh.Net)                     AS avg_invoice
FROM Sales_header sh
JOIN Branches b ON sh.Branch_id = b.Branch_id
WHERE MONTH(sh.Date_time) = MONTH(GETDATE())
  AND YEAR(sh.Date_time)  = YEAR(GETDATE())
  AND sh.Is_deleted = 0
GROUP BY b.Branch_id, b.Branch_name
ORDER BY revenue DESC;
GO

-- ── 7. TODAY'S SALES ─────────────────────────────────────────
PRINT '=== TODAY SALES ===';
SELECT
    b.Branch_name                   AS branch,
    COUNT(sh.Bill_id)               AS invoices,
    SUM(sh.Net)                     AS revenue
FROM Sales_header sh
JOIN Branches b ON sh.Branch_id = b.Branch_id
WHERE CAST(sh.Date_time AS DATE) = CAST(GETDATE() AS DATE)
  AND sh.Is_deleted = 0
GROUP BY b.Branch_id, b.Branch_name;
GO

-- ── 8. TOP 20 PRODUCTS (last 30 days) ────────────────────────
PRINT '=== TOP 20 PRODUCTS (30 days) ===';
SELECT TOP 20
    p.Product_name                  AS product,
    SUM(sd.Qty)                     AS qty_sold,
    SUM(sd.Total)                   AS revenue
FROM Sales_details sd
JOIN Sales_header sh  ON sd.Bill_id    = sh.Bill_id
JOIN Products p       ON sd.Product_id = p.Product_id
WHERE sh.Date_time >= DATEADD(day, -30, GETDATE())
  AND sh.Is_deleted = 0
GROUP BY p.Product_id, p.Product_name
ORDER BY qty_sold DESC;
GO

-- ── 9. LOW STOCK ITEMS ───────────────────────────────────────
PRINT '=== LOW STOCK (below reorder level) ===';
SELECT TOP 30
    p.Product_name                  AS product,
    pa.Amount                       AS current_stock,
    p.Min_amount                    AS reorder_level,
    (p.Min_amount - pa.Amount)      AS deficit,
    b.Branch_name                   AS branch
FROM Products p
JOIN Product_Amount pa ON p.Product_id  = pa.Product_id
JOIN Branches b        ON pa.Store_id   = b.Branch_id
WHERE pa.Amount <= p.Min_amount
  AND p.Is_deleted = 0
  AND p.Min_amount > 0
ORDER BY deficit DESC;
GO

-- ── 10. EXPIRY ALERTS (next 90 days) ─────────────────────────
PRINT '=== EXPIRY ALERTS (90 days) ===';
SELECT TOP 30
    p.Product_name                              AS product,
    pa.Amount                                   AS stock_qty,
    pa.Expiry_date                              AS expiry_date,
    DATEDIFF(day, GETDATE(), pa.Expiry_date)    AS days_remaining,
    b.Branch_name                               AS branch
FROM Products p
JOIN Product_Amount pa ON p.Product_id = pa.Product_id
JOIN Branches b        ON pa.Store_id  = b.Branch_id
WHERE pa.Expiry_date <= DATEADD(day, 90, GETDATE())
  AND pa.Amount > 0
  AND p.Is_deleted = 0
ORDER BY pa.Expiry_date ASC;
GO

-- ── 11. TOP 10 SUPPLIERS (by purchase value) ─────────────────
PRINT '=== TOP SUPPLIERS ===';
SELECT TOP 10
    v.Vendor_name                   AS supplier,
    COUNT(ph.Purchase_id)           AS orders,
    SUM(ph.Total)                   AS total_purchased,
    MAX(ph.Date_time)               AS last_order
FROM Purchase_header ph
JOIN Vendor v ON ph.Vendor_id = v.Vendor_id
WHERE ph.Is_deleted = 0
GROUP BY v.Vendor_id, v.Vendor_name
ORDER BY total_purchased DESC;
GO

-- ── 12. EMPLOYEES ────────────────────────────────────────────
PRINT '=== EMPLOYEES ===';
SELECT 
    e.Emp_name      AS name,
    e.Job_id,
    j.Job_name      AS role,
    b.Branch_name   AS branch,
    e.Is_active
FROM Employee e
LEFT JOIN Jobs j     ON e.Job_id     = j.Job_id
LEFT JOIN Branches b ON e.Branch_id  = b.Branch_id
ORDER BY b.Branch_name, e.Emp_name;
GO

-- ── 13. SECURITY CHECK — PASSWORD STORAGE ────────────────────
PRINT '=== PASSWORD SECURITY CHECK ===';
SELECT
    User_name                       AS username,
    LEN(Password)                   AS password_length,
    LEFT(Password, 10)              AS password_preview,
    CASE
        WHEN LEN(Password) < 20  THEN '🔴 PLAIN TEXT — CRITICAL'
        WHEN LEN(Password) = 32  THEN '🟠 MD5 HASH — HIGH RISK'
        WHEN LEN(Password) = 64  THEN '🟡 SHA-256 — MEDIUM'
        WHEN LEN(Password) > 50  THEN '🟢 LIKELY HASHED — OK'
        ELSE '⚪ UNKNOWN'
    END AS security_status
FROM user_login;
GO

-- ── 14. MONTHLY REVENUE TREND (last 12 months) ───────────────
PRINT '=== MONTHLY TREND (12 months) ===';
SELECT
    FORMAT(sh.Date_time, 'yyyy-MM')     AS month,
    b.Branch_name                       AS branch,
    COUNT(sh.Bill_id)                   AS invoices,
    SUM(sh.Net)                         AS revenue,
    AVG(sh.Net)                         AS avg_invoice
FROM Sales_header sh
JOIN Branches b ON sh.Branch_id = b.Branch_id
WHERE sh.Date_time >= DATEADD(month, -12, GETDATE())
  AND sh.Is_deleted = 0
GROUP BY FORMAT(sh.Date_time, 'yyyy-MM'), b.Branch_id, b.Branch_name
ORDER BY month ASC, revenue DESC;
GO

-- ── 15. COLUMN NAMES FOR CORE TABLES ─────────────────────────
PRINT '=== CORE TABLE COLUMNS ===';
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN (
    'Products','Sales_header','Sales_details',
    'Purchase_header','Customer','Vendor',
    'Employee','Branches','Product_Amount'
)
ORDER BY TABLE_NAME, ORDINAL_POSITION;
GO

-- ============================================================
-- DONE — Copy ALL results and paste back into Claude chat
-- ============================================================
