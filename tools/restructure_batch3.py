#!/usr/bin/env python3
"""
restructure_batch3.py  —  File names that match the printed chapters, plus small fixes
=====================================================================================
Run from the dissertation repo root, on a clean working tree:

    python3 tools/restructure_batch3.py

1. Renames (git mv) so every file is named after the chapter it prints as:
     General_Introduction.qmd  -> Chapter_1_General_Introduction.qmd
     Chapter_1.qmd             -> Chapter_2_Concurrent_Effort_Younger_Adults.qmd
     Chapter_2.qmd             -> Chapter_3_Psychometric_Pupillometry.qmd
     Chapter_3.qmd             -> Chapter_4_DDM_Older_Adults.qmd   (placeholder)
     General_Conclusion.qmd    -> Chapter_5_General_Conclusion.qmd
     Appendix_A.qmd            -> Appendix_A_Chapter_2_Supplement.qmd
     Appendix_B.qmd            -> Appendix_B_Chapter_3_Supplement.qmd
     figures/chapter1/*.png    -> chapter2/figures/*.png
     figures/appendix_a/*.png  -> chapter2/figures/supplement/*.png
   and updates _quarto.yml and the image paths to match.
2. Removes stale files: old setup notes, Quarto template leftovers, the
   figures README; moves the finished batch-1/2 scripts to tools/archive/.
3. Funding statement covers Chapters 2–4 (all on NIA R01AG072607).
4. Appendix A tables: explicit column widths so no cell overruns its column.
5. Writes a README that describes the current structure.

Afterwards run tools/sync_ch3.py (it now writes the new Chapter 3 file names).
Every check runs before anything changes; on any mismatch nothing is changed.
"""
import os
import subprocess
import sys

ROOT = os.getcwd()

RENAMES = [
    ("General_Introduction.qmd", "Chapter_1_General_Introduction.qmd"),
    ("Chapter_1.qmd", "Chapter_2_Concurrent_Effort_Younger_Adults.qmd"),
    ("Chapter_2.qmd", "Chapter_3_Psychometric_Pupillometry.qmd"),
    ("Chapter_3.qmd", "Chapter_4_DDM_Older_Adults.qmd"),
    ("General_Conclusion.qmd", "Chapter_5_General_Conclusion.qmd"),
    ("Appendix_A.qmd", "Appendix_A_Chapter_2_Supplement.qmd"),
    ("Appendix_B.qmd", "Appendix_B_Chapter_3_Supplement.qmd"),
    ("figures/chapter1/figure1_task_schematics.png", "chapter2/figures/figure1_task_schematics.png"),
    ("figures/chapter1/figure2_performance.png", "chapter2/figures/figure2_performance.png"),
    ("figures/chapter1/figure3_pupil_waveforms.png", "chapter2/figures/figure3_pupil_waveforms.png"),
    ("figures/chapter1/figure4_auc_plots.png", "chapter2/figures/figure4_auc_plots.png"),
    ("figures/appendix_a/figure_s1.png", "chapter2/figures/supplement/figure_s1.png"),
    ("figures/appendix_a/figure_s2.png", "chapter2/figures/supplement/figure_s2.png"),
    ("figures/appendix_a/figure_s3.png", "chapter2/figures/supplement/figure_s3.png"),
    ("tools/fix_ch2_batch1_v2.py", "tools/archive/fix_ch2_batch1_v2.py"),
    ("tools/fix_ch2_batch2.py", "tools/archive/fix_ch2_batch2.py"),
]

REMOVE = [
    "ARABIC_FOOTNOTE_EXAMPLE.md",
    "ARABIC_SETUP_COMPLETE.md",
    "CHAPTER1_INTEGRATION_GUIDE.md",
    "MISSING_REFERENCES.md",
    "SETUP_COMPLETE.md",
    "intro.qmd",
    "summary.qmd",
    "cover.png",
    "figures/chapter1/README.md",
]

# (file AFTER rename, old, new, expected count)
EDITS = []


def E(path, old, new, count=1):
    EDITS.append((path, old, new, count))


E("_quarto.yml",
  "  chapters:\n"
  "    - index.qmd\n"
  "    - General_Introduction.qmd\n"
  "    - Chapter_1.qmd\n"
  "    - Chapter_2.qmd\n"
  "    - Chapter_3.qmd\n"
  "    - General_Conclusion.qmd\n"
  "    - references.qmd\n"
  "  appendices:\n"
  "    - Appendix_A.qmd\n"
  "    - Appendix_B.qmd\n",
  "  chapters:\n"
  "    - index.qmd\n"
  "    - Chapter_1_General_Introduction.qmd\n"
  "    - Chapter_2_Concurrent_Effort_Younger_Adults.qmd\n"
  "    - Chapter_3_Psychometric_Pupillometry.qmd\n"
  "    - Chapter_4_DDM_Older_Adults.qmd\n"
  "    - Chapter_5_General_Conclusion.qmd\n"
  "    - references.qmd\n"
  "  appendices:\n"
  "    - Appendix_A_Chapter_2_Supplement.qmd\n"
  "    - Appendix_B_Chapter_3_Supplement.qmd\n")

C2 = "Chapter_2_Concurrent_Effort_Younger_Adults.qmd"
A = "Appendix_A_Chapter_2_Supplement.qmd"
E(C2, "](figures/chapter1/", "](chapter2/figures/", 4)
E(A, "](figures/appendix_a/", "](chapter2/figures/supplement/", 3)

E("Chapter_4_DDM_Older_Adults.qmd",
  "# Placeholder for Study 3 {#sec-chapter3}",
  "# Placeholder for Chapter 4 {#sec-ch4}")

E("index.qmd",
  "The research presented in Chapter 2 was supported by the National Institute on Aging under Grant No. NIH/NIA R01AG072607. The funding agency had no role in the study design, data collection, analysis, decision to publish, or preparation of the manuscript.",
  "The research presented in Chapters 2, 3, and 4 was supported by the National Institute on Aging under Grant No. NIH/NIA R01AG072607. The funding agency had no role in the study design, data collection, analysis, decision to publish, or preparation of the manuscripts.")

# Appendix A: explicit column widths (percent of text width) so no cell overruns
E(A, "{#tbl-s3}", '{#tbl-s3 tbl-colwidths="[7,13,17,8,7,17,6,10,15]"}')
E(A, "{#tbl-s4}", '{#tbl-s4 tbl-colwidths="[8,38,10,10,24,10]"}')
E(A, "{#tbl-s6}", '{#tbl-s6 tbl-colwidths="[7,16,20,10,9,28,10]"}')

README = """# UCR PhD Dissertation

Quarto book source for Mohammad Dastgheib's dissertation in Psychology at the University of California, Riverside.

**Title:** Effects of Concurrent Task Difficulty and Physical Effort on Cognitive Performance
**Degree:** Doctor of Philosophy, Psychology
**Conferral:** December 2026
**Chair:** Ilana J. Bennett
**Committee:** Ilana J. Bennett, Aaron R. Seitz, John Franchak

The PDF uses the local `ucr` document class (`ucr.cls`, UCR 2025/2026 format guide), XeLaTeX, and citeproc with APA 7 (`apa.csl`). Front matter (title, copyright, and approval pages, acknowledgments, dedication, abstract, and contents lists) is written in `index.qmd`. Typeface, size, spacing, and margins are set once for the whole book; chapter files must not set their own.

## Structure

| File | Prints as |
|---|---|
| `index.qmd` | Front matter |
| `Chapter_1_General_Introduction.qmd` | Chapter 1: General Introduction (scaffold) |
| `Chapter_2_Concurrent_Effort_Younger_Adults.qmd` | Chapter 2: reprint of Dastgheib et al. (2026), *Cognitive Research: Principles and Implications*, doi:10.1186/s41235-026-00768-0 |
| `Chapter_3_Psychometric_Pupillometry.qmd` | Chapter 3: generated from the Psychometrics_Pupillometry repo (do not edit here) |
| `Chapter_4_DDM_Older_Adults.qmd` | Chapter 4: placeholder |
| `Chapter_5_General_Conclusion.qmd` | Chapter 5: General Conclusion (scaffold) |
| `references.qmd` | References: one list for the whole dissertation, from `references.bib` |
| `Appendix_A_Chapter_2_Supplement.qmd` | Appendix A: Chapter 2 supplementary material (published supplement) |
| `Appendix_B_Chapter_3_Supplement.qmd` | Appendix B: Chapter 3 supplementary material (generated; do not edit here) |

Assets: `chapter2/figures/` (Chapter 2 and Appendix A figures) and `chapter3/` (Chapter 3 export, figures, R helpers; generated).

## Chapter 3 is generated

Chapter 3 and Appendix B are written by `tools/sync_ch3.py` from a local checkout of [Psychometrics_Pupillometry](https://github.com/mohdasti/Psychometrics_Pupillometry). Edit the chapter there, commit, then from this folder:

```bash
python3 tools/sync_ch3.py --src ../Psychometrics_Pupillometry --check   # dry run
python3 tools/sync_ch3.py --src ../Psychometrics_Pupillometry           # write
```

`chapter3/SOURCE.txt` records the chapter-repo commit and export run in the book. The script also maintains a marked block of Chapter 3-only entries at the end of `references.bib`.

## Render

Requirements: [Quarto](https://quarto.org), a TeX Live install with XeLaTeX, the Amiri font (Arabic in the acknowledgments), and R with `knitr`, `jsonlite`, and `rmarkdown` (Chapter 3 computes its numbers at render time).

```bash
quarto render --to pdf
```

The PDF is written to `_book/UCR_PhD_Dissertation.pdf`. Build products (`_book/`, `.quarto/`, LaTeX auxiliaries) are gitignored.

## Tools

- `tools/sync_ch3.py`: brings Chapter 3 in from its repo (see above).
- `tools/restructure_batch3.py`: one-time rename to the current file layout (already applied).
- `tools/archive/`: one-time cleanup scripts for Chapter 2 (already applied; kept for the record).
"""


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def main():
    problems = []
    if not os.path.isfile(os.path.join(ROOT, "_quarto.yml")):
        sys.exit("ERROR: run from the dissertation repo root (folder with _quarto.yml).")
    st = git("status", "--porcelain", "--untracked-files=no")
    if st.returncode != 0:
        sys.exit("ERROR: not a git repository.")
    if st.stdout.strip():
        problems.append("working tree has uncommitted changes to tracked files:\n" + st.stdout)
    for old, new in RENAMES:
        if not os.path.exists(os.path.join(ROOT, old)):
            problems.append(f"missing (already renamed?): {old}")
        if os.path.exists(os.path.join(ROOT, new)):
            problems.append(f"target already exists: {new}")
    for f in REMOVE:
        if not os.path.exists(os.path.join(ROOT, f)):
            problems.append(f"missing (already removed?): {f}")

    # dry-run the edits against the files' current (pre-rename) content
    rename_back = {new: old for old, new in RENAMES}
    texts = {}
    for path, old, new, count in EDITS:
        if path not in texts:
            src = rename_back.get(path, path)
            if not os.path.exists(os.path.join(ROOT, src)):
                problems.append(f"missing file for edits: {src}")
                continue
            with open(os.path.join(ROOT, src), encoding="utf-8") as fh:
                texts[path] = fh.read()
        found = texts[path].count(old)
        if found != count:
            problems.append(f"{path}: expected {count} match(es), found {found}: {old[:80]!r}")
            continue
        texts[path] = texts[path].replace(old, new)

    if problems:
        print("NOTHING WAS CHANGED. Problems found:\n")
        for p in problems:
            print(" -", p)
        sys.exit(1)

    for old, new in RENAMES:
        os.makedirs(os.path.dirname(os.path.join(ROOT, new)) or ROOT, exist_ok=True)
        r = git("mv", old, new)
        if r.returncode != 0:
            sys.exit(f"git mv failed for {old}: {r.stderr}\nRun `git status` and report before retrying.")
    for f in REMOVE:
        r = git("rm", "-q", f)
        if r.returncode != 0:
            sys.exit(f"git rm failed for {f}: {r.stderr}\nRun `git status` and report before retrying.")
    for path, txt in texts.items():
        with open(os.path.join(ROOT, path), "w", encoding="utf-8") as fh:
            fh.write(txt)
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(README)
    for d in ("figures/chapter1", "figures/appendix_a", "figures"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            leftovers = [x for x in os.listdir(p) if x != ".DS_Store"]
            if not leftovers:
                for x in os.listdir(p):
                    os.remove(os.path.join(p, x))
                os.rmdir(p)
    print(f"ALL OK: {len(RENAMES)} renames, {len(REMOVE)} removals, {len(EDITS)} edits, README rewritten. "
          "Next: run tools/sync_ch3.py.")


if __name__ == "__main__":
    main()
