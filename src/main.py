"""
Main FastAPI application for LaTeX to PDF converter
"""

import base64
import logging
import os
import secrets
import subprocess
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from .models.schemas import QuestionPaperRequest
from .services.latex_compiler import compile_question_paper
from .services.figure_renderer import (
    FigureError, render_figure_png, render_figure_svg)
from .utils.helpers import setup_logging, create_pdf_response

# The one place the port is defined. The Dockerfile starts the app with
# `python -m src.main`, so the container listens on whatever is set here;
# only docker-compose.yml's port mapping has to be changed alongside it.
PORT = 5013

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="LaTeX to PDF Converter", version="1.0.0")

# The key a caller must present to compile anything.
#
# Set API_KEY in the environment (docker-compose passes it through) and every
# request to /convert and /render-figure must carry the same value in the
# X-API-Key header. Leave it unset and the service stays open, which is what
# makes the rollout safe: deploy the callers with the key first, then set this
# and restart - no window where a paper fails to generate.
#
# / and /health stay open either way, so uptime checks need no secret.
API_KEY = os.environ.get("API_KEY", "").strip()


def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> None:
    """Rejects a caller that cannot name the key, once one is configured."""
    if not API_KEY:
        return

    # compare_digest, not ==: a plain comparison returns as soon as two
    # characters differ, and the time it takes tells an attacker how much of
    # the key they have guessed.
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        logger.warning("Rejected a request with no valid X-API-Key")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "LaTeX to PDF Converter API",
        "endpoints": ["/convert", "/render-figure", "/health"]
    }


class FigureRequest(BaseModel):
    """One diagram's LaTeX - a tikzpicture, circuitikz, chemfig and so on."""
    latex: str = Field(..., min_length=1, max_length=20_000)
    # png when the picture is going to be KEPT in the question: \includegraphics
    # takes PNG, JPG or PDF and never SVG. svg for a preview that is thrown away.
    format: str = Field("svg", pattern="^(svg|png)$")
    # 300 for print. At 96 the thin lines of a circuit diagram break up.
    dpi: int = Field(300, ge=72, le=600)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


@app.post("/convert", dependencies=[Depends(require_api_key)])
async def convert_question_paper(request: QuestionPaperRequest):
    """
    Convert question paper data to PDF
    
    Args:
        request: QuestionPaperRequest containing paper data
        
    Returns:
        PDF file as streaming response
        
    Raises:
        HTTPException: If compilation fails or times out
    """
    logger.info(f"Received PDF conversion request for: {request.qp_code}")
    
    try:
        question_data = request.model_dump()
        pdf_bytes = await compile_question_paper(question_data)
        
        filename = f"{request.qp_code}.pdf"
        
        logger.info(f"Successfully generated PDF: {filename}")
        
        return create_pdf_response(pdf_bytes, filename)
    
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Compilation timed out")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render-figure", dependencies=[Depends(require_api_key)])
async def render_figure(request: FigureRequest):
    """
    Draw one diagram and return it as SVG.

    For figures the portal's in-browser TeX engine cannot draw - circuits,
    chemical structures, hatched fills, Indic labels. Drawn by the same
    LuaLaTeX and the same preamble as the printed paper, so what the teacher
    sees here is what the paper will carry.

    Returns:
        {"svg": "<svg ...>...</svg>"}

    Raises:
        HTTPException 422 with a message written for the teacher, never a
        LuaLaTeX log.
    """
    logger.info("Figure render requested (%d chars, %s)",
                len(request.latex), request.format)

    try:
        if request.format == "png":
            png = render_figure_png(request.latex, request.dpi)
            # base64 rather than raw bytes: the editor drops it straight into an
            # <img src="data:image/png;base64,...">, which is the same shape a
            # pasted screenshot already takes through the save path.
            return {
                "png": base64.b64encode(png).decode("ascii"),
                "dataUrl": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
                "dpi": request.dpi,
            }

        return {"svg": render_figure_svg(request.latex)}

    except FigureError as e:
        # A figure that cannot be drawn is the teacher's to fix, not a fault of
        # the service - so it is a 422 with something they can act on, and it is
        # not logged as an error.
        logger.info("Figure could not be drawn: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error("Figure render failed: %s", e)
        raise HTTPException(status_code=500, detail="Could not draw the figure.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, workers=2)

