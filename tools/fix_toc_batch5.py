#!/usr/bin/env python3
"""
fix_toc_batch5.py  —  Tighter contents lists, still within UCR rules
=====================================================================
Run from the dissertation repo root:   python3 tools/fix_toc_batch5.py

UCR: the table of contents and the lists of figures and tables are
single-spaced with a blank line between entries. That rule stays. This batch:
  1. Lists chapters and their first-level sections only (e.g., 4.2 Methods),
     not sub-sections (4.2.1 Participants): \\setcounter{tocdepth}{1}.
  2. Stops hyphenating words in the contents lists ("Mem-ory").
  3. Titles the page "Table of Contents" (Quarto sets "Table of contents"),
     matching "List of Figures" and "List of Tables".
Checks every edit first; on any mismatch nothing is changed.
"""
import os
import sys

EDITS = [
    ("ucr.cls",
     "% Wrap TOC/LOF/LOT in single spacing, and set entry spacing INSIDE that environment\n"
     "% so the \"blank line\" is interpreted under single spacing.\n",
     "% Wrap TOC/LOF/LOT in single spacing, and set entry spacing INSIDE that environment\n"
     "% so the \"blank line\" is interpreted under single spacing.\n"
     "% The TOC lists chapters and first-level sections (tocdepth 1); words in all\n"
     "% three lists are not hyphenated.\n"
     "\\setcounter{tocdepth}{1}\n"
     "\\newcommand{\\ucr@nohyphenation}{\\hyphenpenalty=10000\\exhyphenpenalty=10000\\relax}\n"),
    ("ucr.cls",
     "    \\setlength{\\cftbeforesubsecskip}{\\baselineskip}\n"
     "    \\ucr@oldtableofcontents\n",
     "    \\setlength{\\cftbeforesubsecskip}{\\baselineskip}\n"
     "    \\ucr@nohyphenation\n"
     "    \\renewcommand*{\\contentsname}{Table of Contents}%\n"
     "    \\ucr@oldtableofcontents\n"),
    ("ucr.cls",
     "    \\setlength{\\cftbeforefigskip}{\\baselineskip}\n"
     "    \\ucr@oldlistoffigures\n",
     "    \\setlength{\\cftbeforefigskip}{\\baselineskip}\n"
     "    \\ucr@nohyphenation\n"
     "    \\ucr@oldlistoffigures\n"),
    ("ucr.cls",
     "    \\setlength{\\cftbeforetabskip}{\\baselineskip}\n"
     "    \\ucr@oldlistoftables\n",
     "    \\setlength{\\cftbeforetabskip}{\\baselineskip}\n"
     "    \\ucr@nohyphenation\n"
     "    \\ucr@oldlistoftables\n"),
]


def main():
    root = os.getcwd()
    if not os.path.isfile(os.path.join(root, "_quarto.yml")):
        sys.exit("ERROR: run from the dissertation repo root.")
    texts, problems = {}, []
    for path, old, new in EDITS:
        if path not in texts:
            with open(os.path.join(root, path), encoding="utf-8") as fh:
                texts[path] = fh.read()
        n = texts[path].count(old)
        if n != 1:
            problems.append(f"{path}: expected 1 match, found {n}: {old[:70]!r}")
            continue
        texts[path] = texts[path].replace(old, new)
    if problems:
        print("NOTHING WAS CHANGED. Problems found:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    for path, txt in texts.items():
        with open(os.path.join(root, path), "w", encoding="utf-8") as fh:
            fh.write(txt)
    print(f"ALL OK: {len(EDITS)} edits applied to {len(texts)} files.")


if __name__ == "__main__":
    main()
