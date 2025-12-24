"""
LaTeX compilation services for generating PDF documents
"""

import subprocess
import tempfile
import pathlib
import json
import logging
from typing import Dict, Any

from .image_processor import extract_and_download_urls, process_images
from ..templates.question_template import get_question_latex_template

logger = logging.getLogger(__name__)


def compile_latex(latex_source: str, engine: str = "pdflatex") -> bytes:
    """
    Compile LaTeX source code to PDF
    
    Args:
        latex_source: LaTeX source code
        engine: LaTeX engine to use (pdflatex, lualatex, xelatex)
        
    Returns:
        PDF file as bytes
        
    Raises:
        ValueError: If engine is not supported
        RuntimeError: If compilation fails
    """
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
    """
    Compile a question paper from structured data to PDF
    
    Args:
        question_data: Dictionary containing question paper structure and content
        
    Returns:
        PDF file as bytes
        
    Raises:
        RuntimeError: If compilation fails
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        
        reports_dir = tmpdir / "Reports"
        reports_dir.mkdir()
        
        photo_dir = tmpdir / "Photo" / "Qpbank"
        photo_dir.mkdir(parents=True)
        
        process_images(question_data.get('images', {}), photo_dir)
        
        processed_data = question_data.copy()
        for part in processed_data.get('qp_parts', []):
            for i, content in enumerate(part.get('content', [])):
                processed_content = extract_and_download_urls(content, photo_dir)
                part['content'][i] = processed_content
        
        json_file = reports_dir / "question.json"
        json_file.write_text(json.dumps(processed_data, ensure_ascii=False), encoding="utf-8")
        
        latex_template = get_question_latex_template()
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
