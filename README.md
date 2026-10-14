# UCR PhD Dissertation

Quarto book source for Mohammad Dastgheib's dissertation in Psychology at the University of California, Riverside.

**Title:** Effects of Concurrent Task Difficulty and Physical Effort on Cognitive Performance  
**Degree:** Doctor of Philosophy, Psychology  
**Conferral:** December 2026  
**Chair:** Ilana J. Bennett  
**Committee:** Ilana J. Bennett, Aaron R. Seitz, John Franchak

The PDF uses the local `ucr` document class, XeLaTeX, and natbib with `apalike`. Front matter (title page, acknowledgments, dedication, abstract, and contents lists) is written in `index.qmd`.

## Chapters

| File | Role |
|---|---|
| `index.qmd` | Front matter |
| `General_Introduction.qmd` | Scaffold. Replace the notes with the general introduction. |
| `Chapter_1.qmd` | R2 manuscript: concurrent task difficulty and physical effort in younger adults |
| `Chapter_2.qmd` | Placeholder |
| `Chapter_3.qmd` | Placeholder |
| `General_Conclusion.qmd` | Scaffold. Replace the notes with the general conclusion. |
| `references.qmd` | Bibliography, generated from `references.bib` |
| `Appendix_A.qmd` | Supplementary materials for Chapter 1 |

Chapter 1 figures live in `figures/chapter1/`. Appendix A figures live in `figures/appendix_a/`.

## Render

From this directory, with [Quarto](https://quarto.org) and a TeX Live install that provides XeLaTeX:

```bash
quarto render --to pdf
```

The dissertation PDF is written to `_book/UCR_PhD_Dissertation.pdf`. HTML output is also configured (`quarto render --to html`). The acknowledgments use the Amiri font for Arabic text, so that font needs to be installed for the PDF build.

Build products (`_book/`, `.quarto/`, and LaTeX auxiliaries) are gitignored.
