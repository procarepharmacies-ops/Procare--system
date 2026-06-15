# ============================================================
#  ProCare Pharmacy — Mashala Branch Setup & Diagnostics
#  Run as Administrator on Elsanta PC
#  Usage:  $Branch = "elsanta"; .\setup-mashala.ps1
# ============================================================
param(
    [string]$Branch = $env:BRANCH
)
if (-not $Branch) { $Branch = "elsanta" }

$MASHALA_IP  = "196.202.93.36"
$MASHALA_PORT = 1433
$SQL_USER    = "ahmedibrahim"
$SQL_PASS    = "EgstART01`$"
$DB          = "stock"
$LOCAL_SQL   = "(local)"
$REP_EXE     = "Replication Master.exe"

function Write-Header($msg) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-OK($msg)   { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-WARN($msg) { Write-Host "[!!]  $msg" -ForegroundColor Yellow }
function Write-ERR($msg)  { Write-Host "[XX]  $msg" -ForegroundColor Red }
function Write-INFO($msg) { Write-Host "      $msg" -ForegroundColor White }

function Run-SQL($server, $query, $useWindows = $true) {
    if ($useWindows) {
        $result = sqlcmd -S $server -E -d $DB -Q $query -W 2>&1
    } else {
        $result = sqlcmd -S $server -U $SQL_USER -P $SQL_PASS -d $DB -Q $query -W 2>&1
    }
    return $result
}

# ─── 1. HEADER ───────────────────────────────────────────────
Clear-Host
Write-Host @"
  ____            ____
 |  _ \ _ __ ___/ ___|__ _ _ __ ___
 | |_) | '__/ _ \___ \/ _` | '__/ _ \
 |  __/| | | (_) |__) | (_| | | |  __/
 |_|   |_|  \___/____/ \__,_|_|  \___|

 Mashala Branch Diagnostics — Elsanta Server
 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@ -ForegroundColor Cyan


# ─── 2. NETWORK CHECK ────────────────────────────────────────
Write-Header "STEP 1 — Network Connectivity to Mashala"

$ping = Test-Connection -ComputerName $MASHALA_IP -Count 2 -Quiet
if ($ping) {
    Write-OK "Ping to Mashala ($MASHALA_IP) — REACHABLE"
} else {
    Write-ERR "Ping to Mashala ($MASHALA_IP) — UNREACHABLE"
    Write-WARN "Check internet connection / router port forwarding (port 1433)"
}

# TCP port test
$tcp = New-Object System.Net.Sockets.TcpClient
try {
    $tcp.Connect($MASHALA_IP, $MASHALA_PORT)
    Write-OK "TCP port 1433 on Mashala — OPEN"
    $tcp.Close()
} catch {
    Write-ERR "TCP port 1433 on Mashala — BLOCKED or CLOSED"
}


# ─── 3. SQL CONNECTIVITY ─────────────────────────────────────
Write-Header "STEP 2 — SQL Server Connectivity"

# Local (Elsanta)
$ver = Run-SQL $LOCAL_SQL "SELECT @@SERVERNAME AS srv, @@VERSION AS ver"
if ($ver -match "DESKTOP") {
    Write-OK "Elsanta SQL Server — Connected ($(($ver | Select-String 'DESKTOP')[0].ToString().Trim()))"
} else {
    Write-ERR "Elsanta SQL Server — Cannot connect"
}

# Remote (Mashala)
$mver = sqlcmd -S "$MASHALA_IP,$MASHALA_PORT" -U $SQL_USER -P $SQL_PASS -d $DB -Q "SELECT @@SERVERNAME" -W 2>&1
if ($mver -match "DESKTOP") {
    Write-OK "Mashala SQL Server — Connected ($($mver | Select-String 'DESKTOP' | Select-Object -First 1))"
} else {
    Write-ERR "Mashala SQL Server — Cannot connect"
    Write-INFO "Error: $($mver | Select-Object -Last 3 | Out-String)"
}


# ─── 4. REPLICATION HEALTH ───────────────────────────────────
Write-Header "STEP 3 — Replication Health (from Elsanta DB)"

$repQuery = @"
SELECT
  branch_id,
  branch_ip1,
  rep_last_sales_id,
  CONVERT(varchar,rep_sales_date,120)          AS rep_sales_date,
  rep_last_purchase_id,
  CONVERT(varchar,rep_purchase_date,120)       AS rep_purchase_date,
  rep_last_cash_disk_close_id,
  CONVERT(varchar,rep_cash_disk_close_date,120) AS rep_cash_close_date,
  rep_last_shortcoming_id
FROM Branches
ORDER BY branch_id
"@

Write-INFO "Branches replication cursors:"
Run-SQL $LOCAL_SQL $repQuery | Write-Host

# Check if purchases/cash closes are stale
$staleQuery = @"
SELECT
  DATEDIFF(day, rep_purchase_date, GETDATE())      AS purchase_days_behind,
  DATEDIFF(day, rep_cash_disk_close_date, GETDATE()) AS cashclose_days_behind,
  DATEDIFF(day, rep_sales_date, GETDATE())         AS sales_days_behind
FROM Branches WHERE branch_id = 2
"@
$stale = Run-SQL $LOCAL_SQL $staleQuery
$stale | Write-Host

if ($stale -match "1[4-9]|[2-9][0-9]") {
    Write-ERR "Mashala purchases or cash closes are MORE THAN 14 days behind!"
} elseif ($stale -match "[2-9]") {
    Write-WARN "Mashala sync is several days behind — restart Replication Master recommended"
} else {
    Write-OK "Replication appears current"
}


# ─── 5. MONEY TRANSFER STATUS ────────────────────────────────
Write-Header "STEP 4 — Branch_money_convert Status"

$moneyElsanta = Run-SQL $LOCAL_SQL "SELECT COUNT(*) as total, SUM(CASE WHEN is_open=1 THEN 1 ELSE 0 END) as pending, SUM(amount) as total_egp FROM Branch_money_convert"
Write-INFO "Elsanta Branch_money_convert:"
$moneyElsanta | Write-Host

$moneyMashala = sqlcmd -S "$MASHALA_IP,$MASHALA_PORT" -U $SQL_USER -P $SQL_PASS -d $DB -Q "SELECT COUNT(*) as total, SUM(CASE WHEN is_open=1 THEN 1 ELSE 0 END) as pending FROM Branch_money_convert" -W 2>&1
Write-INFO "Mashala Branch_money_convert:"
$moneyMashala | Write-Host

if ($moneyMashala -match "^\s*[0-5]\s") {
    Write-ERR "Mashala has very few money transfer records — data is NOT synced"
    Write-WARN "See estock-system-guide.md Section 8, Problem 1 for the fix steps"
} else {
    Write-OK "Mashala money transfer count looks reasonable"
}


# ─── 6. TODAY'S TRANSACTIONS ─────────────────────────────────
Write-Header "STEP 5 — Today's Transactions ($(Get-Date -Format 'yyyy-MM-dd'))"

$todayQuery = @"
SELECT
  'Elsanta_Sales'    AS source, COUNT(*) AS bills, SUM(total_bill_net) AS revenue_egp
FROM Sales_header WHERE insert_date >= CAST(GETDATE() AS DATE)
UNION ALL
SELECT
  'Mashala_Sales_synced', COUNT(*), SUM(total_bill_net)
FROM Branches_sales_header WHERE insert_date >= CAST(GETDATE() AS DATE) AND branch_id=2
UNION ALL
SELECT
  'Elsanta_Purchases', COUNT(*), SUM(total_bill)
FROM Purchase_header WHERE insert_date >= CAST(GETDATE() AS DATE)
"@
Run-SQL $LOCAL_SQL $todayQuery | Write-Host


# ─── 7. REPLICATION MASTER PROCESS ───────────────────────────
Write-Header "STEP 6 — Replication Master Process"

$repProc = Get-Process -Name "Replication Master" -ErrorAction SilentlyContinue
if ($repProc) {
    Write-OK "Replication Master is RUNNING (PID: $($repProc.Id), CPU: $([math]::Round($repProc.CPU,1))s)"
} else {
    Write-ERR "Replication Master is NOT RUNNING"
    Write-WARN "Possible cause: maua password was changed, breaking the connection"

    $ans = Read-Host "`n  Do you want to RESTART Replication Master now? (y/n)"
    if ($ans -eq 'y') {
        $repPath = "C:\Program Files (x86)\Modern Soft For Programming\e-Stock Replication Setup\Replication Master.exe"
        if (Test-Path $repPath) {
            Start-Process -FilePath $repPath -WindowStyle Normal
            Write-OK "Replication Master started from: $repPath"
            Start-Sleep -Seconds 5
            $check = Get-Process -Name "Replication Master" -ErrorAction SilentlyContinue
            if ($check) { Write-OK "Process confirmed running (PID: $($check.Id))" }
            else { Write-ERR "Process did not start — check the path and credentials" }
        } else {
            Write-ERR "Executable not found at expected path:"
            Write-INFO $repPath
            Write-INFO "Search for it:"
            Get-ChildItem "C:\Program Files (x86)\Modern Soft*" -Recurse -Filter "Replication*" -ErrorAction SilentlyContinue | Select-Object FullName | Write-Host
        }
    }
}


# ─── 8. POST-CHECK REPLICATION ───────────────────────────────
Write-Header "STEP 7 — Verify Latest Sync Timestamps"

$syncCheck = @"
SELECT
  'Mashala_Sales'     AS data_type, MAX(insert_date) AS last_received FROM Branches_sales_header    WHERE branch_id=2
UNION ALL SELECT
  'Mashala_Purchases',               MAX(insert_date)                 FROM Branches_purchase_header WHERE branch_id=2
UNION ALL SELECT
  'Mashala_CashCloses',              MAX(insert_date)                 FROM Branches_Cash_disk_close WHERE branch_id=2
UNION ALL SELECT
  'Mashala_Shortcomings',            MAX(insert_date)                 FROM Branches_shortcoming     WHERE branch_id=2
"@
Run-SQL $LOCAL_SQL $syncCheck | Write-Host


# ─── 9. INTER-BRANCH BALANCE ─────────────────────────────────
Write-Header "STEP 8 — Inter-Branch Financial Balance"

$balQuery = @"
SELECT TOP 1
  total        AS mashala_owes_elsanta_egp,
  insert_date  AS as_of_date
FROM Gedo_branches
WHERE branch_id = 2
ORDER BY gb_id DESC
"@
Run-SQL $LOCAL_SQL $balQuery | Write-Host


# ─── 10. SUMMARY ─────────────────────────────────────────────
Write-Header "SUMMARY — Outstanding Action Items"

Write-Host ""
Write-Host "  URGENT:" -ForegroundColor Red
Write-Host "  [ ] Restart Replication Master if stopped (Step 6 above)" -ForegroundColor Yellow
Write-Host "  [ ] Fix Branch_money_convert: copy 1,090 records from Elsanta to Mashala" -ForegroundColor Yellow
Write-Host "  [ ] Verify purchases sync resumes after Replication Master restart" -ForegroundColor Yellow
Write-Host ""
Write-Host "  MEDIUM:" -ForegroundColor DarkYellow
Write-Host "  [ ] Get maua password from vendor (Modern Soft For Programming)" -ForegroundColor White
Write-Host "  [ ] Set up nightly database backup schedule" -ForegroundColor White
Write-Host "  [ ] Add rep_last_branch_money_convert_id to Branches table (vendor task)" -ForegroundColor White
Write-Host ""
Write-Host "  DASHBOARD:" -ForegroundColor Cyan
Write-Host "  [ ] Run START_DASHBOARD.bat to launch API + alerts" -ForegroundColor White
Write-Host "  [ ] Configure WhatsApp CallMeBot API key" -ForegroundColor White
Write-Host "  [ ] Set up Windows Task Scheduler for auto-start" -ForegroundColor White
Write-Host ""
Write-Host "  Done. $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host ""
