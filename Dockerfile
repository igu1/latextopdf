FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-luatex \
    texlive-xetex \
    texlive-lang-arabic \
    texlive-lang-other \
    fonts-lohit-deva \
    fonts-lohit-deva-marathi \
    fonts-lohit-deva-nepali \
    fonts-smc \
    fonts-smc-rachana \
    fonts-arabeyes \
    fonts-hosny-amiri \
    fonts-farsiweb \
    luarocks \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN luarocks install dkjson \
    && luarocks install luafilesystem

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.txt

COPY app.py .
COPY wsgi.py .

RUN chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2", "--timeout", "60", "--max-requests", "1000", "--max-requests-jitter", "50"]
