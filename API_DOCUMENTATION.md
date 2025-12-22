# LaTeX to PDF API

**Base URL:** `http://localhost:5000`

## Endpoints

### GET `/`
API information

### GET `/health`
Check service status

**Response:**
```json
{"status": "healthy"}
```

### POST `/convert`
Convert LaTeX to PDF

**Request:**
```json
{
  "latex": "LaTeX source code",
  "engine": "pdflatex"  // optional: pdflatex, lualatex, xelatex
}
```

**Response:** PDF file (binary)

**Status Codes:**
- `200` - Success
- `400` - Bad request
- `408` - Timeout
- `422` - Compilation failed
- `500` - Server error

## Usage Examples

**cURL:**
```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d '{"latex": "\\documentclass{article}\\begin{document}Hello\\end{document}"}' \
  --output output.pdf
```

**Python:**
```python
import requests
response = requests.post("http://localhost:5000/convert", 
                        json={"latex": "LaTeX code"})
with open("output.pdf", "wb") as f:
    f.write(response.content)
```

**JavaScript:**
```javascript
fetch('http://localhost:5000/convert', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({latex: 'LaTeX code'})
})
.then(r => r.blob())
.then(blob => download(blob, 'output.pdf'))
```
