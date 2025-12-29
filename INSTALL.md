# Installation and Usage Guide

## Full Installation Command
Run this command to install everything (TeX Live Full, fonts, Lua dependencies, and Python environment):

```bash
sudo apt-get update && sudo apt-get install -y texlive-full curl fonts-noto fonts-noto-cjk fonts-noto-color-emoji fonts-indic fonts-sil-lateef fonts-smc-rachana luarocks liblua5.1-0-dev python3-pip python3-venv && sudo luarocks install dkjson --lua-version 5.1 && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
```

## Full Uninstallation Command
Run this command to remove all TeX Live packages, configuration, the virtual environment, and Lua dependencies:

```bash
sudo apt-get purge -y "texlive*" "tex-common" "fonts-noto*" "fonts-indic" "fonts-sil-lateef" "fonts-smc-rachana" "luarocks" "liblua5.1-0-dev" && sudo apt-get autoremove -y && sudo apt-get autoclean && sudo rm -rf /usr/local/texlive /var/lib/texmf /etc/texmf ~/.texlive* venv/
```

## Detailed Installation Steps
- OS: Ubuntu/Debian based (tested on Linux Mint 22.1)
- LaTeX: TeX Live Full
- Python: 3.9+
- Lua: 5.1 with LuaRocks

## Installation Steps

### 1. Install System Dependencies
Install TeX Live Full, required fonts, and development libraries:
```bash
sudo apt-get update
sudo apt-get install -y \
    texlive-full \
    curl \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-indic \
    fonts-sil-lateef \
    fonts-smc-rachana \
    luarocks \
    liblua5.1-0-dev \
    python3-pip \
    python3-venv
```

### 2. Configure Lua and dkjson
Install the `dkjson` library for Lua 5.1 (required by the LaTeX templates):
```bash
sudo luarocks install dkjson --lua-version 5.1
```

### 3. Setup Python Environment
Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Running the Project

### Start the Server
```bash
./venv/bin/uvicorn app:app --host 0.0.0.0 --port 5000
```

### Test Conversion
You can test the API using `curl`:
```bash
curl -X POST http://127.0.0.1:5000/convert \
     -H "Content-Type: application/json" \
     -d @q.json \
     --output test_output.pdf
```

## Minimal Setup Note
The project is configured to run directly on the host system without Docker. All LaTeX compilation is handled by `lualatex`, which is included in the `texlive-full` package.
