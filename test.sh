#!/bin/bash

curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d @q.json --output test_output.pdf 

echo ""
echo "PDF generation complete. Check test_output.pdf"
