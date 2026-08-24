"""
Runtime configuration, read once from the environment (and from .env if present).

Every entry point - `python -m src.main`, wsgi.py, the uvicorn CLI in the
Dockerfile - takes its host and port from here, so changing the port is a
one-line edit in .env and never a hunt through five files.
"""

import os

from dotenv import load_dotenv

# override=False: a variable already exported in the shell, or injected by
# docker compose, wins over the file. That is what makes the same .env safe to
# keep in the image and still overridable per deployment.
load_dotenv(override=False)

# 0.0.0.0 rather than 127.0.0.1: inside a container the port has to be bound on
# all interfaces or Docker's published port reaches nothing.
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

# Only read by docker-compose.yml (host side of the port mapping); listed here
# so the full set of knobs is visible in one place.
HOST_PORT = int(os.getenv("HOST_PORT", str(PORT)))
