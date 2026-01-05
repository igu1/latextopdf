"""
Pydantic models and data schemas for the LaTeX to PDF converter
"""

from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime


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
    password: Optional[bool] = False
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v):
        if v is True:
            return True
        return False
