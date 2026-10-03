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

from .asymptote import run_asymptote
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


# Where the watermark is written, relative to the LaTeX run's directory. The
# name is fixed: nothing but the institution logo is ever written to it.
LOGO_FILE = "institution-logo.png"

# What \includegraphics can actually read, by the bytes a file starts with.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


async def _prepare_logo(logo: Any, photo_dir, qp_code: str) -> str:
    """
    Writes the institution logo next to the paper and returns its path.

    Returns "" for a paper with no logo, and for a logo that could not be
    used - a 404 on the URL, a data URL that is not an image, a file the
    service cannot read. A paper is never failed over its watermark: the
    questions are the paper, and the crest is decoration.
    """
    source = (logo or "").strip() if isinstance(logo, str) else ""
    if not source:
        return ""

    await process_images({LOGO_FILE: source}, photo_dir)

    written = photo_dir / LOGO_FILE
    if not written.exists() or written.stat().st_size == 0:
        logger.warning("Institution logo could not be read for %s - the paper "
                       "will print without a watermark", qp_code)
        return ""

    # What was actually written, from its first bytes rather than its name.
    #
    # This is the one check that has to be here. \includegraphics picks its
    # reader by file EXTENSION, so a JPEG written as .png - or an HTML page
    # from a server that answers 200 for a file it does not have - is not a
    # picture that prints badly, it is a LaTeX error that takes the whole
    # paper down with it. Eight bytes is cheap insurance against losing a
    # question paper.
    head = written.read_bytes()[:8]
    if head.startswith(PNG_MAGIC):
        path = LOGO_FILE
    elif head.startswith(JPEG_MAGIC):
        # Right picture, wrong name: give it the one \includegraphics needs.
        path = LOGO_FILE.rsplit(".", 1)[0] + ".jpg"
        written.replace(photo_dir / path)
    else:
        logger.warning("Institution logo for %s is not a PNG or JPEG (starts "
                       "%r) - printing without a watermark", qp_code, head[:4])
        written.unlink(missing_ok=True)
        return ""

    logger.info("Institution watermark ready for %s", qp_code)
    return "./Photo/Qpbank/" + path


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
    logger.info(f"Starting question paper compilation for: {qp_code}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        
        reports_dir = tmpdir / "Reports"
        reports_dir.mkdir()
        
        photo_dir = tmpdir / "Photo" / "Qpbank"
        photo_dir.mkdir(parents=True)
        
        logger.info(f"Processing images for question paper: {qp_code}")
        await process_images(question_data.get('images', {}), photo_dir)
        
        processed_data = question_data.copy()

        # The institution's watermark, if one was sent. It goes through the
        # same writer as the question pictures - so a data URL, a URL or a
        # path all work - and what reaches the template is the FILE PATH, not
        # the picture: question.json is read by the paper itself, and a
        # megabyte of base64 in it would be written into the LaTeX run for no
        # reason. A logo that did not arrive leaves the key empty, and the
        # template then prints no watermark at all.
        processed_data['logo'] = await _prepare_logo(
            question_data.get('logo'), photo_dir, qp_code)
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

            # Between the two passes, because that is the only place it works:
            # the first pass writes each \begin{asy} figure out as question-N.asy
            # without drawing it, and the second pass includes the PDFs made
            # here. A paper with no Asymptote figure in it finds no files and
            # runs nothing. An error is logged rather than raised - one figure
            # that will not draw must not cost the whole paper, and it is the
            # same figure the teacher already previewed through /render-figure.
            if i == 0:
                asy = run_asymptote(tmpdir)
                for message in asy.errors:
                    logger.error("Asymptote figure failed in %s: %s",
                                 qp_code, message)

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
        
        # This service always returns an UNPROTECTED PDF. Password protection is
        # applied in the portal at download time, so the same generated file can
        # be opened by the "View" actions without a password.
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes
