"""
Renders one diagram to SVG for the portal's on-screen preview.

WHY THIS EXISTS

The portal previews diagrams with TikzJax, a prebuilt TeX engine in the
browser. Its package set is fixed and cannot be extended, so a circuit
(circuitikz), a chemical structure (chemfig) or a hatched fill (pattern=) has
no preview at all, and any label in an Indic script comes out blank because the
engine carries none of those fonts. Those same figures print perfectly. A
teacher writing one therefore had no way to check it before the paper was
printed - which is the exact shape of failure this codebase has hit repeatedly.

The figure here is typeset by the SAME LuaLaTeX, from the SAME preamble, as the
printed paper. That is the whole point: the preview cannot drift from the paper,
because there is only one definition of how a figure is drawn. Add a package to
question_template.py and it appears in both at once.
"""

import logging
import pathlib
import re
import subprocess
import tempfile
from typing import Tuple

from ..templates.question_template import get_question_latex_template

logger = logging.getLogger(__name__)

# A figure is one picture, not a paper. Anything past this is a mistake or an
# attempt to use the endpoint as a general LaTeX compiler.
MAX_SOURCE_CHARS = 20_000

# LuaLaTeX loading this preamble takes 2-4s measured; a figure that has not
# finished by then is not going to.
COMPILE_TIMEOUT_S = 45
CONVERT_TIMEOUT_S = 30

# Refused outright: these reach outside the figure. \write18 runs shell
# commands, \input and friends read the container's filesystem, \directlua runs
# arbitrary Lua. Note that \usepackage and \documentclass are NOT here - they
# arrive constantly in pasted work and are stripped instead, see _extract_figure.
FORBIDDEN = re.compile(
    r"\\(write18|immediate\s*\\write|input\b|include\b|openin|openout|read\b"
    r"|catcode|directlua|latelua|shellescape|special\b)",
    re.IGNORECASE,
)

# Preamble the paper's own template already provides.
WRAPPER_LINES = re.compile(
    r"^[ \t]*\\(documentclass|usepackage|RequirePackage|geometry|pagestyle"
    r"|thispagestyle|pagenumbering|setlength|graphicspath|usetikzlibrary"
    r"|pgfplotsset)\b.*$",
    re.MULTILINE,
)

# Kept, not stripped: the picture refers to whatever these define, and removing
# the definition leaves an undefined command that takes the whole figure down.
FONT_LINES = re.compile(
    r"^[ \t]*\\(?:newfontfamily|setmainfont|setsansfont)\b.*$", re.MULTILINE)

# Something that actually draws. Asked for a figure and given a paragraph, the
# honest answer is to say so - typesetting the paragraph and calling it a
# picture leaves the teacher to work out why their diagram became a sentence.
DRAWS_SOMETHING = re.compile(
    r"\\begin\{(tikzpicture|circuitikz|tikzcd|forest|venndiagram\w*|smartdiagram"
    r"|axis|tikzcd\*)\}|\\chemfig\b|\\schemestart\b|\\smartdiagram\b")


def _extract_figure(source: str) -> str:
    """
    Reduces a pasted LaTeX document to the figure inside it.

    The portal strips this before saving, so most sources arrive clean. This is
    the second layer, for what does not come through the editor - questions
    written by the generator, rows already in the database - because a
    \\documentclass reaching the paper is fatal to every question in it, not
    just this one. Anything already bare passes through unchanged.
    """
    if "\\documentclass" not in source and "\\begin{document}" not in source:
        return source

    fonts = [m.group(0).strip() for m in FONT_LINES.finditer(source)]

    begin = source.rfind("\\begin{document}")
    end = source.rfind("\\end{document}")
    if begin >= 0:
        body = source[begin + len("\\begin{document}"):]
        if end > begin:
            body = source[begin + len("\\begin{document}"):end]
    else:
        body = source

    body = WRAPPER_LINES.sub("", body).strip()
    return "\n".join([*fonts, body]).strip()


class FigureError(RuntimeError):
    """The figure could not be drawn. The message is meant for the teacher."""


def _first_latex_error(log_text: str) -> str:
    """The one line worth showing, out of a thousand-line LuaLaTeX log."""
    for line in log_text.splitlines():
        if line.startswith("! ") and "Option clash" not in line:
            return line[2:].strip()
    return "the figure could not be compiled"


def _compile(latex: str) -> Tuple[str, bytes]:
    """
    Checks, extracts and compiles one figure. Returns (svg text, pdf bytes).

    The SVG is produced even when the caller wanted a PNG: it is the only
    reliable way to tell a figure that drew nothing from one that drew
    something, and that check has to happen whatever format was asked for.
    """
    source = (latex or "").strip()
    if not source:
        raise FigureError("No figure code was given.")
    if len(source) > MAX_SOURCE_CHARS:
        raise FigureError(
            f"This figure is too long to draw ({len(source)} characters, "
            f"limit {MAX_SOURCE_CHARS})."
        )

    # Before the guard below, not after: a pasted document legitimately carries
    # \usepackage and \documentclass, and refusing it outright would reject the
    # commonest thing a teacher does - paste what ChatGPT handed them.
    source = _extract_figure(source)
    if not source or not DRAWS_SOMETHING.search(source):
        raise FigureError(
            "No figure was found in that code. Paste the picture itself - the "
            "\\begin{tikzpicture} ... \\end{tikzpicture} part, or a "
            "circuitikz, tikzcd or \\chemfig figure."
        )

    forbidden = FORBIDDEN.search(source)
    if forbidden:
        raise FigureError(
            f"\\{forbidden.group(1)} is not allowed in a figure. Write the "
            f"diagram itself here; packages are loaded by the paper template."
        )

    template = get_question_latex_template()
    marker = "\\begin{document}"
    # The commented example of this line earlier in the template is why rfind is
    # used rather than a search from the top - splitting on the first hit
    # truncates the preamble and silently drops every package guard.
    preamble = template[: template.rfind(marker)]

    # active,tightpage crops the page down to the figure's own bounding box.
    # Without it every figure arrives on a sheet of A4 with the paper's margins
    # and header around it.
    document = (
        preamble
        + "\\usepackage[active,tightpage]{preview}\n"
        + marker + "\n"
        + "\\begin{preview}\n" + source + "\n\\end{preview}\n"
        + "\\end{document}\n"
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        (tmpdir / "figure.tex").write_text(document, encoding="utf-8")

        try:
            proc = subprocess.run(
                ["lualatex", "-interaction=nonstopmode", "-no-shell-escape",
                 "figure.tex"],
                cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=COMPILE_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise FigureError(
                "The figure took too long to draw. A very large plot or a "
                "domain with thousands of samples is the usual cause."
            )

        pdf = tmpdir / "figure.pdf"
        log_text = ""
        log_file = tmpdir / "figure.log"
        if log_file.exists():
            log_text = log_file.read_text(encoding="utf-8", errors="replace")

        # nonstopmode produces a PDF even when the figure failed, so the log is
        # the only honest signal. Reporting success off the exit code or the
        # existence of the file is how a blank question reaches a printed paper.
        if not pdf.exists() or pdf.stat().st_size == 0:
            logger.warning("figure produced no PDF: %s", proc.returncode)
            raise FigureError(_first_latex_error(log_text))

        svg = tmpdir / "figure.svg"
        try:
            conv = subprocess.run(
                ["dvisvgm", "--pdf", "--optimize", "--output=figure.svg",
                 "figure.pdf"],
                cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=CONVERT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise FigureError("The figure could not be converted for display.")

        if not svg.exists():
            logger.error("dvisvgm failed: %s", conv.stderr[:500])
            raise FigureError("The figure could not be converted for display.")

        content = svg.read_text(encoding="utf-8")

        # An empty <g id='page1'/> means LaTeX measured the figure and drew
        # nothing into it - a missing glyph, most often an Indic label written
        # without \foreignlanguage, where the fallback font has no such
        # character. It compiles cleanly and produces a correctly sized, blank
        # picture, so it has to be caught by looking at the content.
        if not re.search(r"<(path|text|use|image|rect|circle|polygon)\b", content):
            missing = re.search(r"Missing character: There is no (.) ", log_text)
            if missing:
                raise FigureError(
                    f"The figure drew nothing: the character '{missing.group(1)}' "
                    f"is not in the font being used. Wrap non-English text in "
                    f"\\foreignlanguage{{malayalam}}{{...}} so the right font is "
                    f"selected."
                )
            raise FigureError(
                "The figure compiled but drew nothing. Check that the picture "
                "actually contains something to draw."
            )

        return content, pdf.read_bytes()


def render_figure_svg(latex: str) -> str:
    """Draws one figure and returns it as SVG, for on-screen preview."""
    svg, _pdf = _compile(latex)
    logger.info("figure rendered: %d bytes of SVG", len(svg))
    return svg


def render_figure_png(latex: str, dpi: int = 300) -> bytes:
    """
    Draws one figure and returns it as a PNG.

    PNG rather than SVG because this one is KEPT: the portal stores it in the
    question and the paper places it with \\includegraphics, which LuaLaTeX
    accepts as PNG, JPG or PDF - never SVG. 300 dpi because it is going to a
    printed page rather than a screen; at 96 the thin lines in a circuit
    diagram break up.
    """
    _svg, pdf_bytes = _compile(latex)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        (tmpdir / "figure.pdf").write_bytes(pdf_bytes)
        try:
            subprocess.run(
                ["mutool", "draw", "-r", str(dpi), "-o", "figure.png", "figure.pdf"],
                cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=CONVERT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise FigureError("The figure could not be converted to an image.")

        png = tmpdir / "figure.png"
        if not png.exists() or png.stat().st_size == 0:
            raise FigureError("The figure could not be converted to an image.")

        data = png.read_bytes()
        logger.info("figure rendered: %d bytes of PNG at %d dpi", len(data), dpi)
        return data
