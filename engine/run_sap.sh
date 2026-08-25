#!/usr/bin/env bash
# Run the full SAP GL/Bank matching pipeline: match_workbook.py then
# build_analysis_tab.py, chained, with the SAP defaults validated on the
# December 2025 data (Matching ID as primary code column, Matching/Group ID
# mirrored, Match Status flipped to Matched, date window 15, max 10 items).
#
# Usage:
#   ./run_sap.sh <input.xlsx> <prefix> <period> [output_dir]
#
# Example:
#   ./run_sap.sh ~/workspace/ReconcilePro_Matching_202512.xlsx SAP 2025-12 ~/workspace/output
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: $0 <input.xlsx> <prefix> <period> [output_dir]" >&2
  echo "Example: $0 ReconcilePro_Matching_202512.xlsx SAP 2025-12" >&2
  exit 1
fi

INPUT="$1"
PREFIX="$2"
PERIOD="$3"
OUTDIR="${4:-$(dirname "$INPUT")}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$INPUT" ]; then
  echo "Input file not found: $INPUT" >&2
  exit 1
fi

BASENAME="$(basename "$INPUT" .xlsx)"
FINAL="$OUTDIR/${BASENAME}_Matched.xlsx"

mkdir -p "$OUTDIR"

# SAP's raw export used to mix multiple source systems in one sheet (an
# upstream query issue) -- filter defensively for SAP only. Other engines'
# raw exports are already single-engine, so no filter is applied for them.
FILTER_ARGS=()
if [ "${PREFIX^^}" = "SAP" ]; then
  FILTER_ARGS=(--gl-filter-col "Source" --gl-filter-value "SAP")
fi

echo "=== Step 1/2: matching engine ==="
python3 "$SCRIPT_DIR/match_workbook.py" \
  --input "$INPUT" \
  --output "$FINAL" \
  "${FILTER_ARGS[@]}" \
  --id-col "Matching ID" \
  --secondary-id-col "Matching/Group ID" \
  --engine-col "Matched By Engine" \
  --engine-tag "Manual" \
  --status-col "Match Status" \
  --status-value "Matched" \
  --prefix "$PREFIX" --period "$PERIOD" \
  --max-items 10 --date-window 15 --cap-entries 2000000

echo
echo "=== Step 2/2: analysis tab ==="
python3 "$SCRIPT_DIR/build_analysis_tab.py" \
  --input "$FINAL" \
  --output "$FINAL" \
  --bank-sheet Bank --source-label "$PREFIX"

echo
echo "Done: $FINAL"
