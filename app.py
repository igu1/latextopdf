from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import subprocess
import tempfile
import pathlib
import io
import json
import logging
import uvicorn

app = FastAPI(title="LaTeX to PDF Converter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LatexRequest(BaseModel):
    latex: str
    engine: str = "pdflatex"


class QuestionPart(BaseModel):
    part_name: str
    part_title: str
    part_description: str
    content: List[str]
    footer: str


class QuestionPaperRequest(BaseModel):
    qp_code: str
    qp_name: str
    qp_stream: str
    course_name: str
    admission_year: str
    time: str
    max_marks: str
    qp_parts: List[QuestionPart]


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


def compile_question_paper(question_data: Dict[str, Any]) -> bytes:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        
        reports_dir = tmpdir / "Reports"
        reports_dir.mkdir()
        
        json_file = reports_dir / "question.json"
        json_file.write_text(json.dumps(question_data, ensure_ascii=False), encoding="utf-8")
        
        latex_template = r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=1.4cm]{geometry}
\usepackage{zref-totpages}
\usepackage{array}
\usepackage{polyglossia}
\usepackage{fontspec}
\usepackage{tabularray}
\usepackage{tikz}
\usepackage{enumitem}
\usepackage{luacode}
\usepackage{luapackageloader}
\usepackage{multicol}
\usepackage{graphicx}
\usepackage{lastpage}
\usepackage{array}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}

\setdefaultlanguage{english}
\setotherlanguage{hindi}
\setotherlanguage{malayalam}
\setotherlanguage{arabic}

\newfontfamily\arabicfont[Script=Arabic,Scale=1.3]{Lateef}
\newfontfamily\devanagarifont[Script=Devanagari,Scale=1.3]{Mangal}
\newfontfamily\malayalamfont[Script=Malayalam,Scale=1.3]{Rachana}
\newfontfamily\hindifont[Script=Devanagari]{Mangal}


\begin{document}
\begin{luacode*}
    json = require('json')
    lfs = require('lfs')
    local jsonPath = lfs.currentdir() .. "/Reports/question.json"
    print(jsonPath)

    function readAll(file)
        local f = assert(io.open(file, "rb"))
        io.input(f)
        local content = f:read("*all")
        f:close()
        return content
    end

    local contents = readAll(jsonPath)
    local data = json.decode(contents)
    print(contents)

    tex.print(data.qp_code .. "\\hfill  Name .............................")
    tex.print("\\begin{flushright}")
    tex.print("Reg.No .............................\\\\")
    tex.print("\\end{flushright}")
    tex.print("\\begin{center}")
    
    tex.print("\\begin{minipage}{5in}")
    tex.print("\\centering")
    tex.print(data.qp_name)
    tex.print("\\end{minipage} \\\\")
    
    tex.print("\\vspace{0.3cm}")
    tex.print("\\end{center}")
    tex.print("Time : " .. data.time .. " \\hfill " .. "Max marks : " .. data.max_marks)
    tex.print("\\begin{enumerate}")
    for i, row in ipairs(data.qp_parts) do
        tex.print("\\begin{center}")
        tex.print("\\textbf{" .. row.part_name .. "} \\\\")
        tex.print("\\texttt{" .. row.part_description .. "} \\\\")
        tex.print("\\end{center}")
        for j, part in ipairs(row.content) do
            if string.find(part, "\\begin{tabular}") then
                tex.print(part)
            else
                tex.print(part .. " \\\\")
                tex.print(" \\\\")
            end
        end

        tex.print("\\begin{flushright}")
        tex.print("\\texttt{\\textbf{" .. row.footer .. "}} \\\\")
        tex.print("\\end{flushright}")

    end
    tex.print("\\end{enumerate}")

\end{luacode*}
\end{document}
'''
        
        tex_file = tmpdir / "question.tex"
        tex_file.write_text(latex_template, encoding="utf-8")
        
        cmd = [
            "lualatex",
            "-interaction=nonstopmode",
            "question.tex",
        ]
        
        for i in range(2):
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            
            if i == 1 and proc.returncode != 0:
                logger.warning(f"LuaLaTeX returned non-zero exit code: {proc.returncode}")
        
        pdf_file = tmpdir / "question.pdf"
        if not pdf_file.exists():
            error_msg = f"PDF was not generated - file does not exist after compilation\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        pdf_bytes = pdf_file.read_bytes()
        if len(pdf_bytes) == 0:
            error_msg = f"PDF was generated but is empty (0 bytes)\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes


@app.get("/")
async def root():
    return {
        "message": "LaTeX to PDF Converter API",
        "endpoints": ["/convert", "/convert-question-paper", "/health"]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/convert")
async def convert_question_paper(request: QuestionPaperRequest):
    try:
        logger.info(f"Generating question paper PDF for: {request.qp_code}")
        
        question_data = request.model_dump()
        
        pdf_bytes = compile_question_paper(question_data)
        
        filename = f"{request.qp_code}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Compilation timed out")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
