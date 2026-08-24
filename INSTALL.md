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

## Configuration

All runtime settings live in a `.env` file in the project root. Start from the
template:

```bash
cp .env.example .env
```

| Variable    | Default   | Meaning |
|-------------|-----------|---------|
| `PORT`      | `5000`    | Port the service listens on (inside the container, under Docker). |
| `HOST`      | `0.0.0.0` | Interface to bind. Use `127.0.0.1` to keep a local run off the network. |
| `HOST_PORT` | `5055`    | Docker only: the port published on your machine. |

To change the port, edit that one line - `PORT=8000` - and restart. Nothing else
needs touching: `src/config.py` feeds the local run, and docker compose feeds the
same values into the port mapping, the build arg, and the container environment.

A real environment variable always beats the file, so a one-off run needs no edit:

```bash
PORT=8000 ./venv/bin/python -m src.main
```

`.env` is gitignored (it is per-machine); `.env.example` is committed as the
reference.

## Running the Project

### Start the Server
```bash
./venv/bin/python -m src.main
```

Or through the uvicorn CLI, if you want `--reload`:
```bash
set -a && . ./.env && set +a
./venv/bin/uvicorn src.main:app --host "$HOST" --port "$PORT" --reload
```

### With Docker
```bash
docker compose up --build
```
The service is then reachable on `HOST_PORT` (5055 by default), not `PORT`.

### Test Conversion
```bash
./test.sh
```
`test.sh` takes the port from `.env`, preferring `HOST_PORT` (Docker) over `PORT`
(local run). Override it for a one-off: `API_PORT=8000 ./test.sh`.

Or by hand:
```bash
curl -X POST http://127.0.0.1:$PORT/convert \
     -H "Content-Type: application/json" \
     -d @q.json \
     --output test_output.pdf
```

## Minimal Setup Note
The project is configured to run directly on the host system without Docker. All LaTeX compilation is handled by `lualatex`, which is included in the `texlive-full` package.
