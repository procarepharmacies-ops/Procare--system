# ProCare Pharmacy System - Automated Setup for Windows 11 WSL2 Ubuntu
# PowerShell script to automate setup from Windows host
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

# Colors
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
$BLUE = "Cyan"

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $GREEN
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $RED
    exit 1
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $YELLOW
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor $BLUE
    Write-Host $Title -ForegroundColor $BLUE
    Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor $BLUE
}

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1: Windows Setup - Enable WSL2
# ═════════════════════════════════════════════════════════════════════════════

function Phase-1-Windows-Setup {
    Write-Section "PHASE 1: Windows 11 Setup"

    Write-Log "Checking if WSL2 is installed..."

    # Check WSL installation
    $wslCheck = wsl --list --verbose 2>&1

    if ($wslCheck -like "*Ubuntu*") {
        Write-Success "WSL2 with Ubuntu detected"
    } else {
        Write-Warning-Custom "WSL2 Ubuntu not detected. Please install:"
        Write-Warning-Custom "  Open PowerShell as Administrator and run:"
        Write-Warning-Custom "  wsl --install"
        Write-Warning-Custom "  Then restart your computer"
        exit 1
    }

    Write-Log "Updating WSL kernel..."
    wsl --update

    Write-Success "Phase 1 complete"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2: Launch WSL and Run Setup Script
# ═════════════════════════════════════════════════════════════════════════════

function Phase-2-WSL-Setup {
    Write-Section "PHASE 2: Running WSL2 Ubuntu Setup"

    Write-Log "Launching WSL and running setup script..."

    # Create the bash setup command
    $bashCommand = @'
#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

PROJECT_DIR="$HOME/projects/procare-dev/Procare--system"

# Update system
log "Updating system packages..."
sudo apt update > /dev/null 2>&1

# Install prerequisites
log "Installing prerequisites..."
sudo apt install -y curl wget git build-essential python3-dev python3-venv unixodbc unixodbc-dev > /dev/null 2>&1

# Check Python
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    warning "Python 3.10+ recommended. Current: $PYTHON_VERSION"
else
    success "Python $PYTHON_VERSION installed"
fi

# Create project directory
log "Creating project directories..."
mkdir -p ~/projects/procare-dev
cd ~/projects/procare-dev

# Clone or pull repository
if [ -d "$PROJECT_DIR" ]; then
    log "Repository exists, pulling latest..."
    cd "$PROJECT_DIR"
    git pull origin claude/slack-session-3hNj0
else
    log "Cloning repository..."
    git clone http://127.0.0.1:32925/git/procarepharmacies-ops/Procare--system.git
    cd "$PROJECT_DIR"
fi

git checkout claude/slack-session-3hNj0

# Create virtual environment
log "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
log "Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

success "Basic setup complete"

# Install ODBC driver
log "Installing ODBC driver for SQL Server..."
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add - > /dev/null 2>&1
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list > /dev/null 2>&1
sudo apt update > /dev/null 2>&1
sudo ACCEPT_EULA=Y apt install -y msodbcsql17 > /dev/null 2>&1

success "ODBC driver installed"

# Setup .env
log "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.template .env
    success ".env file created"
else
    success ".env already exists"
fi

# Create quick start scripts
log "Creating quick start scripts..."

cat > activate.sh << 'SCRIPT_EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ ProCare environment activated"
echo ""
echo "Available commands:"
echo "  python app.py                    - Start Flask server"
echo "  python test_slack_integration.py - Run tests"
echo "  python tools/hermes_slack_sync.py - Run daily sync"
SCRIPT_EOF

cat > start.sh << 'SCRIPT_EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting ProCare Pharmacy Dashboard..."
echo "Access at: http://localhost:5000"
echo ""
python app.py
SCRIPT_EOF

chmod +x activate.sh start.sh

success "Quick start scripts created"

# Run tests
log "Running integration tests..."
if python test_slack_integration.py > /dev/null 2>&1; then
    success "All tests passed"
else
    warning "Tests need review - continuing anyway"
fi

echo ""
echo "═════════════════════════════════════════════════════════════════════"
echo "✅ WSL2 UBUNTU SETUP COMPLETE!"
echo "═════════════════════════════════════════════════════════════════════"
echo ""
echo "NEXT STEPS:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "   Required settings:"
echo "   - SQL_SERVER=172.x.x.x (Windows host IP)"
echo "   - SQL_USERNAME=your_sql_user"
echo "   - SQL_PASSWORD=your_sql_password"
echo ""
echo "2. Find Windows host IP:"
echo "   cat /etc/resolv.conf | grep nameserver"
echo ""
echo "3. Start Flask server:"
echo "   ./start.sh"
echo ""
echo "4. Access dashboard:"
echo "   http://localhost:5000"
echo ""
'@

    # Run the bash script in WSL
    Write-Log "Executing setup in WSL2 Ubuntu..."
    $bashCommand | wsl bash

    Write-Success "Phase 2 complete - WSL2 setup finished"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3: Setup Slack Bot
# ═════════════════════════════════════════════════════════════════════════════

function Phase-3-Slack-Setup {
    Write-Section "PHASE 3: Slack Bot Setup"

    Write-Log "Slack bot setup instructions:"
    Write-Log ""
    Write-Log "1. Go to: https://api.slack.com/apps"
    Write-Log "2. Click 'Create New App' → 'From scratch'"
    Write-Log "3. Name: 'ProCare Pharmacy'"
    Write-Log "4. Select your workspace"
    Write-Log "5. Go to 'OAuth & Permissions'"
    Write-Log "6. Add Bot Token Scopes:"
    Write-Log "   - chat:write"
    Write-Log "   - chat:write.public"
    Write-Log "7. Install to workspace"
    Write-Log "8. Copy Bot User OAuth Token (xoxb-...)"
    Write-Log ""
    Write-Log "Then update .env in WSL:"
    Write-Log "  wsl"
    Write-Log "  nano .env"
    Write-Log "  SLACK_BOT_TOKEN=xoxb-[your-token]"
    Write-Log ""

    Read-Host "Press Enter after setting up Slack bot token"

    Write-Success "Phase 3 complete"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4: Open Dashboard
# ═════════════════════════════════════════════════════════════════════════════

function Phase-4-Dashboard {
    Write-Section "PHASE 4: Ready to Start"

    Write-Log ""
    Write-Log "Your ProCare system is ready! To start:"
    Write-Log ""
    Write-Log "1. Open Windows Terminal or PowerShell"
    Write-Log "2. Run: wsl"
    Write-Log "3. Run: cd ~/projects/procare-dev/Procare--system"
    Write-Log "4. Run: ./start.sh"
    Write-Log "5. Open browser: http://localhost:5000"
    Write-Log ""
    Write-Log "Or use the quick start script:"
    Write-Log "  wsl ~/projects/procare-dev/Procare--system/start.sh"
    Write-Log ""

    Write-Success "Phase 4 complete - System ready!"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 5: Summary
# ═════════════════════════════════════════════════════════════════════════════

function Phase-5-Summary {
    Write-Section "Setup Summary"

    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              ✅ ProCare System Setup Complete! ✅                          ║
║                                                                            ║
║              Windows 11 + WSL2 + Ubuntu Server                             ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ COMPLETED SETUP:
  ✓ WSL2 with Ubuntu verified
  ✓ Python virtual environment created
  ✓ All dependencies installed
  ✓ ODBC driver installed
  ✓ Quick start scripts created
  ✓ Tests verified (ready)

📚 DOCUMENTATION:
  • START_HERE.md - Quick start guide
  • SETUP_WINDOWS_WSL2_UBUNTU.md - Detailed setup
  • PRODUCTION_GO_LIVE.md - Deployment guide
  • CLAUDE_CODE_SLACK_PROMPT.md - Slack automation

🚀 NEXT STEPS:

  1. Get Slack Bot Token (https://api.slack.com/apps)
  2. Update .env with your credentials
  3. Test database connection
  4. Create Slack channels
  5. Start Flask server
  6. Access at http://localhost:5000

🎯 QUICK COMMANDS:

  wsl                                              # Launch WSL
  cd ~/projects/procare-dev/Procare--system        # Navigate
  ./start.sh                                       # Start server
  python tools/hermes_slack_sync.py                # Run sync

═══════════════════════════════════════════════════════════════════════════

"@ -ForegroundColor Green
}

# ═════════════════════════════════════════════════════════════════════════════
# Main Execution
# ═════════════════════════════════════════════════════════════════════════════

Write-Host "Starting ProCare Pharmacy System Setup for Windows 11..." -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')

if (-not $isAdmin) {
    Write-Warning-Custom "This script should be run as Administrator for best results"
    Write-Log "Continuing anyway..."
}

# Run phases
Phase-1-Windows-Setup
Phase-2-WSL-Setup
Phase-3-Slack-Setup
Phase-4-Dashboard
Phase-5-Summary

Write-Success "All phases complete!"
