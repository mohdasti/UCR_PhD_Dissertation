# UCR PhD Dissertation

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
| `Chapter_4_DDM_Older_Adults.qmd` | Chapter 4: generated from the modeling-pupil-DDM repo (do not edit here); in preparation for submission |
| `Chapter_5_General_Conclusion.qmd` | Chapter 5: General Conclusion (scaffold) |
| `references.qmd` | References: one list for the whole dissertation, from `references.bib` |
| `Appendix_A_Chapter_2_Supplement.qmd` | Appendix A: Chapter 2 supplementary material (published supplement) |
| `Appendix_B_Chapter_3_Supplement.qmd` | Appendix B: Chapter 3 supplementary material (generated; do not edit here) |
| `Appendix_C_Chapter_4_Supplement.qmd` | Appendix C: Chapter 4 supplementary material (generated; do not edit here) |

Assets: `chapter2/figures/` (Chapter 2 and Appendix A figures), `chapter3/` and `chapter4/` (exports, tables, figures, R helpers for Chapters 3 and 4; generated).

## Chapters 3 and 4 are generated

Chapter 3 and Appendix B are written by `tools/sync_ch3.py` from a local checkout of [Psychometrics_Pupillometry](https://github.com/mohdasti/Psychometrics_Pupillometry). Edit the chapter there, commit, then from this folder:

```bash
python3 tools/sync_ch3.py --src ../Psychometrics_Pupillometry --check   # dry run
python3 tools/sync_ch3.py --src ../Psychometrics_Pupillometry           # write
```

Chapter 4 and Appendix C are written the same way by `tools/sync_ch4.py` from a local checkout of [modeling-pupil-DDM](https://github.com/mohdasti/modeling-pupil-DDM) (source `reports/chap3_revised.qmd`, which that repo calls Chapter 3):

```bash
python3 tools/sync_ch4.py --src ../modeling-pupil-DDM --check   # dry run
python3 tools/sync_ch4.py --src ../modeling-pupil-DDM           # write
```

Only files tracked in git in the chapter repos are copied. `chapter3/SOURCE.txt` and `chapter4/SOURCE.txt` record the chapter-repo commit used. Each script maintains its own marked block in `references.bib` (entries not already in the dissertation bibliography) and in `ucr-preamble.tex`; `sync_ch4.py` also keeps the Chapter 4 sentence in the co-authorship acknowledgments of `index.qmd` up to date.

## Render

Requirements: [Quarto](https://quarto.org), a TeX Live install with XeLaTeX, the Amiri font (Arabic in the acknowledgments), and R with `knitr`, `jsonlite`, and `rmarkdown` (Chapter 3 computes its numbers at render time).

```bash
quarto render --to pdf
```

The PDF is written to `_book/UCR_PhD_Dissertation.pdf`. Build products (`_book/`, `.quarto/`, LaTeX auxiliaries) are gitignored.

## Tools

- `tools/sync_ch3.py`, `tools/sync_ch4.py`: bring Chapters 3 and 4 in from their repos (see above).
- `tools/restructure_batch3.py`: one-time rename to the current file layout (already applied).
- `tools/archive/`: one-time cleanup scripts for Chapter 2 (already applied; kept for the record).
