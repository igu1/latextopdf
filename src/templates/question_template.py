"""
LaTeX templates for document generation
"""


def get_question_latex_template() -> str:
    """
    Returns the LaTeX template for question paper generation
    """
    return r'''\documentclass[12pt]{article}
% The measure - how long a line of a question is - decides whether a paper
% reads easily, and matters more than the size of the type. At 11pt inside
% 1.4cm margins a line ran to 98 characters; comfortable reading is 60-75 and
% 85 is about the limit, which is why the questions came out as a block of
% text. 12pt inside 2cm gives 84 - inside that limit, and the widest the page
% takes before it starts to read as a block again. Measured on a real paper,
% the extra size cost nothing:
% the same 60 questions printed on the same number of pages, because the page
% count follows how long the questions are and where the breaks fall.
%
% headheight/headsep are what the running head below needs; they are given to
% geometry rather than set afterwards so it lays the page out knowing about
% them (setting \headheight later only earns a "headheight is too small"
% warning). With includehead off - geometry's default - the head lives INSIDE
% the 1.4cm top margin, so the body of every paper stays exactly where it has
% always been, except that `top` is 1.7cm rather than 1.4cm.
%
% That 3mm is for the running head. An 18pt line needs 22pt of height and a
% 10pt gap under it; inside a 1.4cm margin its TOP would sit 3.5mm from the
% edge of the sheet, which is inside the strip most laser printers cannot
% print at all - the code would come out clipped or missing on exactly the
% pages it is there for. At 1.7cm it starts 5.6mm down, which every printer
% manages.
\usepackage[a4paper,left=2cm,right=2cm,top=1.7cm,bottom=1.5cm,headheight=15pt,headsep=10pt]{geometry}
\usepackage{zref-totpages}
\usepackage{array}
\usepackage{fontspec}
\usepackage{tabularray}
\usepackage{tikz}
\usepackage{luacode}
\usepackage{luapackageloader}
\usepackage{multicol}
\graphicspath{{./Photo/Qpbank/}}
\usepackage[draft=false]{graphicx}
\setkeys{Gin}{keepaspectratio,width=0.3\textwidth,height=0.3\textheight}
\usepackage{lastpage}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}

% ---------------------------------------------------------------------------
% CODE BLOCKS, and long identifiers in ordinary text.
%
% A programming question arrives as \begin{verbatim}...\end{verbatim}. Plain
% verbatim NEVER breaks a long line, and a line of Java runs to 150 characters:
% it went straight off the right-hand margin and the printed paper simply lost
% the end of it, so the student read half a statement. LaTeX reports that as an
% overfull hbox - a warning, not an error, so the paper still built and nobody
% was told.
%
% fvextra's Verbatim does break, and \DefineVerbatimEnvironment aims the
% ORIGINAL name at it: every question already stored as \begin{verbatim} prints
% correctly with no change to the stored LaTeX and no migration. Switching to
% lstlisting instead would have meant rewriting every row in the bank.
%
% breakanywhere, not merely breaklines: code offers no spaces to break at
% inside System.out.println("a long string"). tabsize is for Python, where the
% indentation is the syntax rather than decoration.
% ---------------------------------------------------------------------------
\IfFileExists{fvextra.sty}{%
  \usepackage{fvextra}%
  \DefineVerbatimEnvironment{verbatim}{Verbatim}%
    {breaklines=true,breakanywhere=true,fontsize=\small,tabsize=4,xleftmargin=1em}%
  \typeout{QPPKG: fvextra loaded}%
}{\typeout{QPPKG: fvextra MISSING}}

% The same right-hand overflow happens in questions with no code block at all:
% \texttt{FileNotFoundException} inside a sentence is one unbreakable word, and
% when it does not fit, TeX prefers an overfull line to a visibly loose one.
%
% \emergencystretch is what actually fixes that: it lets the paragraph stretch
% on a final pass, so the long word moves down to the next line instead of being
% pushed past the margin. It needs no package and works in every engine.
% hyphenat's [htt] additionally permits hyphenation INSIDE typewriter text,
% which is a genuine improvement where it takes effect - under LuaLaTeX with
% fontspec that depends on the monospace font's own hyphenation character, so it
% is a bonus here rather than the thing being relied on.
\IfFileExists{hyphenat.sty}{%
  \usepackage[htt]{hyphenat}%
  \typeout{QPPKG: hyphenat loaded}%
}{\typeout{QPPKG: hyphenat MISSING}}
\emergencystretch=3em

% ---------------------------------------------------------------------------
% Features the BROWSER preview can already draw, but which this preamble did
% not load - so a teacher could put one in a question, watch it render on
% screen, print the paper, and the student would get a blank space. No error is
% raised anywhere along that path, which makes it the worst way round to fail.
%
% Measured in a browser against the same MathJax + TikzJax the portal loads:
% amssymb, mhchem and tikz-cd all preview; pgfplots does not preview but is the
% feature most often wanted for maths and physics graphs.
%
% \IfFileExists rather than a bare \usepackage, deliberately. The image installs
% a MINIMAL TeX Live (texlive-latex-recommended / -extra / -pictures, not
% texlive-full), so whether a given .sty is present depends on the image - and a
% \usepackage for a missing one does NOT fail cleanly: it blocks waiting to
% fetch the package and the batch-mode build hangs until it times out, taking
% every paper with it rather than just the question that used the feature.
% Guarded, a missing package costs only that one feature.
%
% Each line reports itself with \typeout so the guard can never quietly hide a
% package that still needs installing. LuaLaTeX's output is captured and only
% logged when a compile FAILS, so on a healthy build these markers are thrown
% away - read them by compiling the preamble directly instead:
%
%   docker compose exec latex-pdf-service sh -c 'cd /tmp && python3 -c "
%   import sys; sys.path.insert(0,\"/app/src\")
%   from templates.question_template import get_question_latex_template as t
%   open(\"p.tex\",\"w\").write(t().split(r\"\begin{document}\")[0]
%                              + r\"\begin{document}x\end{document}\")" \
%   && lualatex -interaction=nonstopmode p.tex | grep QPPKG'
%
% Verified in the image built from this repository (all seven load):
%   amssymb / mhchem / tikz-cd / pgfplots / siunitx / circuitikz / chemfig
% and, in the subject block below, all fourteen of tkz-euclide / tkz-graph /
% venndiagram / tikz-3dplot / tikz-feynman / pst-optic / physics / chemformula /
% chemmacros / modiagram / forest / smartdiagram / asymptote / svg.
%
% Loading a package here fixes the printed paper and - since /render-figure
% compiles a single figure against this same preamble - the on-screen preview of
% a DIAGRAM as well. What it still does not reach is maths and text inside a
% question, which the browser draws itself with MathJax (mhchem extension, no
% siunitx) and TikzJax (a fixed WebAssembly dump). So siunitx in running text
% has no preview of its own, and latex-capabilities.ts in the portal must WARN
% about that rather than block the save.
% ---------------------------------------------------------------------------
\IfFileExists{amssymb.sty}{%
  \usepackage{amssymb}%
  \typeout{QPPKG: amssymb loaded}%
}{\typeout{QPPKG: amssymb MISSING}}

\IfFileExists{mhchem.sty}{%
  \usepackage[version=4]{mhchem}%
  \typeout{QPPKG: mhchem loaded}%
}{\typeout{QPPKG: mhchem MISSING}}

\IfFileExists{tikz-cd.sty}{%
  \usepackage{tikz-cd}%
  \typeout{QPPKG: tikz-cd loaded}%
}{\typeout{QPPKG: tikz-cd MISSING}}

\IfFileExists{pgfplots.sty}{%
  \usepackage{pgfplots}%
  \pgfplotsset{compat=1.18}%
  \typeout{QPPKG: pgfplots loaded}%
}{\typeout{QPPKG: pgfplots MISSING}}

% The three below were already present in the image but never loaded, so a
% question using them compiled with "Undefined control sequence" / "Environment
% undefined" and - because nonstopmode keeps going and the compiler only WARNS
% on a non-zero exit (see latex_compiler.py) - the service still answered 200
% with a PDF in which that question was simply blank. Loading them costs no
% measurable compile time (2-3s, unchanged) and does not disturb plain tikz,
% pgfplots or mhchem, all three re-checked after adding these.
\IfFileExists{siunitx.sty}{%
  \usepackage{siunitx}%
  \typeout{QPPKG: siunitx loaded}%
}{\typeout{QPPKG: siunitx MISSING}}

\IfFileExists{circuitikz.sty}{%
  \usepackage{circuitikz}%
  \typeout{QPPKG: circuitikz loaded}%
}{\typeout{QPPKG: circuitikz MISSING}}

\IfFileExists{chemfig.sty}{%
  \usepackage{chemfig}%
  \typeout{QPPKG: chemfig loaded}%
}{\typeout{QPPKG: chemfig MISSING}}

% ---------------------------------------------------------------------------
% SUBJECT DRAWING PACKAGES.
%
% Same \IfFileExists guard and QPPKG marker as above, for the same reason: the
% image installs a MINIMAL TeX Live, and a bare \usepackage for a .sty it does
% not have does not fail cleanly - it blocks looking for the package until the
% batch run times out, which loses every paper in the queue rather than the one
% question that used the feature.
%
% These are as much for /render-figure as for the printed paper: that endpoint
% compiles the figure against THIS preamble, so a lens diagram, a Feynman
% diagram, an MO diagram or a Venn diagram is now shown to the teacher exactly
% as it will print - none of them can be drawn by the browser's own TeX engine.
%
% Every line below was verified in the image built from this repository's
% Dockerfile by compiling a real figure and checking the SVG for drawn content,
% not by trusting a zero exit code (nonstopmode returns one either way).
% ---------------------------------------------------------------------------

% Euclidean geometry: \tkzDefPoint, \tkzDrawCircle, \tkzMarkAngle. Inside an
% ordinary tikzpicture, so nothing else has to change to use it.
\IfFileExists{tkz-euclide.sty}{%
  \usepackage{tkz-euclide}%
  \typeout{QPPKG: tkz-euclide loaded}%
}{\typeout{QPPKG: tkz-euclide MISSING}}

% Graph theory: \Vertex, \Edge, \SetGraphUnit - vertices and edges by name
% instead of by coordinate.
\IfFileExists{tkz-graph.sty}{%
  \usepackage{tkz-graph}%
  \typeout{QPPKG: tkz-graph loaded}%
}{\typeout{QPPKG: tkz-graph MISSING}}

% Set theory: venndiagram2sets / venndiagram3sets with \fillANotB and friends.
\IfFileExists{venndiagram.sty}{%
  \usepackage{venndiagram}%
  \typeout{QPPKG: venndiagram loaded}%
}{\typeout{QPPKG: venndiagram MISSING}}

% 3D coordinates for solid geometry and crystal structures: \tdplotsetmaincoords
% and the (r,theta,phi) coordinate system.
\IfFileExists{tikz-3dplot.sty}{%
  \usepackage{tikz-3dplot}%
  \typeout{QPPKG: tikz-3dplot loaded}%
}{\typeout{QPPKG: tikz-3dplot MISSING}}

% Feynman diagrams. compat is passed explicitly because tikz-feynman warns and
% falls back to its 1.0 syntax without it. It lays diagrams out with pgf's
% graphdrawing library, which exists only under LuaTeX - which is the engine
% used here, so \feynmandiagram works without coordinates being given by hand.
\IfFileExists{tikz-feynman.sty}{%
  \usepackage[compat=1.1.0]{tikz-feynman}%
  \typeout{QPPKG: tikz-feynman loaded}%
}{\typeout{QPPKG: tikz-feynman MISSING}}

% Optics: \lens, \mirror, ray tracing through a converging lens - the standard
% ray diagram, drawn to scale from the focal length rather than by eye.
%
% pst-optic is PSTricks, which is normally the one family of graphics packages
% that cannot be used with a PDF-producing engine: it emits PostScript specials
% and needs a dvips detour (auto-pst-pdf, shell escape) under pdflatex. Under
% LuaLaTeX it draws directly - measured here, a full converging-lens diagram
% with rays and labelled foci, 26 paths in the SVG - so no detour and no shell
% escape is involved. Its pictures are \begin{pspicture}, not tikzpicture.
\IfFileExists{pst-optic.sty}{%
  \usepackage{pst-optic}%
  \typeout{QPPKG: pst-optic loaded}%
}{\typeout{QPPKG: pst-optic MISSING}}

% Physics notation: \dv, \pdv, \grad, \div, \curl, \abs, \norm, \ket, \bra.
%
% physics also defines \qty - and so does siunitx v3, for something completely
% different: siunitx's is a number with a unit, physics' is an auto-sized
% bracket. Whichever loads second wins, in silence. With physics winning,
% \qty{9.8}{\meter\per\second\squared} - which printed correctly before this
% package was added, because siunitx has been loaded here all along - becomes
% "Undefined control sequence \meter" in the middle of a paper, and nonstopmode
% prints that question blank rather than stopping.
%
% So siunitx keeps \qty, by the resolution siunitx itself prints in the log.
% Nothing that used to compile changes meaning, and physics' bracket is still
% reachable under its unambiguous names: \pqty (), \bqty [], \Bqty {}, \vqty ||.
% \ifdefined guards it because siunitx is itself behind an \IfFileExists.
\IfFileExists{physics.sty}{%
  \usepackage{physics}%
  \AtBeginDocument{\ifdefined\SI\RenewCommandCopy\qty\SI\fi}%
  \typeout{QPPKG: physics loaded}%
}{\typeout{QPPKG: physics MISSING}}

% Chemistry beyond mhchem's equations: \ch{} formulas (chemformula), oxidation
% numbers, IUPAC names and reaction mechanisms (chemmacros), and molecular
% orbital diagrams (modiagram). chemmacros pulls chemformula and siunitx in
% itself; both are still named here so a change to chemmacros' dependencies
% cannot quietly remove them.
%
% mhchem stays loaded alongside these: \ce{} is the ONE chemistry feature the
% browser preview can already draw (index.html loads MathJax's mhchem
% extension), so it remains the right thing for a teacher to write for an
% equation in running text. chemformula's \ch{} was re-checked next to it -
% they define different macros and do not interfere.
\IfFileExists{chemformula.sty}{%
  \usepackage{chemformula}%
  \typeout{QPPKG: chemformula loaded}%
}{\typeout{QPPKG: chemformula MISSING}}

\IfFileExists{chemmacros.sty}{%
  \usepackage{chemmacros}%
  \typeout{QPPKG: chemmacros loaded}%
}{\typeout{QPPKG: chemmacros MISSING}}

\IfFileExists{modiagram.sty}{%
  \usepackage{modiagram}%
  \typeout{QPPKG: modiagram loaded}%
}{\typeout{QPPKG: modiagram MISSING}}

% Trees: taxonomic classification, cladograms, pedigree charts, syntax trees.
% forest is the one to reach for over tikz's own trees library - it computes the
% layout instead of leaving sibling spacing to be tuned by hand.
\IfFileExists{forest.sty}{%
  \usepackage{forest}%
  \typeout{QPPKG: forest loaded}%
}{\typeout{QPPKG: forest MISSING}}

% Process and cycle diagrams: \smartdiagram[circular diagram]{...} - life
% cycles, water cycles, flow charts, from a plain list of labels.
\IfFileExists{smartdiagram.sty}{%
  \usepackage{smartdiagram}%
  \typeout{QPPKG: smartdiagram loaded}%
}{\typeout{QPPKG: smartdiagram MISSING}}

% Asymptote: a drawing LANGUAGE rather than a package - loops, functions and
% real 3D, for a figure that would be unreadable as a list of TikZ coordinates.
%
% \begin{asy} ... \end{asy} does not compile in one pass. LaTeX writes the code
% out as <job>-N.asy, the asy program turns each one into a PDF, and a second
% LaTeX pass includes them. Both the paper and /render-figure run that sequence
% (see run_asymptote in src/services/asymptote.py); it is the documented
% workflow for exactly this case - no shell escape, which stays off because a
% figure is untrusted input.
\IfFileExists{asymptote.sty}{%
  \usepackage{asymptote}%
  \typeout{QPPKG: asymptote loaded}%
}{\typeout{QPPKG: asymptote MISSING}}

% svg is loaded so that \includesvg reports itself properly, NOT because it
% works: converting an SVG needs Inkscape called through shell escape, and this
% image has neither. Without the package the same line is "Undefined control
% sequence" and the question prints blank; with it, the svg package says what is
% wrong. Figures reach the paper as PNG or JPG through \includegraphics - which
% is what the portal sends, including for figures drawn by /render-figure.
\IfFileExists{svg.sty}{%
  \usepackage{svg}%
  \typeout{QPPKG: svg loaded}%
}{\typeout{QPPKG: svg MISSING}}

% TikZ libraries. Part of pgf itself, so no \IfFileExists guard is needed - a
% missing one errors immediately instead of blocking the way \usepackage does.
%
% This list is not a wish list, it is a repair. The browser preview runs
% TikzJax, whose prebuilt dump loads all of these already, so a teacher drawing
% a hexagon or a marked angle sees it render on screen. The PDF loaded only
% arrows.meta, so the same question compiled to "I do not know the key
% '/tikz/regular polygon'" and - because nonstopmode continues and the compiler
% only warns on a non-zero exit - the paper printed with that question blank.
% Measured against the shipped preamble before this change, real snippets for
% shapes.geometric, patterns, intersections, decorations.markings, angles,
% positioning, fit, backgrounds and 3d ALL failed; only arrows.meta, calc,
% matrix, plotmarks and decorations.pathmorphing worked, and those four only
% because pgfplots happens to pull them in.
%
% Keep in step with the preview: the set below is what tikzjax preloads plus
% what question papers actually use.
\usetikzlibrary{
  arrows.meta, calc, positioning, fit, matrix, chains,
  shapes.geometric, shapes.misc, shapes.symbols,
  patterns, patterns.meta,
  intersections, through, angles, quotes,
  decorations.markings, decorations.pathmorphing,
  decorations.pathreplacing, decorations.text,
  backgrounds, plotmarks, trees, 3d, fadings, calendar
}


% babel with the full Unicode bidirectional algorithm (bidi=basic, LuaLaTeX).
% This replaces polyglossia, whose LuaLaTeX RTL support laid out digit and
% Latin runs inside Arabic text in reverse order (1948 -> 8491, UNESCO ->
% OCSENU, enumerate label 10. -> 01.).
% layout=lists MUST be a package option (not a \babelprovide key): the LuaTeX
% layout patches in luababel.def are applied at load time and skipped entirely
% when the option is absent. It mirrors list indentation/labels in RTL blocks.
%
% `tabular` is the same story for tables. bidi=basic reorders the text INSIDE a
% cell but never the cells themselves, so an Arabic matching table came out with
% its first column on the left - the mirror image of the Word original, where
% column (a) belongs on the right. This option mirrors the column order too.
\usepackage[bidi=basic, layout={lists tabular}]{babel}
\babelprovide[main, import]{english}
\babelprovide[import]{arabic}
\babelprovide[import]{hindi}
\babelprovide[import]{malayalam}
\babelprovide[import]{tamil}
\babelprovide[import]{telugu}
\babelprovide[import]{kannada}
\babelprovide[import]{bengali}
\babelprovide[import]{gujarati}
\babelprovide[import]{punjabi}
\babelprovide[import]{odia}
\babelprovide[import]{assamese}
% Urdu and Sanskrit are separate languages that reuse an already-loaded script
% (Arabic and Devanagari); French is Latin-script and needs no extra font.
\babelprovide[import]{urdu}
\babelprovide[import]{sanskrit}
\babelprovide[import]{french}
\babelprovide[import]{syriac}

\babelfont[arabic]{rm}[Script=Arabic,Scale=1.3]{Lateef}
\babelfont[hindi]{rm}[Script=Devanagari,Scale=1.2]{Lohit Devanagari}
\babelfont[malayalam]{rm}[Script=Malayalam,Scale=1.2]{Rachana}
\babelfont[tamil]{rm}[Script=Tamil,Scale=1.2]{Lohit Tamil}
\babelfont[telugu]{rm}[Script=Telugu,Scale=1.2]{Lohit Telugu}
\babelfont[kannada]{rm}[Script=Kannada,Scale=1.2]{Lohit Kannada}
\babelfont[bengali]{rm}[Script=Bengali,Scale=1.2]{Lohit Bengali}
\babelfont[gujarati]{rm}[Script=Gujarati,Scale=1.2]{Lohit Gujarati}
\babelfont[punjabi]{rm}[Script=Gurmukhi,Scale=1.2]{Lohit Gurmukhi}
\babelfont[odia]{rm}[Script=Oriya,Scale=1.2]{Lohit Odia}
\babelfont[assamese]{rm}[Script=Bengali,Scale=1.2]{Lohit Assamese}
% Urdu uses the Arabic script font; Sanskrit uses the Devanagari one.
\babelfont[urdu]{rm}[Script=Arabic,Scale=1.3]{Lateef}
\babelfont[sanskrit]{rm}[Script=Devanagari,Scale=1.2]{Lohit Devanagari}
% Syriac uses Noto Sans Syriac, installed by the fonts-noto-core apt package.
% If that package is ever dropped from the Dockerfile this line must go too -
% naming a missing font can fail EVERY paper, not just the Syriac ones.
\babelfont[syriac]{rm}[Script=Syriac,Scale=1.2]{Noto Sans Syriac}

% eso-pic puts something on the page BEHIND everything else, on every page,
% which is exactly what the institution watermark is. \LenToUnit comes with it
% and is the only way to write a real length inside picture coordinates.
%
% Guarded like the other optional packages above: a paper is never failed over
% its watermark, so an image built without eso-pic simply prints no logo (the
% \ifdefined test in the body below).
\IfFileExists{eso-pic.sty}{%
  \usepackage{eso-pic}%
  \typeout{QPPKG: eso-pic loaded}%
}{\typeout{QPPKG: eso-pic MISSING}}

% The paper's code at the top left of every page.
%
% A page that comes loose from its staple has to be identifiable, which is why
% a question paper carries its code on every sheet rather than only on the
% first. Page 1 is the exception: it already prints the code on its own first
% line, beside Name and Reg.No, so it is left on `plain` and does not say it
% twice.
%
% Written out by hand rather than with fancyhdr: a page style is six lines of
% kernel macros, and this image is a minimal TeX Live where every extra
% package is one more thing that can be missing (see the \IfFileExists guards
% above). The foot is kept exactly as `plain` had it - the page number,
% centred - so nothing but the head changes.
\makeatletter
\newcommand{\qpRunningCode}{}

% The page number, and "Turn over" on every page but the last.
%
% A student handed a stapled paper has no way of knowing whether there is
% another page - and papers do get mis-collated and mis-copied. This is the
% line that stops someone answering fifteen questions because they never knew
% page 2 existed. \llap hangs it off the right margin so the page number stays
% centred on the page rather than on what is left of it.
%
% \ztotpages is 0 on the first LaTeX pass and right on the second, so the last
% page loses the line on the pass that produces the PDF.
\newcommand{\qpPageFoot}{%
  % "2/4", not "2": a student holding one sheet can tell whether the paper is
  % whole, and an invigilator collecting them can see at a glance that a page
  % is missing. \ztotpages is 0 on the first LaTeX pass and right on the
  % second, which is the pass that produces the PDF.
  \normalfont\hfil\thepage/\ztotpages\hfil
  \llap{\ifnum\value{page}<\ztotpages\bfseries Turn over\fi}%
}

\def\ps@qpcode{%
  \let\@mkboth\@gobbletwo
  % 12pt bold. The code on page 1 is 18pt because it identifies the PAPER;
  % up here it identifies the SHEET, which a reader looks for rather than
  % reads - and a line as large as page 1's would sit on top of the questions.
  % On the RIGHT. Page 1 carries the code on the left, where it is read with
  % the Name and Reg. No beside it; on the pages after it the code is only a
  % label for the sheet, and the right-hand corner is where a reader thumbing
  % a stack of papers looks for one.
  \def\@oddhead{\normalfont\fontsize{12}{14}\selectfont\bfseries\hfil\qpRunningCode}%
  \def\@evenhead{\@oddhead}%
  \def\@oddfoot{\qpPageFoot}%
  \let\@evenfoot\@oddfoot
}

% The first page: no running code - its code is the first thing in the body -
% but the same foot, because page 1 is the page most likely to be read alone.
\def\ps@qpfirst{%
  \let\@mkboth\@gobbletwo
  \def\@oddhead{}%
  \def\@evenhead{}%
  \def\@oddfoot{\qpPageFoot}%
  \let\@evenfoot\@oddfoot
}
\makeatother

% enumitem must load after babel so babel's RTL list adaptations see (and
% survive) enumitem's list re-implementation
\usepackage{enumitem}

% Polyglossia-compatible commands: the portal's request JSON is written
% against these names, so they are kept as the stable contract.
\newcommand{\textarabic}[1]{\foreignlanguage{arabic}{#1}}
\newcommand{\texthindi}[1]{\foreignlanguage{hindi}{#1}}
\newcommand{\textmalayalam}[1]{\foreignlanguage{malayalam}{#1}}
\newcommand{\textenglish}[1]{\foreignlanguage{english}{#1}}
\newcommand{\texttamil}[1]{\foreignlanguage{tamil}{#1}}
\newcommand{\texttelugu}[1]{\foreignlanguage{telugu}{#1}}
\newcommand{\textkannada}[1]{\foreignlanguage{kannada}{#1}}
\newcommand{\textbengali}[1]{\foreignlanguage{bengali}{#1}}
\newcommand{\textgujarati}[1]{\foreignlanguage{gujarati}{#1}}
\newcommand{\textpunjabi}[1]{\foreignlanguage{punjabi}{#1}}
\newcommand{\textodia}[1]{\foreignlanguage{odia}{#1}}
\newcommand{\texturdu}[1]{\foreignlanguage{urdu}{#1}}
\newcommand{\textsanskrit}[1]{\foreignlanguage{sanskrit}{#1}}
\newcommand{\textfrench}[1]{\foreignlanguage{french}{#1}}
\newcommand{\textsyriac}[1]{\foreignlanguage{syriac}{#1}}
% unstarred otherlanguage: switches PARAGRAPH direction too (the starred form
% only switches text direction, so babel's mirrored list layout never fires).
% Legacy stored questions wrap themselves in flushright to fake RTL alignment
% under the old engine; a real RTL paragraph is already flush right and the
% wrapper's margin resets cancel the mirrored list indent (items align
% inconsistently), so flushright is neutralized to plain paragraphs here.
\newenvironment{Arabic}{%
  \begin{otherlanguage}{arabic}%
  \renewenvironment{flushright}{\par}{\par}%
  \renewenvironment{flushleft}{\par}{\par}%
}{\end{otherlanguage}}

% Read the request JSON already in the preamble: \babelfont (used for the
% optional per-request font overrides) is a preamble-only command. The parsed
% table is kept in the global `qpdata` for the document body below.
\begin{luacode*}
    json = require('dkjson')
    lfs = require('lfs')

    function readAll(file)
        local f = io.open(file, "rb")
        if not f then return nil end
        local content = f:read("*all")
        f:close()
        return content
    end

    qpdata = nil
    qperror = nil

    local jsonPath = lfs.currentdir() .. "/Reports/question.json"
    local contents = readAll(jsonPath)
    if not contents then
        qperror = "Error: Could not read JSON data from " .. jsonPath
    else
        local data, pos, err = json.decode(contents, 1, nil)
        if err then
            qperror = "Error decoding JSON: " .. err
        else
            qpdata = data
        end
    end

    -- Optional font settings from JSON
    local fonts = (qpdata and qpdata.fonts) or {}
    if fonts.arabic then
        tex.print("\\babelfont[arabic]{rm}[Script=Arabic,Scale=" .. (fonts.arabic_scale or "1.3") .. "]{" .. fonts.arabic .. "}")
    end
    if fonts.hindi then
        tex.print("\\babelfont[hindi]{rm}[Script=Devanagari,Scale=" .. (fonts.hindi_scale or "1.2") .. "]{" .. fonts.hindi .. "}")
    end
    if fonts.malayalam then
        tex.print("\\babelfont[malayalam]{rm}[Script=Malayalam,Scale=" .. (fonts.malayalam_scale or "1.2") .. "]{" .. fonts.malayalam .. "}")
    end
\end{luacode*}

\begin{document}

% Outside the luacode* environment on purpose. That environment is a group,
% and \pagestyle does nothing but \def\@oddhead and friends - chosen inside
% it, the style is undone at \end{luacode*} and only the pages shipped out
% before that point carry a head. Page 1 would look right and every page
% after it would lose the code.
%
% The code itself is filled in from the JSON below with \gdef, for the same
% reason. \thispagestyle is already global, but it is kept here beside its
% partner: page 1 prints the code on its own first line, so it stays plain.
\pagestyle{qpcode}
\thispagestyle{qpfirst}

\begin{luacode*}
    if qperror then
        tex.print(qperror)
        return
    end
    local data = qpdata

    -- Feed multi-line strings to TeX as separate input lines: a raw U+000A
    -- character has no glyph in any font and renders as a box in the PDF
    local function print_multiline(s)
        local lines = {}
        for line in (s .. "\n"):gmatch("(.-)\n") do
            lines[#lines + 1] = (line:gsub("\r$", ""))
        end
        tex.print(lines)
    end

    -- The institution's watermark, centred on every page under the
    -- questions. Declared here, before anything is typeset, because
    -- \AddToShipoutPictureBG applies from this point on - to every page of
    -- the paper, including the ones LaTeX has not broken yet.
    --
    -- Three things must be true before a single line is emitted: the portal
    -- sent a logo, the file was written beside the paper, and eso-pic is
    -- installed - \AtPageCenter is its command, and centring on the sheet is
    -- all that is asked of it, so there are no coordinates here to get wrong.
    -- Any of the three missing prints the paper exactly as it prints with no
    -- watermark at all, which is also what an institution that has never
    -- uploaded a logo gets.
    --
    -- The picture arrives already grey and faded (the portal does that in the
    -- browser), so nothing here decides how it looks. It is only placed: dead
    -- centre of the sheet, at most half of it either way, aspect kept.
    local logo = data.logo
    if type(logo) == "string" and logo ~= "" then
        tex.print("\\ifdefined\\AtPageCenter")
        tex.print("\\IfFileExists{" .. logo .. "}{%")
        tex.print("\\AddToShipoutPictureBG{\\AtPageCenter{%")
        tex.print("\\makebox(0,0){\\includegraphics[width=0.5\\paperwidth,height=0.5\\paperheight,keepaspectratio]{" .. logo .. "}}%")
        tex.print("}}}{}")
        tex.print("\\fi")
    end

    -- What the running head prints. \gdef, not \renewcommand: this is inside
    -- the luacode* group (see \pagestyle above \begin{luacode*}), and a local
    -- definition would be gone by the time the second page is shipped out.
    tex.print("\\gdef\\qpRunningCode{" .. data.qp_code .. "}")

    -- Code, page count, Name - one line, the way a university paper prints it.
    --
    -- The code and the Name sit in boxes of NO width, so the two \hfill either
    -- side of the page count are always equal and it falls on the centre of
    -- the line however long the code is. Written as plain \hfill the middle
    -- would drift with the length of the code.
    --
    -- \ztotpages (zref-totpages) is the whole paper's page count. It is 0 on
    -- the first LaTeX pass and right on the second, which is why this service
    -- has always compiled every paper twice.
    -- The sizes of the heading, in points, as the institution's own papers
    -- print them: the code at 18, everything else on these two lines at 12.
    -- \fontsize takes the size and the baseline to go with it and needs
    -- \selectfont to take effect; each one is inside a box or a group, so it
    -- ends where that does.
    -- Name and Reg. No are ONE block, hung at the right margin.
    --
    -- They used to be written in two different places - Name on this line,
    -- Reg. No in a flushright block of its own underneath - and each was
    -- right-aligned on its own. "Reg. No" is 16pt wider than "Name", so the
    -- two words started 16pt apart however carefully the dots were counted.
    -- In one block with a label column they can only line up.
    --
    -- The label column is 2cm: "Reg. No" measures about 1.73cm at 12pt bold,
    -- and in a narrower box it overflowed, so its dots began before Name's
    -- did. Half a centimetre of clearance costs nothing and the two can only
    -- line up.
    --
    -- \dotfill rather than a typed run of full stops: the dots then end
    -- exactly on the margin whatever the labels say, and nobody has to count
    -- them again if a label is renamed or translated.
    --
    -- The box is zero width, so the block hangs to the LEFT of the margin and
    -- the page count between the \hfill either side stays exactly centred.
    tex.print("\\noindent\\makebox[0pt][l]{\\fontsize{18}{22}\\selectfont\\bfseries " .. data.qp_code .. "}"
        .. "\\hfill {\\fontsize{12}{14}\\selectfont\\bfseries (Pages : \\ztotpages)}\\hfill"
        .. "\\makebox[0pt][r]{"
        .. "\\begin{minipage}[t]{6.5cm}"
        .. "\\setlength{\\parindent}{0pt}"
        .. "\\fontsize{12}{14}\\selectfont\\bfseries"
        .. "\\makebox[2cm][l]{Name}\\dotfill\\par"
        .. "\\vspace{4pt}"
        .. "\\makebox[2cm][l]{Reg. No}\\dotfill\\par"
        .. "\\end{minipage}}")

    -- The four blocks of the heading - who the paper belongs to, what the
    -- examination is, what it is worth, and then the paper itself - are set
    -- 24pt apart, with a little more before the first section. Measured on a
    -- printed paper they had been 23, 31 and 24: close enough to look
    -- accidental rather than chosen, and the widest of them left Time and Max
    -- marks floating between the title above and the questions below.
    tex.print("\\vspace{1pt}")
    tex.print("\\begin{center}")

    tex.print("\\begin{minipage}{5in}")
    tex.print("\\centering")

    -- The heading is two things of different size: the EXAMINATION (14pt) and
    -- the PAPER it is for (12pt). The portal sends them as one string with a
    -- LaTeX line break between, so it is split on the first one. Both are
    -- bold; a question paper's heading block is bold throughout.
    --
    -- Everything after that first break is the paper line, however many
    -- breaks it holds of its own - a paper named in two scripts prints both
    -- at the same size.
    local nameHead = data.qp_name
    local nameRest = nil
    local cut = string.find(data.qp_name, "\\\\", 1, true)
    if cut then
        nameHead = string.sub(data.qp_name, 1, cut - 1)
        -- The separator is two backslashes, or four: the portal's screens
        -- have never agreed - two from the generate flow, four from the
        -- preview - and a leftover pair prints as a line break of its own
        -- in front of the paper's name, or swallows the first word after it.
        -- An odd backslash belongs to a COMMAND, not to the separator.
        --
        -- Taking the whole run fixed one thing and broke another: the
        -- paper's name arrives wrapped in a font command - \textnormal{...}
        -- for Latin, \textmalayalam{...} and friends for the rest - whose
        -- single backslash sits at the end of that same run. Stripped with
        -- the separator, the command lost its backslash and TeX printed its
        -- NAME: a heading reading "textnormalFundamentals of Computers...",
        -- with the braces swallowed as grouping.
        --
        -- So the separator goes in PAIRS, and an odd one is kept.
        local nameTail = string.sub(data.qp_name, cut)
        local nameLead = string.match(nameTail, "^\\+") or ""
        nameRest = string.rep("\\", #nameLead % 2) .. string.sub(nameTail, #nameLead + 1)
    end

    tex.print("{\\fontsize{14}{17}\\selectfont\\bfseries")
    print_multiline(nameHead)
    tex.print("\\par}")

    -- The paper's name is NOT bold: the examination above it is the heading,
    -- and setting both bold leaves nothing to tell them apart but their size.
    --
    -- 5pt of air above it, because without any the course sat CLOSER to the
    -- examination name (14pt) than the examination's own two lines are to
    -- each other (17pt) - so it read as a third line of the title rather than
    -- as the paper being examined.
    if nameRest and string.find(nameRest, "%S") then
        tex.print("\\vspace{5pt}")
        tex.print("{\\fontsize{12}{14}\\selectfont")
        print_multiline(nameRest)
        tex.print("\\par}")
    end
    tex.print("\\end{minipage} \\\\")

    -- Was 0.3cm (8.5pt), which made this the widest gap on the page.
    tex.print("\\vspace{1.5pt}")
    tex.print("\\end{center}")
    tex.print("Time : " .. data.time .. " \\hfill " .. "Max marks : " .. data.max_marks)

    -- A little more air before the paper proper than between the heading's
    -- own blocks: this is where the reading starts.
    tex.print("\\vspace{4pt}")

    -- Paper-level direction from the portal's "RTL Paper" checkbox. The header
    -- block above (code / name / time / marks) always stays left-to-right;
    -- only the question part below follows this flag.
    local paper_is_rtl = (data.rtl == true)

    -- No list round the parts.
    --
    -- There used to be a \begin{enumerate} here and an \end{enumerate} after
    -- the loop, holding no \item of its own. It did two things, both
    -- unwanted: it indented EVERY section, heading and question 30pt inside
    -- the left margin - so a question's text began 3.06cm from the edge of
    -- the sheet while ending 2cm from the other - and, being a list with no
    -- items, it was the "Something's wrong--perhaps a missing \item" error
    -- that has been in the log of every paper this service has ever made.
    --
    -- The questions are already a list: the portal sends each section's
    -- content as its own \begin{enumerate} with the labels and numbering the
    -- paper's layout asks for.
    for i, row in ipairs(data.qp_parts) do
        tex.print("\\begin{center}")
        tex.print("\\textbf{" .. row.part_name .. "} \\\\")
        -- Plain, in the paper's own face and size. It was typewriter, which
        -- looked like a system message and was wider than it needed to be on
        -- a measure the questions themselves have to share; italic read as an
        -- aside. The line is simply part of the paper.
        -- In a group, and that is not cosmetic. The line begins with "[" -
        -- "[Answer All. Each Question Carries 5 Marks]" - and the line before
        -- it ends with \\. TeX then reads \\[Answer All...] as a line break
        -- with an optional LENGTH argument, swallows "[A", and loses the
        -- spacing of everything after it in the section. The braces end the
        -- \\ before the bracket is reached.
        tex.print("{" .. row.part_description .. "} \\\\")
        tex.print("\\end{center}")
        for j, part in ipairs(row.content) do
            -- Paper-level RTL (the portal's checkbox): typeset the whole
            -- question part right-to-left. Content the caller already wrapped
            -- in \begin{Arabic} is left alone so it is not nested twice.
            -- plain find (4th arg true): the argument is a literal string, not
            -- a Lua pattern ('(' and '-' would otherwise be pattern magic)
            if paper_is_rtl and not string.find(part, "\\begin{Arabic}", 1, true) then
                part = "\\begin{Arabic}\n" .. part .. "\n\\end{Arabic}"
            end

            -- A question ending in an ENVIRONMENT gets no trailing \\.
            --
            -- The pair below is a paragraph break for ordinary text, but after
            -- \end{tabular} or \end{verbatim} the paper is back in vertical
            -- mode, where \\ is "There's no line here to end" and the compile
            -- fails - and worse for verbatim, the first \\ would land on the
            -- SAME line as \end{verbatim}, which the scanner then does not
            -- recognise as the end at all, so the environment runs away and
            -- swallows the rest of the paper.
            -- Any content that ENDS with an \end{...} is in vertical mode
            -- already, whatever the environment was. Only tabular and
            -- verbatim were named here, which was enough while a list sat
            -- round the whole paper; with that gone, a section's questions -
            -- which arrive as one \begin{enumerate}...\end{enumerate} - end
            -- that way too, and every section earned a "There's no line here
            -- to end".
            if string.find(string.gsub(part, "%s+$", ""), "\\end{%a+%*?}$")
                or string.find(part, "\\begin{verbatim}", 1, true) then
                print_multiline(part)
            else
                print_multiline(part .. " \\\\")
                tex.print(" \\\\")
            end
        end

        tex.print("\\begin{flushright}")
        tex.print("\\texttt{\\textbf{" .. row.footer .. "}} \\\\")
        tex.print("\\end{flushright}")

    end

\end{luacode*}
\end{document}
'''
