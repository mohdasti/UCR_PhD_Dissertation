%% ucr.cls — UCR dissertation/thesis class (2025/2026 Format Guide)
%%
%% Designed for Quarto/Pandoc workflows:
%% - You generate the preliminary pages manually in index.qmd (via \makefrontmatter).
%% - Quarto's default title block is suppressed (see title.tex partial).

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ucr}[2026/01/15 UCR Dissertation Class]

% Base class
\LoadClass[12pt,letterpaper,oneside]{report}

% --- Margins (all pages) ---
% Top/Left: 1.5 in, Bottom/Right: 1 in
% Page number sits in the footer area, centered below the bottom margin line.
\RequirePackage[letterpaper,top=1.5in,left=1.5in,right=1in,bottom=1in,footskip=0.5in]{geometry}

% --- Spacing ---
\RequirePackage{setspace}
\doublespacing

% --- Paragraphs ---
\setlength{\parindent}{0.5in}
\setlength{\parskip}{0pt}

% --- Widow/orphan control ---
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000

% --- Page numbers centered at bottom ---
\RequirePackage{fancyhdr}
\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyfoot[C]{\thepage}%
  \renewcommand{\headrulewidth}{0pt}%
}
\pagestyle{plain}

% Quarto/Pandoc templates may try to typeset a default title block.
% We generate all prelim pages manually (via index.qmd), so keep \maketitle empty.
\renewcommand{\maketitle}{}

% --- TOC / LOF / LOT formatting ---
% UCR requires TOC/LOF/LOT to be single-spaced with a blank line between entries.
\RequirePackage[titles]{tocloft}

% Wrap TOC/LOF/LOT in single spacing, and set entry spacing INSIDE that environment
% so the "blank line" is interpreted under single spacing.
\let\ucr@oldtableofcontents\tableofcontents
\renewcommand{\tableofcontents}{%
  \clearpage
  \begin{singlespace}
    \setlength{\cftbeforechapskip}{\baselineskip}
    \setlength{\cftbeforesecskip}{\baselineskip}
    \setlength{\cftbeforesubsecskip}{\baselineskip}
    \ucr@oldtableofcontents
  \end{singlespace}
  \clearpage
}

\let\ucr@oldlistoffigures\listoffigures
\renewcommand{\listoffigures}{%
  \clearpage
  \begin{singlespace}
    \setlength{\cftbeforefigskip}{\baselineskip}
    \ucr@oldlistoffigures
  \end{singlespace}
  \clearpage
}

\let\ucr@oldlistoftables\listoftables
\renewcommand{\listoftables}{%
  \clearpage
  \begin{singlespace}
    \setlength{\cftbeforetabskip}{\baselineskip}
    \ucr@oldlistoftables
  \end{singlespace}
  \clearpage
}

% --- Fields + front matter generators ---
\makeatletter

% Defaults (override in index.qmd)
\def\@doctype{Dissertation} % or Thesis
\def\@degree{Doctor of Philosophy}
\def\@program{Graduate Program}
\def\@degreemonth{June}
\def\@degreeyear{\number\year}
\def\@chair{}
\def\@cochair{}
\def\@committee{}

\newcommand{\doctype}[1]{\def\@doctype{#1}}
\newcommand{\degree}[1]{\def\@degree{#1}}
\newcommand{\program}[1]{\def\@program{#1}}
\newcommand{\degreemonth}[1]{\def\@degreemonth{#1}}
\newcommand{\degreeyear}[1]{\def\@degreeyear{#1}}
\newcommand{\chair}[1]{\def\@chair{#1}}
\newcommand{\cochair}[1]{\def\@cochair{#1}}

% Flexible committee list (provide names separated by \\)
\newcommand{\committee}[1]{\def\@committee{#1}}

% Signature line count (defaults to 4; adjust if needed)
\newcount\ucr@siglines
\ucr@siglines=4\relax
\newcommand{\signaturelines}[1]{\ucr@siglines=#1\relax}

\newcommand{\ucr@printsignaturelines}{%
  \begingroup
  \parindent=0pt
  \@tempcnta=0\relax
  \loop
    \ifnum\@tempcnta<\ucr@siglines
      \noindent\rule{3in}{0.4pt}\par\vspace{0.6in}
      \advance\@tempcnta by 1\relax
  \repeat
  \endgroup
}

% --- Title page (counted as page i, number not printed) ---
\newcommand{\maketitlepage}{%
  \begin{titlepage}
    \thispagestyle{empty}
    \begin{center}
      \begin{singlespace}
        \vspace*{0.5in}
        UNIVERSITY OF CALIFORNIA\\
        RIVERSIDE\\[0.5in]

        {\@title}\\[0.5in]

        A \@doctype\ submitted in partial satisfaction\\
        of the requirements for the degree of\\[0.2in]

        \@degree\\
        in\\
        \@program\\
        by\\
        \@author\\[0.5in]

        \@degreemonth\ \@degreeyear\\[0.5in]

        \@doctype\ Committee:\\
        \@committee
      \end{singlespace}
    \end{center}
  \end{titlepage}
}

% --- Copyright page (counted as page ii, number not printed) ---
\newcommand{\makecopyrightpage}{%
  \clearpage
  \thispagestyle{empty}
  \null\vfill
  \begin{center}
    \begin{singlespace}
      Copyright by\\
      \@author\\
      \@degreeyear
    \end{singlespace}
  \end{center}
  \vfill\null
  \clearpage
}

% --- Signature approval page (counted as page iii, number not printed) ---
\newcommand{\makesignaturepage}{%
  \clearpage
  \thispagestyle{empty}
  \begin{center}
    \begin{singlespace}
      The \@doctype\ of \@author\ is approved:
    \end{singlespace}
  \end{center}

  \vspace{0.8in}
  \ucr@printsignaturelines

  \vfill
  \begin{center}
    \begin{singlespace}
      Committee Chairperson\\[0.8in]
      University of California, Riverside
    \end{singlespace}
  \end{center}
  \clearpage
}

% --- One-shot front matter helper ---
% Creates Title (i), Copyright (ii), Approval (iii) with page numbers hidden.
% After this, roman numerals continue and ARE printed starting at iv.
\newcommand{\makefrontmatter}{%
  \pagenumbering{roman}% start counting at i
  \setcounter{page}{1}%
  \maketitlepage
  \makecopyrightpage
  \makesignaturepage
  \pagestyle{plain}% page iv+ prints centered footer
}

% --- Abstract (preliminary pages) ---
% Use \begin{ucrabstract} ... \end{ucrabstract}
\newenvironment{ucrabstract}{%
  \clearpage
  \begin{center}
    \begin{singlespace}
      ABSTRACT OF THE \MakeUppercase{\@doctype}\\[0.3in]
      \@title\\[0.2in]
      by\\[0.2in]
      \@author\\[0.2in]
      \@degree, Graduate Program in \@program\\
      University of California, Riverside, \@degreemonth\ \@degreeyear\\
      \@chair, Chairperson%
      \ifx\@cochair\@empty\else\\\@cochair, Co-Chairperson\fi
    \end{singlespace}
  \end{center}
  \vspace{0.25in}
  \doublespacing
}{%
  \clearpage
}

% --- Switch to main body ---
\newcommand{\startmainmatter}{%
  \clearpage
  \pagenumbering{arabic}
  \setcounter{page}{1}
}

\makeatother
