FROM python:3.9-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    texlive-full \
    curl \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-indic \
    fonts-sil-lateef \
    fonts-smc-rachana \
    luarocks \
    liblua5.3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN luarocks install dkjson

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/Photo/Qpbank

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
