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
