#!/usr/bin/env python3
"""
fix_ch2_batch1_v2.py  —  Dissertation cleanup, batch 1 (v2)
=========================================================
Run from the repository root:   python3 tools/fix_ch2_batch1_v2.py

v2 targets the repo AFTER the Oct-31 local edits are committed (commit
"WIP Oct 31: partial citation fixes ..."). It builds on those edits.

What it does (all edits are exact find/replace; nothing is guessed):
  A. Build: page numbering, stray "Front matter" page, missing glyphs (≤ ≥ ≈ ₀),
     APA 7 references via citeproc, Appendix A as a real appendix.
  B. Chapter 2 (file Chapter_1.qmd): reprint note instead of journal author block,
     every broken / plain-text citation converted to a real citation, wording
     synced to the published CR:PI article, Supplementary-Material pointers turned
     into cross-references to Appendix A, Declarations cleaned up.
  C. Appendix A: section ids, cross-reference fixes, typos.
  D. Front matter: committee titles (Dr.), co-authorship / reprint statement,
     pronoun fix, Arabic orthography, chapter numbers.
  E. references.bib: name particles, bad metadata, two missing entries.
  F. Swaps the four figure files whose contents are under the wrong names.

Safety: the script first checks EVERY edit before writing ANY file.
If anything does not match exactly, it stops and changes nothing.
"""
import hashlib
import os
import sys

ROOT = os.getcwd()


def p(rel):
    return os.path.join(ROOT, rel)


def md5(rel):
    with open(p(rel), "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# --------------------------------------------------------------------------
# Edits: (file, old, new, expected_number_of_occurrences)
# --------------------------------------------------------------------------
EDITS = []


def E(path, old, new, count=1):
    EDITS.append((path, old, new, count))


# ============================== A. BUILD ===================================

# A1 — UCR class: the titlepage environment resets the page counter in
#      oneside mode, so Acknowledgments printed "iii" instead of "iv".
E("ucr.cls",
  "  \\maketitlepage\n",
  "  \\maketitlepage\n"
  "  \\setcounter{page}{2}% titlepage env resets the counter in oneside mode\n")

# A2 — Preamble: replace the CSL block (it crashed with current pandoc:
#      "Lonely \\item") with a patch that keeps pandoc's list environment.
E("ucr-preamble.tex",
  "\\makeatletter\n"
  "% 1) If Pandoc CSL creates a CSLReferences environment, enforce spacing there.\n"
  "\\AtBeginDocument{%\n"
  "  \\@ifundefined{CSLReferences}{}{%\n"
  "    \\renewenvironment{CSLReferences}[2]{%\n"
  "      \\begin{singlespace}%\n"
  "      \\setlength{\\parskip}{\\baselineskip}% blank line between entries\n"
  "    }{%\n"
  "      \\end{singlespace}%\n"
  "      \\setlength{\\parskip}{0pt}%\n"
  "    }%\n"
  "  }%\n"
  "}\n"
  "\\makeatother\n",
  "\\makeatletter\n"
  "% 1) Pandoc/citeproc (CSL) bibliography: keep pandoc's list environment, but\n"
  "%    force single spacing and one blank line (1\\baselineskip) between entries.\n"
  "\\AtBeginDocument{%\n"
  "  \\@ifundefined{CSLReferences}{}{%\n"
  "    \\let\\ucr@origCSLReferences\\CSLReferences\n"
  "    \\renewcommand{\\CSLReferences}[2]{\\singlespacing\\ucr@origCSLReferences{#1}{1}}%\n"
  "  }%\n"
  "}\n"
  "\\makeatother\n")

# A3 — Preamble: glyphs missing from Latin Modern + suppress the stray
#      "Front matter" chapter page that Quarto emits from index.qmd's H1.
E("ucr-preamble.tex",
  "% Note: Use \\ar{...} for Arabic text in your document\n"
  "% Example: This is English^[\\ar{هذا عربي}] text.",
  "% Note: Use \\ar{...} for Arabic text in your document\n"
  "% Example: This is English^[\\ar{هذا عربي}] text.\n"
  "\n"
  "% ========================================\n"
  "% Characters missing from the Latin Modern text font\n"
  "% ========================================\n"
  "% Without these, the PDF silently drops the glyphs (blank space).\n"
  "\\usepackage{newunicodechar}\n"
  "\\newunicodechar{≤}{\\ensuremath{\\leq}}\n"
  "\\newunicodechar{≥}{\\ensuremath{\\geq}}\n"
  "\\newunicodechar{≈}{\\ensuremath{\\approx}}\n"
  "\\newunicodechar{₀}{\\textsubscript{0}}\n"
  "\n"
  "% ========================================\n"
  "% Suppress the \"Front matter\" heading page\n"
  "% ========================================\n"
  "% Quarto requires index.qmd to start with an H1. That H1 would print as a\n"
  "% page before the UCR title page, so drop exactly that one starred chapter.\n"
  "\\makeatletter\n"
  "\\let\\ucr@origchapter\\chapter\n"
  "\\renewcommand{\\chapter}{\\@ifstar{\\ucr@starchapter}{\\ucr@origchapter}}\n"
  "\\newcommand{\\ucr@starchapter}[1]{%\n"
  "  \\def\\ucr@tempa{#1}\\def\\ucr@tempb{Front matter}%\n"
  "  \\ifx\\ucr@tempa\\ucr@tempb\\else\\ucr@origchapter*{#1}\\fi}\n"
  "\\makeatother")

# A4 — _quarto.yml: real title (PDF metadata), Appendix A as an appendix,
#      APA 7 via citeproc instead of natbib/apalike.
E("_quarto.yml",
  '  title: "UCR_PhD_Dissertation"\n',
  '  title: "Effects of Concurrent Task Difficulty and Physical Effort on Cognitive Performance"\n'
  '  output-file: "UCR_PhD_Dissertation"\n')
E("_quarto.yml",
  "    - references.qmd\n    - Appendix_A.qmd\n",
  "    - references.qmd\n  appendices:\n    - Appendix_A.qmd\n")
E("_quarto.yml",
  "# Optional for Psychology-style citations/references (NOT table styling):\n"
  "# csl: apa-7th-edition.csl\n",
  "# APA 7th edition (citation-style-language/styles, apa.csl)\n"
  "csl: apa.csl\n")
E("_quarto.yml",
  "    cite-method: natbib\n    biblio-style: apalike\n",
  "")

# ======================= B. CHAPTER 2 (Chapter_1.qmd) =======================
C = "Chapter_1.qmd"

# B1 — Heading without hard-coded "Chapter 1:" (Quarto numbers it Chapter 2)
#      and a reprint note instead of the journal author block.
E(C,
  "# Chapter 1: Effects of Concurrent Task Difficulty and Physical Effort on Memory and Perceptual Performance and Pupil Response in Younger Adults {#sec-chapter1}\n"
  "\n"
  "**Authors:** Mohammad Dastgheib^1+^, Andrew Y. Sun^2+^, Kimia C. Yaghoubi^1^, Weiwei Zhang^1^, Megan A.K. Peters^3,4^, Ilana J. Bennett^*1^, Aaron R. Seitz^*1,2^\n"
  "\n"
  "**Affiliations:** ^1^University of California, Riverside; ^2^Northeastern University; ^3^University of California, Irvine; ^4^Canadian Institute for Advanced Research\n"
  "\n"
  "^+^co-first author; ^*^co-senior author\n"
  "\n"
  "**Correspondence:** Mohammad Dastgheib; `mdast003@ucr.edu`\n"
  "\n"
  "This chapter is a co-authored manuscript accepted for publication in *Cognitive Research: Principles and Implications* [@Dastgheib-inpress-crpi].\n"
  "\n"
  "## Abstract\n",
  "# Effects of Concurrent Task Difficulty and Physical Effort on Memory and Perceptual Performance and Pupil Response in Younger Adults {#sec-concurrent-effort}\n"
  "\n"
  "This chapter is a reprint of the following open-access article, published under a Creative Commons Attribution 4.0 International License (<https://creativecommons.org/licenses/by/4.0/>):\n"
  "\n"
  "> Dastgheib, M., Sun, A. Y., Yaghoubi, K. C., Zhang, W., Peters, M. A. K., Bennett, I. J., & Seitz, A. R. (2026). Effects of concurrent task difficulty and physical effort on memory and perceptual performance and pupil response in younger adults. *Cognitive Research: Principles and Implications*. <https://doi.org/10.1186/s41235-026-00768-0>\n"
  "\n"
  "Mohammad Dastgheib and Andrew Y. Sun are co-first authors; Ilana J. Bennett and Aaron R. Seitz are co-senior authors. Changes from the published article are limited to formatting, citation style, and cross-references for consistency with this dissertation. The article's supplementary material is reproduced as @sec-appendix-a.\n"
  "\n"
  "## Abstract {.unnumbered}\n")
E(C, "## Significance Statement\n", "## Significance Statement {.unnumbered}\n")

# B2 — Introduction citations
E(C, "relative to their maximum voluntary contraction (MVC; [@Lind1967-tf])",
     "relative to their maximum voluntary contraction [MVC, @Lind1967-tf]")
E(C, "(e.g., walking; [@Hausdorff2008-st]; [@Plummer-D-Amato2012-ss])",
     "[e.g., walking, @Hausdorff2008-st; @Plummer-D-Amato2012-ss]")
E(C, "(low physical effort; [@Brown2015-zu])",
     "[low physical effort, @Brown2015-zu]")
E(C, "task-evoked pupil responses (TEPR)[@Gilzenrat2010-ye; @Joshi2020-il]",
     "task-evoked pupil responses [TEPR, @Gilzenrat2010-ye; @Joshi2020-il]")

# B3 — Methods
E(C, "using a long-term memory task is not included",
     "using a long-term memory task are not included")
E(C, "Sessions 2-4 included", "Sessions 2–4 included")
E(C, "(1280x960 resolution", "(1280 × 960 resolution")
E(C, "dimly lit room and screens were", "dimly lit room, and screens were")
E(C, "Additional task details are described next and trial schematics are provided in @fig-task-schematics.\n",
     "Additional task details are described next, and trial schematics are provided in @fig-task-schematics.\n")
E(C, "Confidence ratings were also collected and are reported in the Supplementary Material (Section 1).",
     "Confidence ratings were also collected and are reported in @sec-appA-confidence.")
E(C, "A Change Detection Task (CDT; Cappiello et al., [-@Cappiello2018-wv]) was used",
     "A Change Detection Task [CDT, @Cappiello2018-wv] was used")
E(C, "An Auditory Discrimination Task (ADT; Murphy et al., [-@Murphy2011-nr]; Näätänen, [-@Naatanen1990-sz]) was used to assess auditory frequency discrimination. On each",
     "An Auditory Discrimination Task [ADT, @Murphy2011-nr; @Naatanen1990-sz] was used to assess auditory frequency discrimination. On each")
E(C, "A Visual Discrimination Task (VDT; [@Polat1994-nv])",
     "A Visual Discrimination Task [VDT, @Polat1994-nv]")
E(C, "Preprocessing followed current recommendations [cf. @Mathot2018-ke; @Mathot2023-vj; @Laeng2024-li]",
     "Preprocessing followed current recommendations [cf. @Laeng2024-li; @Mathot2023-vj; @Mathot2018-ke]")
E(C, "(≥10 samples required for baseline calculation; as in prior work [@Mathot2018-ke]).",
     "[≥10 samples required for baseline calculation, as in prior work, @Mathot2018-ke].")
E(C, "is reported in the Supplementary Material (Section 2) and the significance",
     "is reported in @sec-appA-random-effects, and the significance")
E(C, "equivalence tests (TOST; Lakens, 2018) using effect size bounds derived from a prior study in our lab (*d* = 0.79; [@Park2021-rs]; Supplementary Material Section 3).",
     "equivalence tests [TOST, @Lakens2018-fq] using effect size bounds derived from a prior study in our laboratory [*d* = 0.79, @Park2021-rs; see @sec-appA-equivalence].")
E(C, "revealing no significant effects (Supplementary Material Section 1)",
     "revealing no significant effects (@sec-appA-confidence)")
E(C, "(Supplementary Material Section 4)", "(@sec-appA-continuous)", 4)
E(C, "**LLM/AI tool use**: Cursor", "**LLM/AI tool use:** Cursor")

# B4 — Results
E(C, "(see @fig-performance, top row and Supplementary Material Section 6)",
     "(see @fig-performance, top row, and @sec-appA-fixed-effects)")
E(C, "(see @fig-performance, bottom row and Supplementary Material Section 6)",
     "(see @fig-performance, bottom row, and @sec-appA-fixed-effects)")
E(C, "(see @fig-auc-plots, top row and Supplementary Material Section 6)",
     "(see @fig-auc-plots, top row, and @sec-appA-fixed-effects)")
E(C, "(all *p*s > .10; see Supplementary Material Section 5)",
     "(all *p*s > .10; see @sec-appA-correlations)")

# B5 — Discussion
E(C, "(40% vs. 5% of MVC; [@Park2021-rs])", "[40% vs. 5% of MVC, @Park2021-rs]")
E(C, "(30% vs. 5% of MVC; [@Azer2023-ft])", "[30% vs. 5% of MVC, @Azer2023-ft]")
E(C, "(e.g., 30-70% MVC in Brown & Bray, 2015)", "[e.g., 30–70% MVC in @Brown2015-zu]")
E(C, "(Eriksen Flanker; [@Thibault2019-hg])", "[Eriksen Flanker, @Thibault2019-hg]")
E(C, "(Go/No-Go; [@Blakely2023-bl])", "[Go/No-Go, @Blakely2023-bl]")
E(C, "(e.g., standard n-back or Sternberg tasks; [@Kahneman1966-jf]; [@Westbrook2015-gy])",
     "[e.g., standard n-back or Sternberg tasks, @Kahneman1966-jf; @Westbrook2015-gy]")
E(C, "(such as older adults; [@Lindenberger2000-aw]; [@Woollacott2002-ur])",
     "[such as older adults, @Lindenberger2000-aw; @Woollacott2002-ur]")
E(C, "other methods for modelling performance", "other methods for modeling performance")
E(C, "\n**Conclusions**\n", "\n## Conclusions\n")

# B6 — Figures: short captions for the List of Figures; keep tall figure on page
E(C, "{#fig-task-schematics}", '{#fig-task-schematics fig-scap="Trial schematics for the CDT, ADT, and VDT"}')
E(C, "{#fig-performance}", '{#fig-performance fig-scap="Accuracy and reaction time by task difficulty and physical effort"}')
E(C, "{#fig-pupil-waveforms}", '{#fig-pupil-waveforms width=80% fig-scap="Pupil response waveforms by task difficulty and physical effort"}')
E(C, "{#fig-auc-plots}", '{#fig-auc-plots fig-scap="Total and Cognitive AUC by task difficulty and physical effort"}')

# B7 — End matter: one abbreviation list (published order), one clean
#      Declarations section (fixes the broken **Label: ** bold markup).
E(C,
  "## List of Abbreviations\n"
  "\n"
  "- **ADT**: Auditory Discrimination Task\n"
  "- **VDT**: Visual Discrimination Task\n"
  "- **CDT**: Change Detection Task\n"
  "- **AUC**: Area Under the Curve\n"
  "- **TEPR**: Task-evoked pupil response\n"
  "- **MVC**: Maximum voluntary contraction\n"
  "- **IRB**: Institutional Review Board\n"
  "- **GLMM**: Generalized linear mixed-effects model\n"
  "- **LMM**: Linear mixed-effects model\n"
  "- **GAM**: Generalized Additive Models\n",
  "## Abbreviations {.unnumbered}\n"
  "\n"
  "- **ADT**: Auditory discrimination task\n"
  "- **VDT**: Visual discrimination task\n"
  "- **CDT**: Change detection task\n"
  "- **AUC**: Area under the curve\n"
  "- **TEPR**: Task-evoked pupil response\n"
  "- **MVC**: Maximum voluntary contraction\n"
  "- **IRB**: Institutional review board\n"
  "- **GLMM**: Generalized linear mixed-effects model\n"
  "- **LMM**: Linear mixed-effects model\n"
  "- **GAM**: Generalized additive model\n")

E(C,
  "## Declarations\n"
  "\n"
  "**Funding**: This work was supported by NIA (Grant No. NIH/NIA R01AG072607). The funder had no role in study design, data collection, analysis, decision to publish, or manuscript preparation.\n"
  "\n"
  "**Ethics approval and consent to participate:** All procedures were approved by the Institutional Review Board at the University of California, Riverside (Protocol No. HS-21-055). All participants provided written informed consent prior to participation.\n"
  "\n"
  "**Consent for publication:** Not applicable\n"
  "\n"
  "**Availability of data and materials:** De-identified behavioral and pupillometry data are available from the corresponding author upon reasonable request. Analysis code and study materials are available via Zenodo (https://doi.org/10.5281/zenodo.20498484)\n"
  "\n"
  "**Competing interests:** The authors declare that they have no competing interests.\n"
  "\n"
  "**Authors' contributions:** Conceptualization: WBZ, MAKP, IJB, ARS. Data curation: MD, AYS, KCY. Formal analysis: MD. Funding acquisition: WBZ, MAKP, IJB, ARS. Investigation: MD. Methodology: WBZ, MAKP, IJB, ARS. Project administration: WBZ, MAKP, IJB, ARS. Resources: ARS. Software: MD, ARS. Supervision: WBZ, MAKP, IJB, ARS. Validation: IJB, ARS. Visualization: MD. Writing—original draft: MD. Writing—review & editing: MD, WBZ, MAKP, IJB, ARS.\n"
  "\n"
  "*MD and AYS contributed equally.\n"
  "\n"
  "**Acknowledgements:** We thank Hadi Kobaissi and Jacqueline Alba for assistance with data collection.\n"
  "\n"
  "## Open Practices Statement\n"
  "\n"
  "**Materials/code availability**: Analysis code and study materials are publicly available via Zenodo (https://doi.org/10.5281/zenodo.20498484) and the associated GitHub repository.\n"
  "\n"
  "**Data availability**: De-identified data are available from the corresponding author upon reasonable request (subject to any IRB/consent constraints).\n"
  "\n"
  "**Preregistration**: This study was not preregistered.\n",
  "## Declarations {.unnumbered}\n"
  "\n"
  "**Code availability:** Analysis code and study materials are publicly available via Zenodo (<https://doi.org/10.5281/zenodo.20498484>) and the associated GitHub repository.\n"
  "\n"
  "**Acknowledgements:** We thank Hadi Kobaissi and Jacqueline Alba for assistance with data collection.\n"
  "\n"
  "**Author contributions:** Conceptualization: WBZ, MAKP, IJB, ARS. Data curation: MD, AYS, KCY. Formal analysis: MD. Funding acquisition: WBZ, MAKP, IJB, ARS. Investigation: MD. Methodology: WBZ, MAKP, IJB, ARS. Project administration: WBZ, MAKP, IJB, ARS. Resources: ARS. Software: MD, ARS. Supervision: WBZ, MAKP, IJB, ARS. Validation: IJB, ARS. Visualization: MD. Writing—original draft: MD. Writing—review & editing: MD, WBZ, MAKP, IJB, ARS. MD and AYS contributed equally.\n"
  "\n"
  "**Funding:** This work was supported by NIA (Grant No. NIH/NIA R01AG072607). The funder had no role in study design, data collection, analysis, decision to publish, or manuscript preparation.\n"
  "\n"
  "**Data availability:** De-identified behavioral and pupillometry data are available from the corresponding author upon reasonable request. Analysis code and study materials are available via Zenodo (<https://doi.org/10.5281/zenodo.20498484>).\n"
  "\n"
  "**Ethics approval and consent to participate:** All procedures were approved by the Institutional Review Board at the University of California, Riverside (Protocol No. HS-21-055). All participants provided written informed consent prior to participation.\n"
  "\n"
  "**Preregistration:** This study was not preregistered.\n"
  "\n"
  "**Consent for publication:** Not applicable.\n"
  "\n"
  "**Competing interests:** The authors declare that they have no competing interests.\n")

# ============================ C. APPENDIX A ================================
A = "Appendix_A.qmd"
E(A, "# Appendix A: Supplementary Materials for Chapter 1 {#sec-appendix-a}",
     "# Supplementary Materials for Chapter 2 {#sec-appendix-a}")
E(A, "## Section 1: Subjective Confidence Results",
     "## Subjective Confidence Results {#sec-appA-confidence}")
E(A, "## Section 2: Random-Effects Structure",
     "## Random-Effects Structure {#sec-appA-random-effects}")
E(A, "## Section 3: Evidence for the Null (Equivalence Testing)",
     "## Evidence for the Null (Equivalence Testing) {#sec-appA-equivalence}")
E(A, "## Section 4: Continuous Measures of Physical Effort",
     "## Continuous Measures of Physical Effort {#sec-appA-continuous}")
E(A, "## Section 5: Individual Difference Correlations",
     "## Individual Difference Correlations {#sec-appA-correlations}")
E(A, "## Section 6: Additional Statistics for GLMM and LMM Effects",
     "## Additional Statistics for GLMM and LMM Effects {#sec-appA-fixed-effects}")
# cross-references were off by one (table ids are s4 and s5)
E(A, "**Models for Cognitive AUC (ADT and VDT only)**\n\nWhen the LMMs for Total AUC were repeated",
     "**Models for Cognitive AUC (ADT and VDT only)**\n\nWhen the LMMs for Cognitive AUC were repeated")
E(A, "All models were fit at the trial level . The", "All models were fit at the trial level. The")
E(A, "for all fixed-effect estimates across the primary behavioral and pupillary models, in response to Reviewer 1's request for complete reporting of effect sizes and variability for all terms.",
     "for all fixed-effect estimates across the primary behavioral and pupillary models, providing complete reporting of effect sizes and variability for all terms.")
E(A, "{#fig-s1}", '{#fig-s1 fig-scap="Subjective confidence across conditions"}')
E(A, "{#fig-s2}", '{#fig-s2 width=80% fig-scap="Equivalence tests for non-significant terms"}')
E(A, "{#fig-s3}", '{#fig-s3 fig-scap="Measured grip force and Total AUC within High-effort trials"}')

# ====================== D. FRONT MATTER & SCAFFOLDS ========================
I = "index.qmd"
E(I, "\\chair{Ilana J. Bennett}", "\\chair{Dr. Ilana J. Bennett}")
E(I, "\\committee{Ilana J. Bennett, Chairperson \\\\ Aaron R. Seitz \\\\ John Franchak}",
     "\\committee{Dr. Ilana J. Bennett, Chairperson \\\\ Dr. Aaron R. Seitz \\\\ Dr. John Franchak}")
E(I, "throughout my doctoral journey. His insights and encouragement",
     "throughout my doctoral journey. Their insights and encouragement")
# Arabic couplet: Arabic kaf/yeh instead of Persian ک/ی
E(I, "\\ar{هُوَ کَهفی مِن نُوَبِ الدُّنیا}", "\\ar{هُوَ كَهفي مِن نُوَبِ الدُّنيا}")
E(I,
  "Chapter 1 of this dissertation is a co-authored manuscript accepted for publication as Dastgheib, M., Sun, A. Y., Yaghoubi, K. C., Zhang, W., Peters, M. A., Bennett, I. J., and Seitz, A. R. (in press). Effects of Concurrent Task Difficulty and Physical Effort on Memory and Perceptual Performance and Pupil Response in Younger Adults. \\textit{Cognitive Research: Principles and Implications}. It was conducted in collaboration with Andrew Y. Sun, Kimia C. Yaghoubi, Weiwei Zhang, Megan A.K. Peters, Ilana J. Bennett, and Aaron R. Seitz. I acknowledge the significant contributions of my co-authors to the conceptualization, methodology, data collection, analysis, and manuscript preparation that comprise this chapter. The research presented in Chapter 1 was supported",
  "The text of Chapter 2 of this dissertation is a reprint of the following previously published, co-authored article: Dastgheib, M., Sun, A. Y., Yaghoubi, K. C., Zhang, W., Peters, M. A. K., Bennett, I. J., & Seitz, A. R. (2026). Effects of concurrent task difficulty and physical effort on memory and perceptual performance and pupil response in younger adults. \\textit{Cognitive Research: Principles and Implications}. https://doi.org/10.1186/s41235-026-00768-0. The article is published open access under a Creative Commons Attribution 4.0 International License, and copyright is held by the authors. Mohammad Dastgheib and Andrew Y. Sun contributed equally as co-first authors. The co-senior authors, Ilana J. Bennett and Aaron R. Seitz, directed and supervised the research that forms the basis of this chapter. I acknowledge the significant contributions of all co-authors to the conceptualization, methodology, data collection, analysis, and manuscript preparation of this work. The research presented in Chapter 2 was supported")
E(I, "multiple cognitive domains. Chapter 1 investigates how",
     "multiple cognitive domains. Chapter 2 investigates how")

G = "General_Introduction.qmd"
E(G, "Chapters 1–3. Suggested structure", "Chapters 2–4. Suggested structure")
E(G, "- **Chapter 3** …", "- **Chapter 4** …")
E(G, "- **Chapter 2** …", "- **Chapter 3** …")
E(G, "- **Chapter 1** examines", "- **Chapter 2** examines")
E(G, "pointing the reader into Chapter 1.", "pointing the reader into Chapter 2.")

K = "General_Conclusion.qmd"
E(K, "### Chapter 3\n", "### Chapter 4\n")
E(K, "### Chapter 2\n", "### Chapter 3\n")
E(K, "### Chapter 1\n", "### Chapter 2\n")

E("Chapter_2.qmd", "# Chapter 2: Placeholder {#sec-chapter2}", "# Placeholder for Study 2 {#sec-chapter2}")
E("Chapter_3.qmd", "# Chapter 3: Placeholder {#sec-chapter3}", "# Placeholder for Study 3 {#sec-chapter3}")

# ============================ E. references.bib =============================
B = "references.bib"
# Name particles (otherwise APA renders "Wel & Steenbergen", "Ouden", "Silva Castanheira")
E(B, 'author    = "Algermissen, Johannes and den Ouden, Hanneke E M",',
     'author    = "Algermissen, Johannes and {den Ouden}, Hanneke E M",', 2)
E(B, 'author    = "van der Wel, Pauline and van Steenbergen, Henk",',
     'author    = "{van der Wel}, Pauline and {van Steenbergen}, Henk",')
E(B, 'author    = "da Silva Castanheira, Kevin and LoParco, Sophia and Otto, A Ross",',
     'author    = "{da Silva Castanheira}, Kevin and LoParco, Sophia and Otto, A Ross",')
# Bad Google-Scholar metadata
E(B,
  '  title     = "Attention and effort",\n'
  '  author    = "Kahneman, Daniel",\n'
  '  publisher = "Citeseer",\n'
  '  volume    =  1063,\n'
  '  year      =  1973\n',
  '  title     = "Attention and effort",\n'
  '  author    = "Kahneman, Daniel",\n'
  '  publisher = "Prentice-Hall",\n'
  '  year      =  1973\n')
E(B,
  '  author    = "Green, David Marvin and Swets, John A and {Others}",\n'
  '  publisher = "Wiley New York",\n'
  '  volume    =  1,\n'
  '  year      =  1966,\n'
  '  url       = "http://andrei.gorea.free.fr/Teaching_fichiers/SDT%20and%20Psytchophysics.pdf"\n',
  '  author    = "Green, David M and Swets, John A",\n'
  '  publisher = "Wiley",\n'
  '  year      =  1966\n')
E(B,
  '@ARTICLE{Williams1949-mw,\n'
  '  title   = "Experimental Designs Balanced for the Estimation of Residual\n'
  '             Eﬀectsof Treatments",\n'
  '  author  = "{Williams}",\n'
  '  journal = "Australian journal of scientific research. Ser. B: Biological\n'
  '             sciences",\n'
  '  year    =  1949,\n'
  '  url     = "https://www.publish.csiro.au/ch/pdf/CH9490149",\n'
  '  issn    = "0365-365X"\n'
  '}',
  '@ARTICLE{Williams1949-mw,\n'
  '  title   = "Experimental designs balanced for the estimation of residual\n'
  '             effects of treatments",\n'
  '  author  = "Williams, E J",\n'
  '  journal = "Australian Journal of Chemistry",\n'
  '  volume  =  2,\n'
  '  number  =  2,\n'
  '  pages   = "149--168",\n'
  '  year    =  1949,\n'
  '  doi     = "10.1071/CH9490149"\n'
  '}')

E(B,
  "@ARTICLE{Dastgheib-inpress-crpi,\n"
  "  author  = {Dastgheib, M. and Sun, A. Y. and Yaghoubi, K. C. and Zhang, W. and\n"
  "              Peters, M. A. and Bennett, I. J. and Seitz, A. R.},\n"
  "  title   = {Effects of Concurrent Task Difficulty and Physical Effort on\n"
  "              Memory and Perceptual Performance and Pupil Response in Younger\n"
  "              Adults},\n"
  "  journal = {Cognitive Research: Principles and Implications},\n"
  "  year    = {in press}\n"
  "  % Manuscript CRPI-D-26-00010R2. DOI to be added when assigned.\n"
  "}\n",
  "@ARTICLE{Dastgheib2026-crpi,\n"
  "  author  = {Dastgheib, Mohammad and Sun, Andrew Y. and Yaghoubi, Kimia C.\n"
  "              and Zhang, Weiwei and Peters, Megan A. K. and Bennett, Ilana J.\n"
  "              and Seitz, Aaron R.},\n"
  "  title   = {Effects of concurrent task difficulty and physical effort on\n"
  "              memory and perceptual performance and pupil response in younger\n"
  "              adults},\n"
  "  journal = {Cognitive Research: Principles and Implications},\n"
  "  year    = {2026},\n"
  "  doi     = {10.1186/s41235-026-00768-0}\n"
  "}\n")

E("README.md",
  "| `Chapter_1.qmd` | Accepted CRPI manuscript (in press): concurrent task difficulty and physical effort in younger adults |",
  "| `Chapter_1.qmd` | Published CR:PI article (2026, doi:10.1186/s41235-026-00768-0); renders as Chapter 2 |")
E("README.md",
  "The PDF uses the local `ucr` document class, XeLaTeX, and natbib with `apalike`.",
  "The PDF uses the local `ucr` document class, XeLaTeX, and citeproc with APA 7 (`apa.csl`).")

BIB_APPEND_UNUSED = """
@ARTICLE{Barr2013-maximal,
  title   = "Random effects structure for confirmatory hypothesis testing:
             Keep it maximal",
  author  = "Barr, Dale J and Levy, Roger and Scheepers, Christoph and Tily,
             Harry J",
  journal = "Journal of Memory and Language",
  volume  =  68,
  number  =  3,
  pages   = "255--278",
  year    =  2013,
  doi     = "10.1016/j.jml.2012.11.001"
}

@ARTICLE{Brauer2018-lmm,
  title   = "Linear mixed-effects models and the analysis of nonindependent
             data: A unified framework to analyze categorical and continuous
             independent variables that vary within-subjects and/or
             within-items",
  author  = "Brauer, Markus and Curtin, John J",
  journal = "Psychological Methods",
  volume  =  23,
  number  =  3,
  pages   = "389--411",
  year    =  2018,
  doi     = "10.1037/met0000159"
}
"""

# ============================ F. FIGURE SWAPS ==============================
# Each pair currently holds the other's image. md5 values identify the wrong
# (current) state, so the swap can never run twice.
SWAPS = [
    ("figures/chapter1/figure2_performance.png", "df5db17b9bf19402b939e3bc091f4a41",
     "figures/chapter1/figure4_auc_plots.png", "105bde4e969c4aa23bb8559d1597f817"),
    ("figures/appendix_a/figure_s1.png", "ef37941d0a3bbd141dd407a5b9fd88cf",
     "figures/appendix_a/figure_s3.png", "920999ee88e4b1f2594e0d6c64e39852"),
]


# ================================ RUN ======================================
def main():
    problems = []

    if not os.path.exists(p("_quarto.yml")) or not os.path.exists(p("ucr.cls")):
        sys.exit("ERROR: run this from the repository root (folder with _quarto.yml).")
    if not os.path.exists(p("apa.csl")):
        problems.append("apa.csl is missing from the repository root (copy it there first).")

    # 1) Load files and dry-run every edit in order.
    texts = {}
    for path, old, new, count in EDITS:
        if path not in texts:
            with open(p(path), encoding="utf-8") as fh:
                texts[path] = fh.read()
        found = texts[path].count(old)
        if found != count:
            problems.append(f"{path}: expected {count} match(es), found {found}:\n    {old[:90]!r}")
            continue
        texts[path] = texts[path].replace(old, new)

    if "@ARTICLE{Barr2013-maximal," not in texts.get(B, ""):
        problems.append("references.bib lacks Barr2013-maximal: commit the Oct-31 local edits first")

    for a, ha, b, hb in SWAPS:
        if md5(a) != ha or md5(b) != hb:
            problems.append(f"figure swap {a} <-> {b}: files are not in the expected (wrong) state")

    if problems:
        print("NOTHING WAS CHANGED. Problems found:\n")
        for pr in problems:
            print(" -", pr)
        sys.exit(1)

    # 2) Write everything.
    for path, txt in texts.items():
        with open(p(path), "w", encoding="utf-8") as fh:
            fh.write(txt)
    for a, _, b, _ in SWAPS:
        tmp = p(a) + ".swaptmp"
        os.rename(p(a), tmp)
        os.rename(p(b), p(a))
        os.rename(tmp, p(b))

    print(f"ALL OK: {len(EDITS)} edits applied to {len(texts)} files; "
          f"{len(SWAPS)} figure pairs swapped.")


if __name__ == "__main__":
    main()
