FROM python:3.12-slim

# Minimal TeX Live set for the LuaLaTeX question-paper template
# (replaces texlive-full: ~600MB download instead of ~5.7GB with docs)
#
# texlive-science carries mhchem (\ce{H2SO4 + 2NaOH -> ...}) and siunitx
# (\SI{9.8}{\meter\per\second}). mhchem matters most: it is the one chemistry
# feature the BROWSER preview can already draw, because index.html loads
# MathJax's mhchem extension - so without it here, a chemical equation rendered
# correctly on screen and then printed as nothing at all, with no error on any
# path. Which packages a question may use is recorded in the portal's
# ClientApp/src/app/qp-editor/latex-capabilities.ts; keep the two in step.
RUN apt-get -o Acquire::Retries=5 update \
    && DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
    texlive-luatex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-pictures \
    texlive-science \
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
    # /render-figure turns a single diagram into an SVG for the portal's
    # preview, so a figure the browser's own TeX engine cannot draw - a circuit,
    # a chemical structure, a hatched fill, anything with Malayalam in it - is
    # still shown to the teacher exactly as it will print, because it is drawn
    # by this LuaLaTeX from this preamble.
    #
    # mutool rather than ghostscript: dvisvgm reads PDF only through Ghostscript
    # older than 10.01 or through mutool, and Debian 13 ships Ghostscript 10.05,
    # which it refuses. mutool is one package against ghostscript's twenty-three
    # and sidesteps the version problem entirely.
    dvisvgm \
    mupdf-tools \
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

# The port the service runs on. Overridable at build time
# (--build-arg PORT=...) and at run time (-e PORT=... / .env via compose),
# because EXPOSE and CMD below both read it rather than hardcoding a number.
ARG PORT=5055
ENV PORT=${PORT}

EXPOSE ${PORT}

# Shell form (sh -c) rather than the exec array: an array CMD is passed straight
# to execve and would hand uvicorn the literal string "$PORT".
#
# --host is fixed at 0.0.0.0: inside a container the port has to be bound on all
# interfaces or Docker's published port reaches nothing.
CMD ["sh", "-c", "exec uvicorn src.main:app --host 0.0.0.0 --port $PORT"]
