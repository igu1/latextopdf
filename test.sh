#!/bin/bash

# Port resolution, most specific first:
#   API_PORT=5099 ./test.sh   - explicit override
#   HOST_PORT from .env       - what docker compose published on this machine
#   PORT from .env            - a plain `python -m src.main` run
[ -f .env ] && set -a && . ./.env && set +a
API_PORT="${API_PORT:-${HOST_PORT:-${PORT:-5000}}}"

echo "POSTing q.json to http://localhost:${API_PORT}/convert"

curl -X POST "http://localhost:${API_PORT}/convert" \
  -H "Content-Type: application/json" \
  -d @q.json --output test_output.pdf

echo ""
echo "PDF generation complete. Check test_output.pdf"
