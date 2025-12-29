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
\usepackage{polyglossia}
\usepackage{fontspec}
\usepackage{tabularray}
\usepackage{tikz}
\usepackage{enumitem}
\usepackage{luacode}
\usepackage{luapackageloader}
\usepackage{multicol}
\usepackage{graphicx}
\graphicspath{{./Photo/Qpbank/}}
\usepackage[draft=false]{graphicx}
\setkeys{Gin}{keepaspectratio,width=0.3\textwidth,height=0.3\textheight}
\usepackage{lastpage}
\usepackage{array}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}

\setdefaultlanguage{english}
\setotherlanguage{hindi}
\setotherlanguage{malayalam}
\setotherlanguage{arabic}

\usepackage{fontspec}

\newfontfamily\arabicfont[
  Script=Arabic,
  Scale=1.3
]{Lateef}

\newfontfamily\devanagarifont[
  Script=Devanagari,
  Scale=1.2
]{Lohit Devanagari}

\newfontfamily\hindifont[
  Script=Devanagari,
  Scale=1.2
]{Lohit Devanagari}

\newfontfamily\malayalamfont[
  Script=Malayalam,
  Scale=1.2
]{Rachana}


\begin{document}
\begin{luacode*}
    json = require('dkjson')
    lfs = require('lfs')
    local jsonPath = lfs.currentdir() .. "/Reports/question.json"
    
    function readAll(file)
        local f = io.open(file, "rb")
        if not f then return nil end
        local content = f:read("*all")
        f:close()
        return content
    end

    local contents = readAll(jsonPath)
    if not contents then
        tex.print("Error: Could not read JSON data from " .. jsonPath)
        return
    end
    
    local data, pos, err = json.decode(contents, 1, nil)
    if err then
        tex.print("Error decoding JSON: " .. err)
        return
    end

    -- Font settings from JSON if available
    local fonts = data.fonts or {}
    if fonts.arabic then
        tex.print("\\newfontfamily\\arabicfont[Script=Arabic,Scale=" .. (fonts.arabic_scale or "1.3") .. "]{" .. fonts.arabic .. "}")
    end
    if fonts.hindi then
        tex.print("\\newfontfamily\\hindifont[Script=Devanagari,Scale=" .. (fonts.hindi_scale or "1.2") .. "]{" .. fonts.hindi .. "}")
    end
    if fonts.malayalam then
        tex.print("\\newfontfamily\\malayalamfont[Script=Malayalam,Scale=" .. (fonts.malayalam_scale or "1.2") .. "]{" .. fonts.malayalam .. "}")
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
    tex.print("\\begin{enumerate}")
    for i, row in ipairs(data.qp_parts) do
        tex.print("\\begin{center}")
        tex.print("\\textbf{" .. row.part_name .. "} \\\\")
        tex.print("\\texttt{" .. row.part_description .. "} \\\\")
        tex.print("\\end{center}")
        for j, part in ipairs(row.content) do
            if string.find(part, "\\begin{tabular}") then
                tex.print(part)
            else
                tex.print(part .. " \\\\")
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
