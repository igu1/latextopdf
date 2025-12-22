from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tempfile
import pathlib
import io
import logging
import uvicorn

app = FastAPI(title="LaTeX to PDF Converter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LatexRequest(BaseModel):
    latex: str
    engine: str = "pdflatex"


def compile_latex(latex_source: str, engine: str = "pdflatex") -> bytes:
    valid_engines = {"pdflatex", "lualatex", "xelatex"}
    if engine not in valid_engines:
        raise ValueError(f"Engine must be one of {valid_engines}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        tex_file = tmpdir / "document.tex"
        
        tex_file.write_text(latex_source, encoding="utf-8")
        
        cmd = [
            engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "document.tex",
        ]
        
        for _ in range(2):
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            if proc.returncode != 0:
                error_msg = f"LaTeX compilation failed:\n{proc.stdout}\n{proc.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        
        pdf_file = tmpdir / "document.pdf"
        if not pdf_file.exists():
            raise RuntimeError("PDF was not generated")
        
        return pdf_file.read_bytes()


@app.get("/")
async def root():
    return {"message": "LaTeX to PDF Converter API", "endpoints": ["/convert", "/health"]}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/convert")
async def convert_latex(request: LatexRequest):
    try:
        if not request.latex:
            raise HTTPException(status_code=400, detail="LaTeX source cannot be empty")
        
        logger.info(f"Converting LaTeX using {request.engine}")
        
        pdf_bytes = compile_latex(request.latex, request.engine)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=output.pdf"}
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Compilation timed out")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
