"""
Runtime configuration, read once from the environment (and from .env if present).

Every entry point - `python -m src.main`, wsgi.py, the uvicorn CLI in the
Dockerfile - takes its port from here, so changing it is a one-line edit in .env
and never a hunt through five files.
"""

import os

from dotenv import load_dotenv

# override=False: a variable already exported in the shell, or injected by
# docker compose, wins over the file. That is what makes the same .env safe to
# keep in the image and still overridable per deployment.
load_dotenv(override=False)

# One number for both sides of the Docker port mapping, so the port you set is
# the port you connect to. 5055 rather than 5000 because the portal's ASP.NET
# process already owns 127.0.0.1:5000 on Windows.
PORT = int(os.getenv("PORT", "5055"))

# Not configurable: inside a container the port has to be bound on all
# interfaces or Docker's published port reaches nothing.
HOST = "0.0.0.0"
