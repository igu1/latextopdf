"""
LaTeX compilation services for generating PDF documents
"""

import subprocess
import tempfile
import pathlib
import json
import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

from .image_processor import extract_and_download_urls, process_images
from ..templates.question_template import get_question_latex_template

logger = logging.getLogger(__name__)


def encrypt_pdf_with_password(pdf_bytes: bytes, password: str) -> bytes:
    """
    Encrypt PDF with password using pdftk or qpdf
    
    Args:
        pdf_bytes: Original PDF bytes
        password: Password to encrypt with
        
    Returns:
        Encrypted PDF bytes
        
    Raises:
        RuntimeError: If encryption fails
    """
    logger.info("Encrypting PDF with password")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        input_pdf = tmpdir / "input.pdf"
        output_pdf = tmpdir / "output.pdf"
        
        input_pdf.write_bytes(pdf_bytes)
        
        # Try qpdf first (more commonly available)
        try:
            cmd = [
                "qpdf",
                "--encrypt", password, password, "128",
                "--print=full", "--modify=full", "--extract=n",
                str(input_pdf), str(output_pdf)
            ]
            
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0 and output_pdf.exists():
                logger.info("PDF encrypted successfully using qpdf")
                return output_pdf.read_bytes()
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("qpdf not available, trying pdftk")
        
        # Try pdftk as fallback
        try:
            cmd = [
                "pdftk",
                str(input_pdf),
                "output", str(output_pdf),
                "user_pw", password,
                "owner_pw", password
            ]
            
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            if proc.returncode == 0 and output_pdf.exists():
                logger.info("PDF encrypted successfully using pdftk")
                return output_pdf.read_bytes()
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("pdftk not available")
        
        # If neither tool is available, return unencrypted PDF
        logger.warning("No PDF encryption tool available, returning unencrypted PDF")
        return pdf_bytes


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
    logger.info(f"Starting LaTeX compilation with engine: {engine}")
    
    valid_engines = {"pdflatex", "lualatex", "xelatex"}
    if engine not in valid_engines:
        logger.error(f"Unsupported LaTeX engine: {engine}")
        raise ValueError(f"Engine must be one of {valid_engines}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        tex_file = tmpdir / "document.tex"
        
        logger.info(f"Writing LaTeX source to temporary file: {tex_file}")
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
            logger.error("PDF file was not generated after compilation")
            raise RuntimeError("PDF was not generated")
        
        pdf_bytes = pdf_file.read_bytes()
        logger.info(f"LaTeX compilation successful, generated PDF: {len(pdf_bytes)} bytes")
        return pdf_bytes


async def compile_question_paper(question_data: Dict[str, Any]) -> bytes:
    """
    Compile a question paper from structured data to PDF
    
    Args:
        question_data: Dictionary containing question paper structure and content
        
    Returns:
        PDF file as bytes
        
    Raises:
        RuntimeError: If compilation fails
    """
    qp_code = question_data.get('qp_code', 'unknown')
    password_enabled = question_data.get('password', False)
    logger.info(f"Starting question paper compilation for: {qp_code}, password protection: {password_enabled}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        
        reports_dir = tmpdir / "Reports"
        reports_dir.mkdir()
        
        photo_dir = tmpdir / "Photo" / "Qpbank"
        photo_dir.mkdir(parents=True)
        
        logger.info(f"Processing images for question paper: {qp_code}")
        await process_images(question_data.get('images', {}), photo_dir)
        
        processed_data = question_data.copy()
        for part in processed_data.get('qp_parts', []):
            for i, content in enumerate(part.get('content', [])):
                processed_content = await extract_and_download_urls(content, photo_dir)
                part['content'][i] = processed_content
        
        logger.info(f"Writing JSON data for question paper: {qp_code}")
        json_file = reports_dir / "question.json"
        json_file.write_text(json.dumps(processed_data, ensure_ascii=False), encoding="utf-8")
        
        latex_template = get_question_latex_template()
        tex_file = tmpdir / "question.tex"
        tex_file.write_text(latex_template, encoding="utf-8")
        
        logger.info(f"Starting LuaLaTeX compilation for question paper: {qp_code}")
        
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
        
        # Apply password protection if requested
        if password_enabled:
            current_date = datetime.now().strftime("%Y%m%d")
            logger.info(f"Applying password protection with date-based password: {current_date}")
            pdf_bytes = encrypt_pdf_with_password(pdf_bytes, current_date)
        
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes
