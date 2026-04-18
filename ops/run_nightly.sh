#!/usr/bin/env bash
# ============================================================
# ARGUS Nightly Batch Scanner
# Cron: 0 22 * * * /opt/argus/ops/run_nightly.sh
# ============================================================
#
# What this does:
#   1. Picks next 1000 unscanned leads from the master CSV
#   2. Splits into 20 chunks (one per parallel worker)
#   3. Runs 20 parallel argus scan workers
#   4. Waits for all to finish
#   5. Runs argus export on tonight's batch → Instantly-ready CSV
#   6. Logs summary
#
# Override defaults via environment:
#   BATCH_SIZE=50 WORKERS=5 /opt/argus/ops/run_nightly.sh
#
# ============================================================

set -euo pipefail

# ── Configuration (override via env vars) ──────────────────
ARGUS_DIR="/opt/argus"
VENV="${ARGUS_DIR}/.venv/bin/python3"
DATA_DIR="/data"
LEADS_CSV="${DATA_DIR}/leads/master.csv"
SCANS_DIR="${DATA_DIR}/scans"
OUTPUT_DIR="${DATA_DIR}/output"
LOG_DIR="/var/log/argus"

BATCH_SIZE="${BATCH_SIZE:-1000}"
WORKERS="${WORKERS:-20}"
MAX_STEP="${MAX_STEP:-9}"

DATE=$(date +%Y%m%d)
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
CHUNKS_DIR="/tmp/argus_chunks_${DATE}"
LOCKFILE="/tmp/argus_nightly.lock"

# ── Lockfile (prevent double-runs) ─────────────────────────
if [ -f "${LOCKFILE}" ]; then
    LOCK_PID=$(cat "${LOCKFILE}" 2>/dev/null || echo "unknown")
    if kill -0 "${LOCK_PID}" 2>/dev/null; then
        echo "ERROR: Another run active (PID ${LOCK_PID}). Exiting."
        exit 1
    else
        echo "WARNING: Stale lockfile (PID ${LOCK_PID} dead). Removing."
        rm -f "${LOCKFILE}"
    fi
fi
echo $$ > "${LOCKFILE}"
trap 'rm -f "${LOCKFILE}"; rm -rf "${CHUNKS_DIR}"' EXIT

# ── Setup ──────────────────────────────────────────────────
mkdir -p "${SCANS_DIR}" "${OUTPUT_DIR}" "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/nightly_${DATE}.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "=========================================="
echo "ARGUS Nightly Batch — ${TIMESTAMP}"
echo "  Batch: ${BATCH_SIZE} | Workers: ${WORKERS} | Steps: ${MAX_STEP}"
echo "=========================================="

# ── Preflight ──────────────────────────────────────────────
if [ ! -f "${LEADS_CSV}" ]; then
    echo "ERROR: ${LEADS_CSV} not found."
    echo "Upload: scp master.csv root@VPS:${LEADS_CSV}"
    exit 1
fi
if [ ! -f "${ARGUS_DIR}/.env" ]; then
    echo "ERROR: .env missing. Run: cp .env.example .env && nano .env"
    exit 1
fi

# ── Step 1: Prepare batch ──────────────────────────────────
echo ""
echo "[1/4] Preparing batch..."
cd "${ARGUS_DIR}"

PREP_EXIT=0
${VENV} ops/prepare_batch.py \
    --leads "${LEADS_CSV}" \
    --scans "${SCANS_DIR}" \
    --batch-size "${BATCH_SIZE}" \
    --workers "${WORKERS}" \
    --output-dir "${CHUNKS_DIR}" \
    || PREP_EXIT=$?

if [ "${PREP_EXIT}" -eq 2 ]; then
    echo "All leads scanned. Done!"
    exit 0
elif [ "${PREP_EXIT}" -ne 0 ]; then
    echo "ERROR: Batch prep failed (exit ${PREP_EXIT})"
    exit 1
fi

CHUNK_COUNT=$(ls -1 "${CHUNKS_DIR}"/chunk_*.csv 2>/dev/null | wc -l)
[ "${CHUNK_COUNT}" -eq 0 ] && echo "No chunks. Exiting." && exit 0

# ── Step 2: Parallel scanning ──────────────────────────────
echo ""
echo "[2/4] Scanning ${CHUNK_COUNT} chunks..."

SCAN_START=$(date +%s)
PIDS=()
WORKER_LOGS="${LOG_DIR}/workers_${DATE}"
mkdir -p "${WORKER_LOGS}"

for chunk_file in "${CHUNKS_DIR}"/chunk_*.csv; do
    chunk_name=$(basename "${chunk_file}" .csv)

    ${VENV} -m argus scan \
        --input "${chunk_file}" \
        --output "${SCANS_DIR}" \
        --steps "${MAX_STEP}" \
        > "${WORKER_LOGS}/${chunk_name}.log" 2>&1 &

    PIDS+=($!)
    echo "  ${chunk_name} → PID $!"
done

echo "  Waiting for ${#PIDS[@]} workers..."

FAILED=0
for pid in "${PIDS[@]}"; do
    wait "${pid}" || FAILED=$((FAILED + 1))
done

SCAN_END=$(date +%s)
SCAN_MIN=$(( (SCAN_END - SCAN_START) / 60 ))
echo "  Done in ${SCAN_MIN} min (${FAILED} failed)"

# ── Step 3: Export ─────────────────────────────────────────
echo ""
echo "[3/4] Exporting..."

BATCH_LEADS="${CHUNKS_DIR}/batch_leads.csv"
OUTPUT_FILE="${OUTPUT_DIR}/instantly_${DATE}.csv"

# Use tonight's batch leads (not full 20K master)
# so each day's CSV has only NEW leads for Instantly
EXPORT_SOURCE="${BATCH_LEADS}"
if [ ! -f "${BATCH_LEADS}" ]; then
    echo "  WARNING: batch_leads.csv missing, using master"
    EXPORT_SOURCE="${LEADS_CSV}"
fi

${VENV} -m argus export \
    --leads "${EXPORT_SOURCE}" \
    --scans "${SCANS_DIR}" \
    --output "${OUTPUT_FILE}"

# ── Step 4: Summary ───────────────────────────────────────
echo ""

TOTAL_SCANS=$(ls -1 "${SCANS_DIR}"/*.json 2>/dev/null | grep -cv "^_" || echo 0)
TOTAL_LEADS=$(${VENV} -c "import csv; r=csv.reader(open('${LEADS_CSV}')); next(r); print(sum(1 for _ in r))")
REMAINING=$((TOTAL_LEADS - TOTAL_SCANS))
[ "${REMAINING}" -lt 0 ] && REMAINING=0

if [ -f "${OUTPUT_FILE}" ]; then
    ROWS=$(${VENV} -c "import csv; r=csv.reader(open('${OUTPUT_FILE}')); next(r); print(sum(1 for _ in r))")
    TIER_A=$(grep -c '"A"' "${OUTPUT_FILE}" 2>/dev/null || echo 0)
    TIER_B=$(grep -c '"B"' "${OUTPUT_FILE}" 2>/dev/null || echo 0)

    echo "=========================================="
    echo "  ${DATE} | ${SCAN_MIN}min | ${FAILED} errors"
    echo "  Tonight:  ${ROWS} rows (A:${TIER_A} B:${TIER_B})"
    echo "  Progress: ${TOTAL_SCANS}/${TOTAL_LEADS} scanned"
    echo "  Left:     ${REMAINING} (~$((REMAINING / BATCH_SIZE)) nights)"
    echo "  File:     ${OUTPUT_FILE}"
    echo "=========================================="
fi

echo "Done at $(date '+%H:%M:%S')."
