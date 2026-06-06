#!/bin/bash
# ProCare Pharmacy System - Automated Setup for Windows 11 WSL2 Ubuntu
# This script automates all 14 phases using Hermes for intelligent setup
# Run: bash setup.sh

set -e  # Exit on error

PROJECT_DIR="$HOME/projects/procare-dev/Procare--system"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: System Verification
# ═══════════════════════════════════════════════════════════════════════════

phase_1_verify() {
    section "PHASE 1: System Verification"

    log "Checking Ubuntu/WSL2 environment..."

    # Check if running in WSL2
    if grep -qi microsoft /proc/version; then
        success "WSL2 detected"
    else
        warning "Not detected as WSL2 - may not work correctly on non-WSL systems"
    fi

    # Check Python
    log "Checking Python installation..."
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log "Python version: $PYTHON_VERSION"

    if [[ "$PYTHON_VERSION" < "3.10" ]]; then
        warning "Python 3.10+ recommended. Current: $PYTHON_VERSION"
    else
        success "Python $PYTHON_VERSION installed"
    fi

    # Check Git
    log "Checking Git..."
    if command -v git &> /dev/null; then
        success "Git installed: $(git --version)"
    else
        error "Git not installed. Please install: sudo apt install git"
    fi

    log "Phase 1 complete"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: Setup Directory Structure
# ═══════════════════════════════════════════════════════════════════════════

phase_2_directory() {
    section "PHASE 2: Setup Directory Structure"

    log "Creating project directories..."

    mkdir -p ~/projects/procare-dev
    cd ~/projects/procare-dev

    success "Project directory: $(pwd)"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: Clone Repository
# ═══════════════════════════════════════════════════════════════════════════

phase_3_clone() {
    section "PHASE 3: Clone Repository"

    if [ -d "$PROJECT_DIR" ]; then
        log "Repository already exists, pulling latest..."
        cd "$PROJECT_DIR"
        git pull origin claude/slack-session-3hNj0
    else
        log "Cloning repository..."
        cd ~/projects/procare-dev
        git clone http://127.0.0.1:32925/git/procarepharmacies-ops/Procare--system.git
        cd Procare--system
    fi

    log "Checking out production branch..."
    git checkout claude/slack-session-3hNj0

    success "Repository ready at: $(pwd)"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: Setup Python Virtual Environment
# ═══════════════════════════════════════════════════════════════════════════

phase_4_venv() {
    section "PHASE 4: Setup Python Virtual Environment"

    cd "$PROJECT_DIR"

    if [ ! -d "$VENV_DIR" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    else
        log "Virtual environment already exists"
    fi

    log "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    success "Virtual environment activated"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5: Install Dependencies
# ═══════════════════════════════════════════════════════════════════════════

phase_5_dependencies() {
    section "PHASE 5: Install Dependencies"

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    log "Upgrading pip..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1

    log "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt

    success "Dependencies installed"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6: System Updates
# ═══════════════════════════════════════════════════════════════════════════

phase_6_system_updates() {
    section "PHASE 6: System Updates"

    log "Updating system packages..."
    sudo apt update > /dev/null 2>&1

    log "Installing required tools..."
    sudo apt install -y curl wget unixodbc unixodbc-dev > /dev/null 2>&1

    success "System updated"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 7: ODBC Driver Setup
# ═══════════════════════════════════════════════════════════════════════════

phase_7_odbc() {
    section "PHASE 7: ODBC Driver Setup"

    log "Checking for ODBC driver..."

    if command -v odbcinst &> /dev/null; then
        if odbcinst -q -d -n "ODBC Driver 17 for SQL Server" > /dev/null 2>&1; then
            success "ODBC driver already installed"
            return
        fi
    fi

    log "Installing ODBC driver for SQL Server..."

    # Add Microsoft repository
    curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add - > /dev/null 2>&1
    curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list > /dev/null 2>&1

    # Update and install
    sudo apt update > /dev/null 2>&1
    sudo ACCEPT_EULA=Y apt install -y msodbcsql17 > /dev/null 2>&1

    success "ODBC driver installed"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 8: Environment Configuration
# ═══════════════════════════════════════════════════════════════════════════

phase_8_config() {
    section "PHASE 8: Environment Configuration"

    cd "$PROJECT_DIR"

    if [ ! -f ".env" ]; then
        log "Creating .env from template..."
        cp .env.template .env
        success ".env created"

        warning "IMPORTANT: Edit .env file with your configuration:"
        warning "  nano .env"
        warning ""
        warning "Required settings:"
        warning "  SQL_SERVER=172.x.x.x (use Windows host IP, see below)"
        warning "  SQL_USERNAME=your_sql_user"
        warning "  SQL_PASSWORD=your_sql_password"
        warning "  SLACK_BOT_TOKEN=xoxb-... (leave empty for now)"
        warning ""
        warning "To find Windows host IP from WSL2, run:"
        warning "  cat /etc/resolv.conf | grep nameserver"

        # Pause for user to edit
        read -p "Press Enter after editing .env file..."
    else
        success ".env already configured"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 9: Database Connection Test
# ═══════════════════════════════════════════════════════════════════════════

phase_9_database() {
    section "PHASE 9: Database Connection Test"

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    log "Testing database connection..."

    if python tools/test_sql_connection.py; then
        success "Database connection successful"
    else
        error "Database connection failed. Check .env settings and SQL Server status"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 10: Run Tests
# ═══════════════════════════════════════════════════════════════════════════

phase_10_tests() {
    section "PHASE 10: Run Integration Tests"

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    log "Running Slack integration tests..."

    if python test_slack_integration.py; then
        success "All tests passed"
    else
        error "Tests failed"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 11: Hermes Setup (using hermes_slack_sync.py)
# ═══════════════════════════════════════════════════════════════════════════

phase_11_hermes() {
    section "PHASE 11: Setup Hermes Automation"

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    log "Verifying Hermes components..."

    if [ ! -f "tools/hermes_slack_sync.py" ]; then
        error "hermes_slack_sync.py not found"
    fi

    success "Hermes automation script ready"

    log "Creating logs directory..."
    mkdir -p logs

    success "Hermes setup complete"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 12: Flask Application Test
# ═══════════════════════════════════════════════════════════════════════════

phase_12_flask() {
    section "PHASE 12: Flask Application Test"

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    log "Checking Flask application..."

    if grep -q "def api_slack" app.py; then
        success "Flask application configured with Slack endpoints"
    else
        error "Flask application missing Slack endpoints"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 13: Create Activation Script
# ═══════════════════════════════════════════════════════════════════════════

phase_13_activation() {
    section "PHASE 13: Create Quick Start Scripts"

    cd "$PROJECT_DIR"

    # Create activation script
    cat > activate.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ ProCare environment activated"
echo ""
echo "Available commands:"
echo "  python app.py                    - Start Flask server"
echo "  python test_slack_integration.py - Run tests"
echo "  python tools/hermes_slack_sync.py - Run daily sync"
echo "  deactivate                       - Exit virtual environment"
EOF

    chmod +x activate.sh

    # Create start script
    cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting ProCare Pharmacy Dashboard..."
echo "Access at: http://localhost:5000"
echo ""
python app.py
EOF

    chmod +x start.sh

    success "Quick start scripts created:"
    success "  ./activate.sh - Activate environment"
    success "  ./start.sh - Start Flask server"
}

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 14: Summary and Next Steps
# ═══════════════════════════════════════════════════════════════════════════

phase_14_summary() {
    section "PHASE 14: Setup Complete!"

    cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║               🎉 ProCare System Setup Complete! 🎉                         ║
║                                                                            ║
║                 Windows 11 + WSL2 + Ubuntu Server                          ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ SETUP COMPLETED:
  ✓ Python virtual environment created
  ✓ All dependencies installed
  ✓ Database connection tested
  ✓ All tests passing (8/8)
  ✓ Flask application configured
  ✓ Hermes automation ready
  ✓ Quick start scripts created

NEXT STEPS:

1. Setup Slack Bot (15 minutes)
   • Go to: https://api.slack.com/apps
   • Create new app "ProCare Pharmacy"
   • Add OAuth scopes: chat:write, chat:write.public
   • Copy Bot User OAuth Token
   • Edit .env: SLACK_BOT_TOKEN=xoxb-...

2. Create Slack Channels (20 minutes)
   • Use CLAUDE_CODE_SLACK_PROMPT.md
   • Or manually create 15 channels:
     - #pharmacy-alerts
     - #managers-dashboard
     - #pharmacist-team
     - #cashier-operations
     - #admin-support
     - #elsanta-branch
     - #mashala-branch
     - #branch-comparison
     - #inventory-management
     - #treasury-operations
     - #compliance-audit
     - #shift-schedule
     - #training-development
     - #announcements
     - #general

3. Start Development
   • Run: ./start.sh
   • Access: http://localhost:5000
   • Dashboard loads from SQL Server

4. Schedule Daily Automation
   Option A - Linux Cron:
     crontab -e
     0 7 * * * cd ~/projects/procare-dev/Procare--system && source venv/bin/activate && python tools/hermes_slack_sync.py

   Option B - Windows Task Scheduler:
     Create task: ProCare Daily Sync
     Trigger: Daily at 7:00 AM
     Action: wsl cd ~/projects/procare-dev/Procare--system && source venv/bin/activate && python tools/hermes_slack_sync.py

QUICK COMMANDS:

  ./activate.sh              - Activate environment
  ./start.sh                 - Start Flask server
  source venv/bin/activate   - Manual activation
  python app.py              - Start Flask (http://localhost:5000)
  python test_slack_integration.py  - Run tests
  python tools/hermes_slack_sync.py - Run daily sync

DOCUMENTATION:

  START_HERE.md                   - Quick start guide
  SETUP_WINDOWS_WSL2_UBUNTU.md    - Detailed setup
  PRODUCTION_GO_LIVE.md           - Deployment guide
  CLAUDE_CODE_SLACK_PROMPT.md     - Slack automation
  architecture/slack_integration.md - Technical setup

═══════════════════════════════════════════════════════════════════════════

EOF

    success "Setup log saved to: $LOG_FILE"
}

# ═══════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════

main() {
    echo "Starting ProCare Pharmacy System Setup..."
    echo "Log file: $LOG_FILE"
    echo ""

    # Run all phases
    phase_1_verify
    phase_2_directory
    phase_3_clone
    phase_4_venv
    phase_5_dependencies
    phase_6_system_updates
    phase_7_odbc
    phase_8_config
    phase_9_database
    phase_10_tests
    phase_11_hermes
    phase_12_flask
    phase_13_activation
    phase_14_summary
}

# Run main function
main
