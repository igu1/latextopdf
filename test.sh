#!/bin/bash

# Port read straight out of src/main.py, so it never drifts from the app.
PORT=$(sed -n 's/^PORT = \([0-9]\+\).*/\1/p' src/main.py)

echo "POSTing q.json to http://localhost:${PORT}/convert"

curl -X POST "http://localhost:${PORT}/convert" \
  -H "Content-Type: application/json" \
  -d @q.json --output test_output.pdf

echo ""
echo "PDF generation complete. Check test_output.pdf"
