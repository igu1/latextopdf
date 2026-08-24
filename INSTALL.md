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

| Variable | Default | Meaning |
|----------|---------|---------|
| `PORT`   | `5055`  | The port the service runs on. |

That is the whole file. `PORT` is used on both sides of the Docker port mapping,
so the number you set is the number you connect to - no separate host/container
port to keep in step.

To change it, edit the one line and restart:

```
PORT=8000
```

Nothing else needs touching: `src/config.py` feeds the local run, and docker
compose feeds the same value into the port mapping, the build arg, and the
container environment. Under Docker no rebuild is needed - the runtime value
overrides the one baked into the image.

Pick a port that is free on the machine, since it is bound on the host too.
5055 is the default rather than 5000 because the portal's ASP.NET process
already owns 127.0.0.1:5000 on Windows.

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
./venv/bin/uvicorn src.main:app --host 0.0.0.0 --port "$PORT" --reload
```

### With Docker
```bash
docker compose up --build
```

### Test Conversion
```bash
./test.sh
```
`test.sh` takes the port from `.env`. Override it for a one-off:
`PORT=8000 ./test.sh`.

Or by hand:
```bash
curl -X POST http://127.0.0.1:5055/convert \
     -H "Content-Type: application/json" \
     -d @q.json \
     --output test_output.pdf
```

## Minimal Setup Note
The project is configured to run directly on the host system without Docker. All LaTeX compilation is handled by `lualatex`, which is included in the `texlive-full` package.
