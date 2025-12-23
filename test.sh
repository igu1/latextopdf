#!/bin/bash

curl -X POST http://31.97.228.140:5013/convert \
  -H "Content-Type: application/json" \
  -d @q.json --output test_output.pdf 

echo ""
echo "PDF generation complete. Check test_output.pdf"
