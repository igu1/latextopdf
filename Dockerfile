FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    texlive-full \
    curl \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-noto-extra \
    fonts-noto-mono \
    fonts-noto-sans \
    fonts-noto-serif \
    fonts-noto-ui-core \
    fonts-noto-ui-extra \
    fonts-noto-unhinted \
    fonts-lohit-deva \
    fonts-lohit-mlym \
    fonts-sil-abyssinica \
    fonts-sil-arabic \
    fonts-sil-mingzat \
    fonts-sil-padauk \
    fonts-telu \
    fonts-deva \
    fonts-mlym \
    fonts-arabic \
    luarocks \
    && rm -rf /var/lib/apt/lists/*

RUN luarocks install dkjson

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/Photo/Qpbank

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
