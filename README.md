# LaTeX to PDF Converter API

A FastAPI-based service that converts LaTeX content to PDF documents, specifically designed for generating question papers.

## System Requirements

### Ubuntu/Debian Packages

```bash
# Core LaTeX distribution
sudo apt update
sudo apt install -y texlive-full

# OR for minimal installation:
sudo apt install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-luatex \
    texlive-polyglossia \
    texlive-fontspec \
    texlive-tabularray \
    texlive-tikz \
    texlive-luacode \
    texlive-multicol \
    texlive-lastpage \
    texlive-booktabs \
    texlive-multirow \
    texlive-science \
    texlive-pictures

# Font packages for multi-language support
sudo apt install -y \
    fonts-lateef \
    fonts-mangal \
    fonts-rachana \
    fonts-sil-abyssinica \
    fonts-sil-nuosu

# System dependencies
sudo apt install -y curl wget git python3-pip
```

### Python Dependencies

Install from `requirements.txt`:
```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.12.5 python-multipart==0.0.6
```

## Quick Installation

Run the installation script:
```bash
chmod +x install_packages.sh
./install_packages.sh
```

## Usage

### Start the server
```bash
python3 app.py
```

The server will start on `http://0.0.0.0:5000`

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /convert` - Convert LaTeX question paper to PDF

### Example Request

```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d @q.json \
  --output output.pdf
```

## Key LaTeX Packages Used

- **geometry**: Page layout and margins
- **polyglossia**: Multi-language support (Hindi, Malayalam, Arabic)
- **fontspec**: Font management
- **tabularray**: Advanced tables
- **tikz**: Graphics and diagrams
- **luacode**: Lua scripting within LaTeX
- **amsmath**: Mathematical formulas
- **graphicx**: Image inclusion
- **enumitem**: List customization
- **booktabs**: Professional tables
- **multirow**: Multi-row table cells

## Troubleshooting

### Common Issues

1. **Missing `luabidi.sty` package**
   ```bash
   sudo apt install -y texlive-arab
   ```

2. **Font not found errors**
   ```bash
   sudo apt install -y fonts-lateef fonts-mangal fonts-rachana
   ```

3. **Permission denied errors**
   ```bash
   sudo chmod +x install_packages.sh
   ```

### Verification Commands

```bash
# Check LaTeX installation
pdflatex --version
lualatex --version

# Check Python packages
python3 -c "import fastapi, uvicorn, pydantic; print('All OK')"

# Test API
curl http://localhost:5000/health
```

## Configuration

The server is configured to:
- Listen on all interfaces (`0.0.0.0:5000`)
- Accept cross-origin requests (CORS enabled)
- Handle forwarded requests from proxies
- Timeout after 60 seconds for LaTeX compilation
