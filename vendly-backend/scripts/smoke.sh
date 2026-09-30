#!/usr/bin/env bash
# Runs the whole must-not-cut path with curl. Requires WEBHOOK_SKIP_SIGNATURE=true.
# Usage: API=http://127.0.0.1:8000/api/v1 ./scripts/smoke.sh
set -euo pipefail
API="${API:-http://127.0.0.1:8000/api/v1}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "1) Create event + vendor"
EVENT=$(curl -sf -X POST "$API/events" -H 'content-type: application/json' -d @"$DIR/event.json")
echo "$EVENT"
EVENT_ID=$(echo "$EVENT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
VENDOR_ID=$(echo "$EVENT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["vendors"][0]["id"])')

echo "2) Send WhatsApp confirmation"
curl -sf -X POST "$API/notify/send" -H 'content-type: application/json' \
  -d "{\"event_id\": $EVENT_ID}"
echo

echo "3) Simulate vendor tapping YES"
python3 "$DIR/simulate_reply.py" --vendor "$VENDOR_ID" --answer YES --base-url "${API%/api/v1}"

echo "4) Confirm the status flipped"
curl -sf "$API/events/$EVENT_ID/status?since=1"
echo

echo "5) Disburse the deposit"
curl -sf -X POST "$API/budget/$VENDOR_ID/disburse" -H 'content-type: application/json' \
  -d '{"kind": "deposit"}'
echo

echo "6) Full budget view"
curl -sf "$API/events/$EVENT_ID/budget"
echo
