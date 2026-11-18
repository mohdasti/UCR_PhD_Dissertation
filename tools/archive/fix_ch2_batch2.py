#!/usr/bin/env python3
"""
fix_ch2_batch2.py  —  Sync Chapter 2 and Appendix A with the published CR:PI article
===================================================================================
Run from the repository root:   python3 tools/fix_ch2_batch2.py
Requires batch 1 (fix_ch2_batch1_v2.py) to be applied and committed first.

1. Chapter_1.qmd (prints as Chapter 2): adopt the publisher's copyedits
   (24 h, 5 s, "whether", "maximum voluntary contraction", ...), and fix one
   citation that rendered without "d = 0.79; Park et al., 2021".
2. Appendix_A.qmd: revert two wording fixes so the text matches the published
   supplement verbatim; restore the Table A.2 cells that were truncated at the
   "|" character in the published file (completed from the analysis output
   LCYA_RandomEffects_Structure.csv in github.com/mohdasti/LCYA).
3. Reprint note: says that Table A.2 is shown in full.

The script checks EVERY edit before writing ANY file; on any mismatch it stops
and changes nothing.
"""
import os
import sys

ROOT = os.getcwd()


def p(rel):
    return os.path.join(ROOT, rel)


EDITS = []


def E(path, old, new, count=1):
    EDITS.append((path, old, new, count))


C = "Chapter_1.qmd"
A = "Appendix_A.qmd"

# ---------------- 1. Chapter 2: citation fix ----------------
E(C, "in our laboratory [*d* = 0.79, @Park2021-rs; see @sec-appA-equivalence].",
     "in our laboratory [*d* = 0.79, @Park2021-rs] (see @sec-appA-equivalence).")

# ---------------- 1. Chapter 2: publisher copyedits ----------------
E(C, "*Keywords*: Task Difficulty, Physical Effort, Pupillometry, Arousal, Working Memory, Perceptual Discrimination",
     "*Keywords*: Task difficulty, Physical effort, Pupillometry, Arousal, Working memory, Perceptual discrimination")
E(C, "University of California, Riverside and surrounding areas",
     "University of California, Riverside, and surrounding areas")
E(C, "(M=22.9 years, SD=3.0 years, 57.8% Female)",
     "(*M* = 22.9 years, *SD* = 3.0 years, 57.8% Female)")
E(C, "separated by at least 24 hours with", "separated by at least 24 h with")
E(C, "was used to measure Maximum Voluntary Contraction (MVC) at the start",
     "was used to measure maximum voluntary contraction (MVC) at the start")
E(C, "as hard as possible for 5 seconds,", "as hard as possible for 5 s,")
E(C, "until the response screen (~5.25s).", "until the response screen (~5.25 s).")
E(C, "4° diameter, 100ms duration)", "4° diameter, 100 ms duration)")
E(C, "Participants indicated if the two Gabor patches", "Participants indicated whether the two Gabor patches")
E(C, "Area Under the Curve (AUC) was then calculated", "Area under the curve (AUC) was then calculated")
E(C, "1–2 seconds post-stimulus", "1–2 s post-stimulus", 2)
E(C, "returned to baseline at ~8 seconds after trial onset", "returned to baseline at ~8 s after trial onset")

# ---------------- 3. Reprint note ----------------
E(C, "Changes from the published article are limited to formatting, citation style, and cross-references for consistency with this dissertation. The article's supplementary material is reproduced as @sec-appendix-a.",
     "Changes from the published article are limited to formatting, citation style, and cross-references for consistency with this dissertation. The article's supplementary material is reproduced as @sec-appendix-a; the cells of @tbl-s2, which were truncated in the published supplementary file, are shown in full.")

# ---------------- 2. Appendix A: verbatim published wording ----------------
E(A, "**Models for Cognitive AUC (ADT and VDT only)**\n\nWhen the LMMs for Cognitive AUC were repeated",
     "**Models for Cognitive AUC (ADT and VDT only)**\n\nWhen the LMMs for Total AUC were repeated")
E(A, "for all fixed-effect estimates across the primary behavioral and pupillary models, providing complete reporting of effect sizes and variability for all terms.",
     "for all fixed-effect estimates across the primary behavioral and pupillary models, in response to Reviewer 1's request for complete reporting of effect sizes and variability for all terms.")

# ---------------- 2. Appendix A: Table A.2 cells ----------------
E(A, "| CDT Accuracy | `(1 |\n", "| CDT Accuracy | (1 \\| Participant) |\n")
E(A, "| CDT Reaction Time | `(1 |\n", "| CDT Reaction Time | (1 \\| Participant) |\n")
E(A, "| CDT Total AUC | `(1 + PhysicalEffort |\n", "| CDT Total AUC | (1 + PhysicalEffort \\| Participant) |\n")
E(A, "| ADT Accuracy | `(1 |\n", "| ADT Accuracy | (1 \\| Participant) |\n")
E(A, "| ADT Reaction Time | `(1 |\n", "| ADT Reaction Time | (1 \\| Participant) |\n")
E(A, "| ADT Total AUC | `(1 |\n", "| ADT Total AUC | (1 \\| Participant) |\n")
E(A, "| VDT Accuracy | `(1 + Difficulty * PhysicalEffort |\n", "| VDT Accuracy | (1 + Difficulty * PhysicalEffort \\| Participant) |\n")
E(A, "| VDT Reaction Time | `(1 |\n", "| VDT Reaction Time | (1 \\| Participant) |\n")
E(A, "| VDT Total AUC | `(1 + Difficulty * PhysicalEffort |\n", "| VDT Total AUC | (1 + Difficulty * PhysicalEffort \\| Participant) |\n")


# ================================ RUN ======================================
def main():
    problems = []

    if not os.path.exists(p("_quarto.yml")) or not os.path.exists(p("ucr.cls")):
        sys.exit("ERROR: run this from the repository root (folder with _quarto.yml).")
    if not os.path.exists(p("tools/fix_ch2_batch1_v2.py")):
        problems.append("batch 1 not found (tools/fix_ch2_batch1_v2.py): apply batch 1 first.")

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



    if problems:
        print("NOTHING WAS CHANGED. Problems found:\n")
        for pr in problems:
            print(" -", pr)
        sys.exit(1)

    # 2) Write everything.
    for path, txt in texts.items():
        with open(p(path), "w", encoding="utf-8") as fh:
            fh.write(txt)

    print(f"ALL OK: {len(EDITS)} edits applied to {len(texts)} files. "
          "Chapter 2 and Appendix A now match the published article.")


if __name__ == "__main__":
    main()
