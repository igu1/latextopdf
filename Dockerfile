FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
    texlive-fonts-extra texlive-luatex texlive-xetex python3 python3-pip curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -s /bin/false appuser

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py wsgi.py ./
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
HEALTHCHECK CMD curl -f http://localhost:5000/health
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
