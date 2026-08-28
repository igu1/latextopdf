r"""
The extra pass an Asymptote figure needs.

WHY THIS EXISTS

\begin{asy} ... \end{asy} is not typeset by LaTeX. The first LaTeX run only
writes the code out as <job>-1.asy, <job>-2.asy, ...; the asy program turns each
of those into a PDF; a second LaTeX run includes them with \includegraphics.
Skip the middle step and LaTeX finds no graphic to include - which under
nonstopmode is a warning and a figure-shaped hole, not an error. That is the
same shape of failure as every other bug this service has had: a request that
succeeds and a paper with a blank where the question was.

Asymptote can run itself from inside LaTeX through shell escape. It is not used
here. A figure is untrusted input - it arrives from a teacher's editor, or from
a language model - and \write18 would hand it the container.
"""

import logging
import pathlib
import re
import subprocess
from typing import List, NamedTuple

logger = logging.getLogger(__name__)

# A figure takes well under a second to render. A minute means the figure's own
# code is looping, and no amount of further waiting ends that.
ASY_TIMEOUT_S = 60


class AsymptoteRun(NamedTuple):
    """What one asy pass did. `figures` is 0 when there was nothing to do."""
    figures: int
    errors: List[str]


def _clean(message: str) -> str:
    """
    asy reports against the file LaTeX wrote - "figure-1.asy: 4.10: syntax
    error". The teacher never saw that file and cannot act on its name, so it
    is dropped and the line and column, which they can act on, are kept.
    """
    return re.sub(r"^\S*?-\d+\.asy:\s*", "", message.strip())


def run_asymptote(workdir: pathlib.Path,
                  timeout: int = ASY_TIMEOUT_S) -> AsymptoteRun:
    """
    Renders every .asy file LaTeX wrote in workdir to a PDF beside it.

    A document with no Asymptote figure costs nothing: there is nothing to
    glob, and asy is never started. `figures` is what tells the caller a second
    LaTeX pass is needed.

    Each file is run separately rather than passing them all to one asy
    invocation, so one figure with a syntax error in it costs that figure and
    not every other figure in the paper.

    -safe -noglobalread is the sandbox, and both halves are needed. -safe
    disables asy's system(), without which a figure could run any command in
    the container. -safe on its own still allows input("/etc/passwd") - which
    was measured, not assumed - so reads are confined to the working directory
    as well. These are asy's own switches, applied to every run here, rather
    than a list of things the source is inspected for.
    """
    sources = sorted(p for p in workdir.glob("*.asy"))
    if not sources:
        return AsymptoteRun(0, [])

    errors: List[str] = []
    for source in sources:
        try:
            proc = subprocess.run(
                ["asy", "-safe", "-noglobalread", source.name],
                cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            errors.append(
                f"{source.name} took longer than {timeout}s to draw - check it "
                f"for a loop that never ends")
            continue
        except FileNotFoundError:
            # The package loads from texlive; the asy PROGRAM comes from the
            # asymptote apt package, so the two can be present separately.
            errors.append(
                "Asymptote figures cannot be drawn: the asy program is not "
                "installed in this image")
            break

        rendered = source.with_suffix(".pdf")
        if proc.returncode != 0 or not rendered.exists():
            first = next(
                (line for line in (proc.stderr or proc.stdout).splitlines()
                 if line.strip()),
                "the figure could not be drawn")
            errors.append(_clean(first))
            logger.warning("asy failed on %s: %s", source.name, first[:200])

    logger.info("asymptote: %d figure(s), %d error(s)", len(sources), len(errors))
    return AsymptoteRun(len(sources), errors)
