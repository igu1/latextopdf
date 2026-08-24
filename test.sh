#!/bin/bash

# Port comes from .env; override for a one-off with PORT=8000 ./test.sh
# The override is saved first because sourcing .env would otherwise clobber it.
_port_override="$PORT"
[ -f .env ] && set -a && . ./.env && set +a
PORT="${_port_override:-${PORT:-5055}}"

echo "POSTing q.json to http://localhost:${PORT}/convert"

curl -X POST "http://localhost:${PORT}/convert" \
  -H "Content-Type: application/json" \
  -d @q.json --output test_output.pdf

echo ""
echo "PDF generation complete. Check test_output.pdf"
