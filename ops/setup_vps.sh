#!/usr/bin/env bash
# ============================================================
# ARGUS VPS Setup — Run once on your Hetzner VPS
# ============================================================
#
# Usage:
#   ssh root@YOUR_VPS
#   curl -fsSL https://raw.githubusercontent.com/philhie/argus/main/ops/setup_vps.sh | bash
#
#   Or copy this file to the VPS and run:
#   chmod +x setup_vps.sh && ./setup_vps.sh
#
# What this does:
#   1. Installs system dependencies (Python 3.11+, git, etc.)
#   2. Clones the ARGUS repo to /opt/argus
#   3. Creates Python venv and installs dependencies
#   4. Creates data directories
#   5. Sets up .env template
#   6. Makes ops scripts executable
#   7. Sets up cron job (22:00 CET nightly)
#   8. Sets timezone to Europe/Berlin
#
# Prerequisites:
#   - Ubuntu 22.04 or 24.04
#   - Root access
#   - Internet connection
#
# ============================================================

set -euo pipefail

echo "=========================================="
echo "ARGUS VPS Setup"
echo "=========================================="

# ── 1. System dependencies ─────────────────────────────────
echo ""
echo "[1/8] Installing system dependencies..."

apt-get update -qq
apt-get install -y -qq \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    jq \
    tmux \
    > /dev/null 2>&1

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  Python: ${PYTHON_VERSION}"

# ── 2. Clone repo ──────────────────────────────────────────
echo ""
echo "[2/8] Setting up ARGUS..."

ARGUS_DIR="/opt/argus"

if [ -d "${ARGUS_DIR}/.git" ]; then
    echo "  Repo exists, pulling latest..."
    cd "${ARGUS_DIR}"
    git pull --ff-only
else
    echo "  Cloning repo..."
    git clone https://github.com/philhie/argus.git "${ARGUS_DIR}"
    cd "${ARGUS_DIR}"
fi

echo "  Location: ${ARGUS_DIR}"

# ── 3. Python venv ─────────────────────────────────────────
echo ""
echo "[3/8] Creating Python environment..."

if [ ! -d "${ARGUS_DIR}/.venv" ]; then
    python3 -m venv "${ARGUS_DIR}/.venv"
fi

"${ARGUS_DIR}/.venv/bin/pip" install --upgrade pip -q
"${ARGUS_DIR}/.venv/bin/pip" install -e ".[all]" -q

echo "  Venv: ${ARGUS_DIR}/.venv"

# Verify installation
"${ARGUS_DIR}/.venv/bin/python3" -c "import argus; print(f'  ARGUS version: {argus.__version__}')"

# ── 4. Data directories ───────────────────────────────────
echo ""
echo "[4/8] Creating data directories..."

mkdir -p /data/leads
mkdir -p /data/scans
mkdir -p /data/output
mkdir -p /var/log/argus

echo "  /data/leads/    ← Upload your Apollo master CSV here"
echo "  /data/scans/    ← Scan JSONs accumulate here (persistent)"
echo "  /data/output/   ← Daily Instantly CSVs appear here"
echo "  /var/log/argus/ ← Logs"

# ── 5. Environment file ───────────────────────────────────
echo ""
echo "[5/8] Setting up environment..."

ENV_FILE="${ARGUS_DIR}/.env"

if [ ! -f "${ENV_FILE}" ]; then
    cp "${ARGUS_DIR}/.env.example" "${ENV_FILE}"
    chmod 600 "${ENV_FILE}"
    echo "  Created ${ENV_FILE} — FILL IN YOUR API KEYS!"
    echo ""
    echo "  ┌─────────────────────────────────────────────┐"
    echo "  │  IMPORTANT: Edit .env with your API keys    │"
    echo "  │                                             │"
    echo "  │  nano /opt/argus/.env                       │"
    echo "  │                                             │"
    echo "  │  Required:                                  │"
    echo "  │    HIBP_API_KEY=       (\$3.50/month)       │"
    echo "  │    GITHUB_TOKEN=       (free PAT)           │"
    echo "  │                                             │"
    echo "  │  Optional:                                  │"
    echo "  │    SHODAN_API_KEY=     (free: InternetDB)   │"
    echo "  │    ANTHROPIC_API_KEY=  (for attack paths)   │"
    echo "  │                                             │"
    echo "  │  NOT needed (disabled at scale):            │"
    echo "  │    SERPAPI_KEY=        (--steps 9 skips it) │"
    echo "  └─────────────────────────────────────────────┘"
else
    echo "  ${ENV_FILE} already exists, not overwriting."
fi

# ── 6. Make scripts executable ─────────────────────────────
echo ""
echo "[6/8] Setting permissions..."

chmod +x "${ARGUS_DIR}/ops/run_nightly.sh"
chmod +x "${ARGUS_DIR}/ops/prepare_batch.py"

echo "  Scripts ready"

# ── 7. Timezone ────────────────────────────────────────────
echo ""
echo "[7/8] Setting timezone to Europe/Berlin..."

timedatectl set-timezone Europe/Berlin 2>/dev/null || \
    ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

echo "  Timezone: $(date +%Z) ($(date))"

# ── 8. Cron job ────────────────────────────────────────────
echo ""
echo "[8/8] Setting up cron..."

CRON_LINE="0 22 * * * ${ARGUS_DIR}/ops/run_nightly.sh >> /var/log/argus/cron.log 2>&1"

# Check if cron already exists
if crontab -l 2>/dev/null | grep -q "run_nightly.sh"; then
    echo "  Cron job already exists, not duplicating."
else
    (crontab -l 2>/dev/null; echo "${CRON_LINE}") | crontab -
    echo "  Added cron: 22:00 CET nightly"
fi

echo ""
echo "=========================================="
echo "SETUP COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Add your API keys:"
echo "     nano /opt/argus/.env"
echo ""
echo "  2. Upload your Apollo CSV:"
echo "     scp master.csv root@$(hostname -I | awk '{print $1}'):/data/leads/master.csv"
echo ""
echo "  3. Test with a small batch (10 leads):"
echo "     cd /opt/argus"
echo "     .venv/bin/python3 -m argus scan --domain example.com"
echo ""
echo "  4. Do a dry run of the nightly script:"
echo "     BATCH_SIZE=10 /opt/argus/ops/run_nightly.sh"
echo ""
echo "  5. Monitor tonight's run:"
echo "     tail -f /var/log/argus/nightly_\$(date +%Y%m%d).log"
echo ""
echo "  6. Download tomorrow's CSV:"
echo "     scp root@$(hostname -I | awk '{print $1}'):/data/output/instantly_\$(date +%Y%m%d).csv ."
echo ""
