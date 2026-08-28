"""
LaTeX templates for document generation
"""


def get_question_latex_template() -> str:
    """
    Returns the LaTeX template for question paper generation
    """
    return r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=1.4cm]{geometry}
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

    tex.print(data.qp_code .. "\\hfill  Name .............................")
    tex.print("\\begin{flushright}")
    tex.print("Reg.No .............................\\\\")
    tex.print("\\end{flushright}")
    tex.print("\\begin{center}")

    tex.print("\\begin{minipage}{5in}")
    tex.print("\\centering")
    tex.print(data.qp_name)
    tex.print("\\end{minipage} \\\\")

    tex.print("\\vspace{0.3cm}")
    tex.print("\\end{center}")
    tex.print("Time : " .. data.time .. " \\hfill " .. "Max marks : " .. data.max_marks)

    -- Paper-level direction from the portal's "RTL Paper" checkbox. The header
    -- block above (code / name / time / marks) always stays left-to-right;
    -- only the question part below follows this flag.
    local paper_is_rtl = (data.rtl == true)

    tex.print("\\begin{enumerate}")
    for i, row in ipairs(data.qp_parts) do
        tex.print("\\begin{center}")
        tex.print("\\textbf{" .. row.part_name .. "} \\\\")
        tex.print("\\texttt{" .. row.part_description .. "} \\\\")
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

            if string.find(part, "\\begin{tabular}", 1, true) then
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
    tex.print("\\end{enumerate}")

\end{luacode*}
\end{document}
'''
