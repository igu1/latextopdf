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
%
% Loading a package here only fixes the PRINTED paper. The browser preview runs
% TikzJax, whose package set is fixed inside a prebuilt WebAssembly dump, and
% MathJax, which has an mhchem extension but no siunitx - so pgfplots, siunitx,
% circuitikz and chemfig render on paper but cannot be previewed on screen.
% latex-capabilities.ts in the portal must therefore WARN about those, not
% block the save.
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
