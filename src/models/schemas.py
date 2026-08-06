"""
Pydantic models and data schemas for the LaTeX to PDF converter
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


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
    images: Optional[Dict[str, str]] = None
    # Paper-level layout direction, sent by the portal's "RTL Paper" checkbox.
    # True  -> the entire question part is typeset right-to-left.
    # False -> left-to-right (content already wrapped in \begin{Arabic} by the
    #          caller still renders RTL, so this is a safe default).
    rtl: Optional[bool] = False

    # NOTE: this service no longer password-protects PDFs. It always returns an
    # unprotected file so the portal's "View" actions can open it; the portal
    # applies the password at download time. A `password` field sent by an
    # older caller is simply ignored.
