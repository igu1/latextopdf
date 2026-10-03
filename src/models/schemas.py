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

    # The institution's logo, printed centred on EVERY page under the
    # questions - the portal's "Institution logo" checkbox.
    #
    # Sent the way `images` entries are: a data URL, an http(s) URL or a path
    # the service can read. The portal sends a data URL it has already turned
    # black and white and faded to a light grey, because a watermark that is
    # legible under the text is a decision about the paper, not about the
    # picture, and the browser is where the teacher is.
    #
    # Left out entirely for a paper printed without one. A logo that cannot be
    # read is dropped and the paper prints as if nothing had been sent, which
    # is what an institution with no logo file on disk relies on.
    logo: Optional[str] = None

    # NOTE: this service no longer password-protects PDFs. It always returns an
    # unprotected file so the portal's "View" actions can open it; the portal
    # applies the password at download time. A `password` field sent by an
    # older caller is simply ignored.
