FROM python:3.12-slim

# Minimal TeX Live set for the LuaLaTeX question-paper template
# (replaces texlive-full: ~600MB download instead of ~5.7GB with docs)
RUN apt-get -o Acquire::Retries=5 update \
    && DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
    texlive-luatex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-pictures \
    texlive-lang-arabic \
    texlive-lang-other \
    fonts-sil-lateef \
    fonts-indic \
    fonts-smc-rachana \
    fonts-noto-core \
    fontconfig \
    lua-dkjson \
    qpdf \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Let LuaTeX's require() find the Debian-packaged dkjson (no luarocks needed)
ENV LUA_PATH="/usr/share/lua/5.3/?.lua;;"

# Pre-build the luaotfload font database so the first request is fast
# and font lookups (Lateef/Lohit/Rachana) are guaranteed to resolve
RUN luaotfload-tool --update --force

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/Photo/Qpbank

EXPOSE 5008

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5008"]
