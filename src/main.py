"""
Main FastAPI application for LaTeX to PDF converter
"""

import logging
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models.schemas import QuestionPaperRequest
from .services.latex_compiler import compile_question_paper
from .utils.helpers import setup_logging, create_pdf_response

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="LaTeX to PDF Converter", version="1.0.0")

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
        "endpoints": ["/convert", "/health"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


@app.post("/convert")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
