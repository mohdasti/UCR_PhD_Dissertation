#!/usr/bin/env python3
"""
sync_ch4.py  —  Bring dissertation Chapter 4 in from the modeling-pupil-DDM repo
================================================================================
Usage (from the dissertation repo root):

    python3 tools/sync_ch4.py --src ../modeling-pupil-DDM            # write
    python3 tools/sync_ch4.py --src ../modeling-pupil-DDM --check    # dry run

The chapter repo stays the single source of truth (it calls this chapter
"Chapter 3"). Re-run this script whenever the chapter changes there; it
regenerates the dissertation files below and never edits the chapter repo.
Only files the chapter repo tracks in git are copied.

Reads (from --src):
    reports/chap3_revised.qmd                      chapter source (dissertation version)
    reports/references.bib                         its references
    R/ch3_report_helpers.R                         table/number helpers
    <tables_dir>/inline_values.rds and *.csv       render inputs (tables_dir from the qmd params)
    <figures_dir>/*.png                            figures      (figures_dir from the qmd params)
    output/neuropsych_demographics/extended_baseline_{continuous,categorical}.csv

Writes (in the dissertation repo):
    Chapter_4_DDM_Older_Adults.qmd          dissertation Chapter 4
    Appendix_C_Chapter_4_Supplement.qmd     its supplementary materials (Appendix C)
    chapter4/                               setup.R, R helper, tables, figures, neuropsych,
                                            SOURCE.txt
    references.bib       managed block of Chapter 4-only entries (between markers)
    _quarto.yml          adds Appendix_C_Chapter_4_Supplement.qmd to the appendices (once)
    ucr-preamble.tex     Greek/prime glyphs for Latin Modern (managed block)
    index.qmd            Chapter 4 sentence in the co-authorship acknowledgments

Conversion rules (so the chapter matches Chapters 2 and 3 and UCR format):
  * Title becomes the chapter heading; an in-preparation note and the abstract
    ("## Abstract {.unnumbered}") follow, as in Chapter 2.
  * Typed section numbers ("2.1 Participants", "{.unnumbered}") are removed;
    the book numbers sections. Each such heading gets an id, and typed
    references ("Section 4.5") become live cross-references.
  * Main-text headings move down one level; per-chapter References are dropped
    (one reference list for the dissertation).
  * Supplementary Materials become Appendix C. "Table S"/"Figure S" floats
    become ordinary tables/figures numbered C.1, C.2, ...
  * Dissertation-only blocks are kept; the render-time diagnostics chunk that
    writes keys_used.csv is dropped.
  * "Chapter 1/2/3" in the prose become Chapter 2/3/4.
  * Every sec-/fig-/tbl- label gets a "ch4-" prefix.
  * Citation keys for works already in references.bib (same DOI, or same title
    and year) are mapped to the existing keys, so no work is listed twice.
  * R-hat is written as math (Latin Modern has no combining hat).
  * Tables: the helper copy sets each column's share of the text width from
    the widest text in it that cannot wrap (numbers and intervals are joined
    with no-break spaces), and the brms-formula table becomes a multiline
    table so formulas wrap. Chapter 4 and Appendix C tables are set in
    \footnotesize with 2.5 pt column padding. If a table cannot fit with every
    "estimate [interval]" on one line, the interval may wrap under its
    estimate; the two widest tables (LANDSCAPE_TABLES) go on landscape pages.

Safety: everything is computed and checked in memory first; if any check
fails, nothing is written.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

ROOT = os.getcwd()

SRC_QMD = "reports/chap3_revised.qmd"
SRC_BIB = "reports/references.bib"
SRC_HELPER = "R/ch3_report_helpers.R"
SRC_NEURO = "output/neuropsych_demographics"
NEURO_FILES = ["extended_baseline_continuous.csv", "extended_baseline_categorical.csv"]

OUT_CHAPTER = "Chapter_4_DDM_Older_Adults.qmd"
OUT_APPENDIX = "Appendix_C_Chapter_4_Supplement.qmd"
OUT_DIR = "chapter4"

CH_LABEL = "sec-ch4"
APP_LABEL = "sec-appendix-c"
APP_TITLE = "Supplementary Materials for Chapter 4"
PREFIX = "ch4-"

AUTHORS = "Dastgheib, M., Bennett, I. J., & Seitz, A. R."

# Chapter-repo keys whose entries lack a DOI/year match but are the same work
# as an existing dissertation entry (the chapter repo still cites it "in press").
KEY_OVERRIDES = {
    "dastgheib_inpress_effects": "Dastgheib2026-crpi",
}

BIB_BEGIN = "% ===== BEGIN Chapter 4 references (managed by tools/sync_ch4.py; do not edit by hand) ====="
BIB_END = "% ===== END Chapter 4 references ====="

PREAMBLE_MARK = "% --- Chapter 4 glyphs and tables (added by tools/sync_ch4.py) ---"
PREAMBLE_END = "% --- end of Chapter 4 glyphs and tables ---"
PREAMBLE_ADD = (
    "\n" + PREAMBLE_MARK + "\n"
    "% Latin Modern has no Greek letters or prime in its text font\n"
    "\\newunicodechar{Δ}{\\ensuremath{\\Delta}}\n"
    "\\newunicodechar{β}{\\ensuremath{\\beta}}\n"
    "% unicode-math redefines the prime at \\begin{document}, so map it after that\n"
    "\\AtBeginDocument{\\newunicodechar{′}{\\ensuremath{{}^{\\prime}}}}\n"
    "% Chapter 4 / Appendix C tables are dense (estimates with intervals in every\n"
    "% cell): set them in \\footnotesize. The flag is switched on and off by the\n"
    "% generated Chapter 4 and Appendix C files, so other chapters are unaffected.\n"
    "\\newif\\ifucrsmalltables\n"
    "\\AtBeginEnvironment{longtable}{\\ifucrsmalltables\\footnotesize\\setlength{\\tabcolsep}{2.5pt}\\fi}\n"
    "\\usepackage{pdflscape}\n"
    + PREAMBLE_END + "\n"
)

INDEX_ANCHOR = "The research presented in Chapters 2, 3, and 4 was supported"
INDEX_RE = re.compile(r"Chapter 4 is in preparation for submission for publication as [^\n]*?\(in prep\.\)\. [^\n]*? This chapter was conducted under the direction of Ilana J\. Bennett and Aaron R\. Seitz\. ")


# Appended to the helper copy: column widths for make_table() pipe tables.
R_WIDTH_HELPERS = r'''
# ---- Added by tools/sync_ch4.py (dissertation only) -------------------------
# Pandoc sizes pipe-table columns from the dashes under the header. Set them in
# proportion to the widest text in each column that cannot wrap: words, and
# numbers/intervals the helpers join with no-break spaces. Short cells (<= 8 em)
# are kept whole. Widths are approximate Latin Modern glyph widths in em.
.diss_char_w <- function(ch) {
  if (grepl("^[0-9]$", ch)) return(0.50)
  if (grepl("^[A-Z]$", ch)) return(0.72)
  if (grepl("^[a-z]$", ch)) return(0.50)
  if (ch %in% c(" ", "\u00a0")) return(0.33)
  if (ch %in% c(".", ",", ":", ";", "'", "|", "!")) return(0.28)
  if (ch %in% c("[", "]", "(", ")")) return(0.39)
  if (ch %in% c("%", "\u00b1", "\u2212", "\u2013", "\u00d7", "\u0394")) return(0.80)
  0.55
}
.diss_text_w <- function(s) {
  chars <- strsplit(s, "")[[1]]
  if (!length(chars)) return(0)
  sum(vapply(chars, .diss_char_w, numeric(1)))
}
.diss_cell_need <- function(s, split_interval = FALSE) {
  s <- gsub("[*$\\\\]", "", as.character(s))
  if (is.na(s) || !nzchar(s)) return(0)
  if (split_interval) s <- gsub("\u00a0[", " [", s, fixed = TRUE)
  words <- strsplit(s, " ", fixed = TRUE)[[1]]
  words <- words[nzchar(words)]
  widest <- if (length(words)) max(vapply(words, .diss_text_w, numeric(1))) else 0
  full <- .diss_text_w(s)
  if (full <= 8) widest <- max(widest, full)
  widest + 0.3
}
# Text width in em at \footnotesize (10 pt): 6 in = 433.6 pt, less 2 x 2.5 pt
# column padding per column and a small margin.
# On a landscape page (see LANDSCAPE_TABLES in sync_ch4.py) the text width is 9 in.
.diss_avail_em <- function(ncol) {
  width_pt <- if (isTRUE(get0(".diss_landscape", envir = globalenv()))) 650.4 else 433.6
  width_pt / 10 - 0.5 * ncol - 0.5
}
.diss_needs <- function(shown, header, split_interval) {
  vapply(seq_len(ncol(shown)), function(j) {
    max(1.5, .diss_cell_need(header[[j]], split_interval),
        vapply(as.character(shown[[j]]), .diss_cell_need, numeric(1), split_interval = split_interval))
  }, numeric(1))
}
# Returns list(shown, lines): if the table cannot fit with every
# "estimate [interval]" cell on one line, the no-break space before "[" becomes
# a normal space, so the interval may move under its estimate.
.diss_fit_table <- function(shown, header) {
  need <- .diss_needs(shown, header, FALSE)
  if (sum(need) > .diss_avail_em(ncol(shown))) {
    shown[] <- lapply(shown, function(x) gsub("\u00a0[", " [", x, fixed = TRUE))
    need <- .diss_needs(shown, header, TRUE)
    if (sum(need) > .diss_avail_em(ncol(shown))) {
      message("sync_ch4 note: a table needs ", round(sum(need), 1), " em; ",
              round(.diss_avail_em(ncol(shown)), 1), " em available")
    }
  }
  list(shown = shown, need = need)
}
.diss_pipe_widths <- function(lines, need) {
  dashes <- pmax(3L, round(240 * need / sum(need)))
  cells <- strsplit(gsub("^\\||\\|$", "", lines[[2]]), "|", fixed = TRUE)[[1]]
  if (length(cells) != length(dashes)) stop("pipe table separator has unexpected columns")
  new <- vapply(seq_along(cells), function(j) {
    c0 <- trimws(cells[[j]])
    paste0(if (startsWith(c0, ":")) ":" else "", strrep("-", dashes[[j]]),
           if (endsWith(c0, ":")) ":" else "")
  }, character(1))
  lines[[2]] <- paste0("|", paste(new, collapse = "|"), "|")
  lines
}
'''


# Appendix C tables too wide for a portrait page even with intervals wrapped:
# set on landscape pages.
LANDSCAPE_TABLES = ["tbl-ch4-robustness", "tbl-ch4-pupil-models"]

LANDSCAPE_OPEN = (
    "```{=latex}\n\\begin{landscape}\n```\n\n"
    "```{r}\n#| include: false\nassign(\".diss_landscape\", TRUE, envir = globalenv())\n```\n\n"
)
LANDSCAPE_CLOSE = (
    "\n\n```{r}\n#| include: false\nassign(\".diss_landscape\", FALSE, envir = globalenv())\n```\n\n"
    "```{=latex}\n\\end{landscape}\n```\n"
)


def landscape_tables(text, labels):
    for lab in labels:
        m = re.search(r"^::: \{#" + re.escape(lab) + r"\}\n.*?^:::\n", text, re.S | re.M)
        need(m is not None, f"landscape table not found: {lab}")
        text = text[:m.start()] + LANDSCAPE_OPEN + m.group(0) + LANDSCAPE_CLOSE + text[m.end():]
    return text


class SyncError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise SyncError(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def git_ls(src, rel):
    try:
        out = subprocess.run(["git", "-C", src, "ls-files", "--", rel],
                             capture_output=True, text=True, check=True).stdout.split()
    except Exception:
        raise SyncError("the chapter repo must be a git checkout (needed to copy only tracked files)")
    return sorted(out)


# ----------------------------------------------------------------------------
# Text helpers
# ----------------------------------------------------------------------------
def split_front_matter(text):
    need(text.startswith("---\n"), "chapter qmd does not start with YAML front matter")
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5:]


def yaml_scalar(yaml, key, indent=""):
    m = re.search(r"^" + indent + re.escape(key) + r':\s*"(.*)"\s*$', yaml, re.M)
    need(m is not None, f"could not find {key!r} in the YAML")
    return m.group(1).replace('\\"', '"')


def iter_lines_outside_code(text):
    in_code = False
    for line in text.split("\n"):
        fence = line.lstrip().startswith("```")
        yield line, in_code or fence
        if fence:
            in_code = not in_code


def resolve_meta_divs(text):
    """Keep content-visible when-meta=dissertation, drop content-hidden ones."""
    out, stack = [], []
    for line, in_code in iter_lines_outside_code(text):
        s = line.strip()
        if not in_code and s.startswith(":::"):
            if re.fullmatch(r":::+\s*\{\.content-visible when-meta=\"dissertation\"\}", s):
                stack.append("keep")
                continue
            if re.fullmatch(r":::+\s*\{\.content-hidden when-meta=\"dissertation\"\}", s):
                stack.append("drop")
                continue
            if re.fullmatch(r":::+", s):
                need(stack, "unbalanced ::: in chapter source")
                kind = stack.pop()
                if kind in ("keep", "drop"):
                    continue
                if "drop" not in stack:
                    out.append(line)
                continue
            stack.append("plain")
        if "drop" in stack:
            continue
        out.append(line)
    need(not stack, "unclosed ::: div in chapter source")
    return "\n".join(out)


TYPED_HEADING = re.compile(r"^(#{1,5}) (\d+(?:\.\d+)*) (.+?) \{\.unnumbered\}\s*$")


def number_id(num):
    return f"sec-{PREFIX}" + num.replace(".", "-")


def convert_main_headings(text):
    """'## 2.1 Participants {.unnumbered}' -> '### Participants {#sec-ch4-2-1}'."""
    out, ids = [], {}
    for line, in_code in iter_lines_outside_code(text):
        if not in_code and line.startswith("#"):
            m = TYPED_HEADING.match(line)
            need(m is not None, f"main-text heading without a typed number: {line!r}")
            hashes, num, title = m.groups()
            ids[num] = number_id(num)
            line = f"#{hashes} {title} {{#{ids[num]}}}"
        out.append(line)
    return "\n".join(out), ids


def convert_section_refs(text, ids):
    def repl(m):
        num = m.group(1)
        need(num in ids, f"typed reference to a section that does not exist: Section {num}")
        return "@" + ids[num]
    return re.sub(r"\bSection (\d+(?:\.\d+)+)\b", repl, text)


def convert_supp_headings(text):
    out = []
    for line, in_code in iter_lines_outside_code(text):
        if not in_code and line.startswith("#"):
            line = line.replace(" (dissertation only)", "")
            line = re.sub(r"\{#(sec-[A-Za-z0-9_-]+) \.unnumbered\}", r"{#\1}", line)
            line = line.replace(" {.unnumbered}", "")
            need(".unnumbered" not in line, f"unexpected heading form: {line!r}")
        out.append(line)
    return "\n".join(out)


def convert_supp_floats(text):
    """suppfig-x / supptbl-x -> fig-x / tbl-x (labels and references)."""
    text = re.sub(r"\{#suppfig-", "{#fig-", text)
    text = re.sub(r"\{#supptbl-", "{#tbl-", text)
    text = re.sub(r"@suppfig-", "@fig-", text)
    text = re.sub(r"@supptbl-", "@tbl-", text)
    return text


def collect_labels(text):
    labels = set(re.findall(r"\{#((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\}", text))
    labels |= set(re.findall(r"^#\| label: ((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\s*$", text, re.M))
    return {l for l in labels if not l.startswith(("sec-" + PREFIX, "fig-" + PREFIX, "tbl-" + PREFIX))}


def prefix_labels(text, labels):
    def lab(name):
        kind, rest = name.split("-", 1)
        return f"{kind}-{PREFIX}{rest}"

    text = re.sub(r"\{#((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\}",
                  lambda m: "{#" + lab(m.group(1)) + "}" if m.group(1) in labels else m.group(0), text)
    text = re.sub(r"^#\| label: ((?:sec|fig|tbl)-[A-Za-z0-9_-]+)(?=\s*$)",
                  lambda m: "#| label: " + lab(m.group(1)) if m.group(1) in labels else m.group(0),
                  text, flags=re.M)
    text = re.sub(r"@((?:sec|fig|tbl)-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*)",
                  lambda m: "@" + lab(m.group(1)) if m.group(1) in labels else m.group(0), text)
    return text


def renumber_chapters(text):
    """Chapter repo: Ch1 = CR:PI paper, Ch2 = pupillometry, Ch3 = this one.
    Dissertation: Chapters 2, 3, 4. Order matters (3 first)."""
    for old, new in (("3", "4"), ("2", "3"), ("1", "2")):
        text = re.sub(r"\bChapter " + old + r"\b", "Chapter " + new, text)
    return text


def drop_chunks_containing(text, needle):
    def repl(m):
        return "" if needle in m.group(0) else m.group(0)
    return re.sub(r"^```\{r[^}]*\}\n.*?^```\n", repl, text, flags=re.S | re.M)


def fix_rhat(text):
    return text.replace("*R̂*", "$\\hat{R}$").replace("R̂", "$\\hat{R}$")


# ----------------------------------------------------------------------------
# Bibliography
# ----------------------------------------------------------------------------
def bib_entries(text):
    out = {}
    for m in re.finditer(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", text, re.M):
        start = m.start()
        depth, i = 0, text.index("{", start)
        while True:
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out[m.group(2)] = text[start:i + 1]
    return out


def bib_field(entry, name):
    """Value of a BibTeX field ({...}, "...", or bare), or None."""
    m = re.search(r"(?im)^\s*" + name + r"\s*=\s*", entry)
    if not m:
        return None
    rest = entry[m.end():]
    if rest[:1] == "{":
        depth = 0
        for j, c in enumerate(rest):
            depth += (c == "{") - (c == "}")
            if depth == 0:
                return rest[1:j]
        return None
    if rest[:1] == '"':
        j = rest.index('"', 1)
        return rest[1:j]
    return re.match(r"[^,\n}]*", rest).group(0).strip()


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:50]


def entry_signature(entry):
    doi = bib_field(entry, "doi")
    year = bib_field(entry, "year")
    year = re.sub(r"\D", "", year or "")[:4]
    return (doi.lower().strip() if doi else None, norm_title(bib_field(entry, "title")), year)


def cited_keys(text):
    keys = set()
    for m in re.finditer(r"(?<![\w.])@([A-Za-z][\w:.-]*)", text):
        k = m.group(1).rstrip(".:-")
        if re.match(r"(sec|fig|tbl)-", k):
            continue
        keys.add(k)
    return keys


def map_keys(text, mapping):
    for old, new in mapping.items():
        text = re.sub(r"(?<![\w.])@" + re.escape(old) + r"(?![\w:-]*\w)", "@" + new, text)
    return text


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
SETUP_HEADER = '''# Chapter 4 setup — GENERATED by tools/sync_ch4.py from the modeling-pupil-DDM repo.
# Do not edit here; edit the chapter repo and re-run the sync.
# Sourced by Chapter_4_DDM_Older_Adults.qmd and Appendix_C_Chapter_4_Supplement.qmd.

proj_root <- normalizePath(".")
while (!file.exists(file.path(proj_root, "_quarto.yml"))) {
  parent <- dirname(proj_root)
  if (identical(parent, proj_root)) stop("could not find the dissertation root (_quarto.yml)")
  proj_root <- parent
}
params <- list(
  tables_dir = file.path(proj_root, "chapter4", "tables"),
  figures_dir = file.path(proj_root, "chapter4", "figures"),
  pupil_run = "%(pupil_run)s",
  draft_watermark = FALSE
)

'''

FRONT = '''---
execute:
  echo: false
  warning: false
  message: false
---

'''

SMALL_ON = "```{=latex}\n\\ucrsmalltablestrue\n```\n"
SMALL_OFF = "```{=latex}\n\\ucrsmalltablesfalse\n```\n"

SETUP_CHUNK = '''```{r ch4-setup}
#| include: false
source(file.path("chapter4", "setup.R"), local = knitr::knit_global())
```
'''


def build(src):
    qmd_path = os.path.join(src, SRC_QMD)
    need(os.path.isfile(qmd_path), f"not found: {qmd_path} (is --src the modeling-pupil-DDM repo?)")
    raw = read(qmd_path)
    yaml, body = split_front_matter(raw)
    title = yaml_scalar(yaml, "title")
    tables_dir = yaml_scalar(yaml, "tables_dir", "  ")
    figures_dir = yaml_scalar(yaml, "figures_dir", "  ")
    pupil_run = yaml_scalar(yaml, "pupil_run", "  ")
    need(re.search(r"^dissertation: true\s*$", yaml, re.M) is not None, "qmd YAML no longer has dissertation: true")

    # --- setup: the three include:false chunks before the abstract ---
    head, sep, rest = body.partition("\n# Abstract {.unnumbered}\n")
    need(sep, "could not find '# Abstract {.unnumbered}'")
    head = re.sub(r"<!--.*?-->", "", head, flags=re.S)
    chunks = re.findall(r"^```\{r\}\n(.*?)^```\n", head, re.S | re.M)
    need(len(chunks) == 2, f"expected 2 setup chunks before the abstract, found {len(chunks)}")
    c1, c2 = (re.sub(r"^#\|.*\n", "", c, flags=re.M) for c in chunks)
    need("proj_root <-" in c1, "first setup chunk no longer defines proj_root")
    old_src = 'source(file.path(proj_root, "R", "ch3_report_helpers.R"), local = knitr::knit_global())'
    need(old_src in c2, "helper source() line not found in setup chunk")
    c2 = c2.replace(old_src, 'source(file.path(proj_root, "chapter4", "R", "ch3_report_helpers.R"), local = knitr::knit_global())')
    setup_r = SETUP_HEADER % {"pupil_run": pupil_run} + c2

    # --- abstract / main text / supplement ---
    abstract, sep, rest = rest.partition("\n# 1 Introduction {.unnumbered}\n")
    need(sep, "could not find '# 1 Introduction {.unnumbered}'")
    main = "# 1 Introduction {.unnumbered}\n" + rest
    ref_hdr, sup_hdr = "\n# References {.unnumbered}\n", "\n# Supplementary Materials {.unnumbered}\n"
    need(ref_hdr in main and sup_hdr in main, "References / Supplementary Materials headings not found")
    supp = main[main.index(sup_hdr) + len(sup_hdr):]
    main = main[:main.index(ref_hdr)]
    main = re.sub(r"```\{=latex\}\n\\FloatBarrier\n```\s*$", "", main.rstrip() + "\n").rstrip() + "\n"

    main = resolve_meta_divs(main)
    supp = resolve_meta_divs(supp)
    supp = drop_chunks_containing(supp, "keys_used.csv")
    main = drop_chunks_containing(main, "keys_used.csv")

    main, ids = convert_main_headings(main)
    main = convert_section_refs(main, ids)
    supp = convert_section_refs(supp, ids)
    supp = convert_supp_headings(supp)
    supp = convert_supp_floats(supp)
    main = convert_supp_floats(main)  # main text may point into the supplement

    labels = collect_labels(main) | collect_labels(supp)
    main, supp = prefix_labels(main, labels), prefix_labels(supp, labels)
    abstract, main, supp = (renumber_chapters(t) for t in (abstract, main, supp))
    abstract, main, supp = (fix_rhat(t) for t in (abstract, main, supp))
    supp = landscape_tables(supp, LANDSCAPE_TABLES)

    for name, t in (("main text", main), ("supplement", supp)):
        need("when-meta" not in t, f"{name} still has a when-meta div")
        need("suppfig" not in t and "supptbl" not in t, f"{name} still uses Table S / Figure S floats")
        need("keys_used" not in t, f"{name} still writes keys_used.csv")
        need(not re.search(r"\bSection \d", t), f"{name} still has a typed section reference")
    for lbl in labels:
        need(not re.search(r"@" + re.escape(lbl) + r"(?![A-Za-z0-9_-])", main + supp), f"unprefixed reference left: @{lbl}")
    defined = set(re.findall(r"\{#((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\}", main + supp))
    defined |= set(re.findall(r"^#\| label: ((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\s*$", main + supp, re.M))
    for ref in set(re.findall(r"@((?:sec|fig|tbl)-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*)", main + supp)):
        need(ref in defined, f"cross-reference to an undefined label: @{ref}")

    note = (
        "This chapter is in preparation for submission for publication as:\n\n"
        f"> {AUTHORS} (in prep.). {sentence_case(title)}.\n"
    )
    chapter = FRONT + (
        "<!-- GENERATED by tools/sync_ch4.py from the modeling-pupil-DDM repo.\n"
        "     Do not edit here: edit the chapter repo and re-run the sync. -->\n\n"
        f"# {title} {{#{CH_LABEL}}}\n\n"
        + SETUP_CHUNK + "\n" + SMALL_ON + "\n"
        + note + "\n"
        "## Abstract {.unnumbered}\n\n"
        + abstract.strip() + "\n\n"
        + main.strip() + "\n\n" + SMALL_OFF
    )
    appendix = FRONT + (
        "<!-- GENERATED by tools/sync_ch4.py from the modeling-pupil-DDM repo.\n"
        "     Do not edit here: edit the chapter repo and re-run the sync. -->\n\n"
        f"# {APP_TITLE} {{#{APP_LABEL}}}\n\n"
        + SETUP_CHUNK + "\n" + SMALL_ON + "\n"
        + supp.strip() + "\n\n" + SMALL_OFF
    )

    # --- files to copy (tracked only) ---
    tables = [f for f in git_ls(src, tables_dir) if f.endswith((".csv", ".rds"))]
    figures = [f for f in git_ls(src, figures_dir) if f.endswith(".png")]
    need(any(f.endswith("inline_values.rds") for f in tables), "inline_values.rds is not tracked in the chapter repo")
    used_tbl = set(re.findall(r"\btbl\$([A-Za-z0-9_]+)", chapter + appendix + read(os.path.join(src, SRC_HELPER))))
    have_tbl = {os.path.splitext(os.path.basename(f))[0] for f in tables}
    missing_tbl = sorted(used_tbl - have_tbl)
    need(not missing_tbl, "chapter uses tables not tracked in the chapter repo: " + ", ".join(missing_tbl))
    used_fig = set(re.findall(r'params\$figures_dir, "([^"]+\.png)"', chapter + appendix))
    have_fig = {os.path.basename(f) for f in figures}
    missing_fig = sorted(used_fig - have_fig)
    need(not missing_fig, "chapter uses figures not tracked in the chapter repo: " + ", ".join(missing_fig))
    figures = [f for f in figures if os.path.basename(f) in used_fig]
    neuro = git_ls(src, SRC_NEURO)
    for f in NEURO_FILES:
        need(f"{SRC_NEURO}/{f}" in neuro, f"{SRC_NEURO}/{f} is not tracked in the chapter repo")

    helper = read(os.path.join(src, SRC_HELPER))
    old_neuro = 'output/neuropsych_demographics/'
    need(helper.count(old_neuro) == 2, "helper no longer reads output/neuropsych_demographics/ twice")
    helper = helper.replace(old_neuro, "chapter4/neuropsych/")
    helper = helper.replace("*R\\u0302*", "$\\\\hat{R}$").replace("R\\u0302", "$\\\\hat{R}$")
    need("R\\u0302" not in helper, "helper still writes R with a combining hat")
    old_formula_out = (
        '  knitr::asis_output(paste(c(\n'
        '    line("Model", "Formula"),\n'
        '    line(strrep("-", width_m), strrep("-", width_f)),\n'
        '    body,\n'
        '    ""\n'
        '  ), collapse = "\\n"))\n'
    )
    need(helper.count(old_formula_out) == 1, "ch3_tbl_formulas output block changed; update sync_ch4.py")
    helper = helper.replace(old_formula_out, (
        '  # Dissertation (tools/sync_ch4.py): a multiline table, so the formulas wrap\n'
        '  # inside the 6-in UCR text width instead of running off the page.\n'
        '  rule <- strrep("-", width_m + 2L + width_f)\n'
        '  rows_ml <- unlist(lapply(body, function(b) c(b, "")))\n'
        '  knitr::asis_output(paste(c(\n'
        '    rule,\n'
        '    line("Model", "Formula"),\n'
        '    line(strrep("-", width_m), strrep("-", width_f)),\n'
        '    rows_ml,\n'
        '    rule,\n'
        '    ""\n'
        '  ), collapse = "\\n"))\n'
    ))
    old_kb = '  names(shown) <- vapply(col_labels, .italic_stat_header, character(1))\n'
    old_body = '  body <- paste(as.character(kb), collapse = "\\n")\n'
    need(helper.count(old_kb) == 1 and helper.count(old_body) == 1, "make_table changed; update sync_ch4.py")
    helper = helper.replace(old_kb, old_kb +
        '  # Dissertation (tools/sync_ch4.py): fit the column widths to the UCR text width.\n'
        '  .diss_fit <- .diss_fit_table(shown, names(shown))\n'
        '  shown <- .diss_fit$shown\n')
    helper = helper.replace(old_body,
        '  body <- paste(.diss_pipe_widths(as.character(kb), .diss_fit$need), collapse = "\\n")\n')
    helper = helper.rstrip("\n") + "\n\n" + R_WIDTH_HELPERS
    helper = ("# GENERATED copy of R/ch3_report_helpers.R from modeling-pupil-DDM (paths adapted by tools/sync_ch4.py).\n"
              "# Do not edit here.\n") + helper

    # --- bibliography ---
    src_bib = bib_entries(read(os.path.join(src, SRC_BIB)))
    diss_text = read(os.path.join(ROOT, "references.bib"))
    diss_text_slot = None
    if BIB_BEGIN in diss_text:
        a = diss_text.index(BIB_BEGIN)
        b = diss_text.index(BIB_END) + len(BIB_END)
        diss_text_slot = diss_text[:a].rstrip("\n") + "\n\n@@MANAGED_BLOCK@@\n\n" + diss_text[b:].lstrip("\n")
        diss_text = diss_text[:a].rstrip("\n") + "\n" + diss_text[b:].lstrip("\n")
    diss_bib = bib_entries(diss_text)
    by_doi, by_ty = {}, {}
    for k, e in diss_bib.items():
        doi, t, y = entry_signature(e)
        if doi:
            by_doi.setdefault(doi, k)
        if t:
            by_ty.setdefault((t, y), k)
    cited = cited_keys(chapter + appendix)
    mapping, new_keys, missing = {}, [], []
    for k in sorted(cited):
        if k not in src_bib:
            if k not in diss_bib:
                missing.append(k)
            continue
        doi, t, y = entry_signature(src_bib[k])
        target = KEY_OVERRIDES.get(k) or (by_doi.get(doi) if doi else None) or by_ty.get((t, y))
        need(target is None or target in diss_bib, f"override target not in references.bib: {target}")
        if target:
            if target != k:
                mapping[k] = target
        elif k in diss_bib:
            raise SyncError(f"key {k} exists in references.bib for a different work; rename it in the chapter repo")
        else:
            new_keys.append(k)
    need(not missing, "cited but in neither bibliography: " + ", ".join(missing))
    chapter, appendix = map_keys(chapter, mapping), map_keys(appendix, mapping)
    block = BIB_BEGIN + "\n\n" + "\n\n".join(src_bib[k] for k in new_keys) + "\n\n" + BIB_END + "\n"
    if diss_text_slot is not None:  # replace the block where it is
        new_bib = diss_text_slot.replace("@@MANAGED_BLOCK@@", block.rstrip("\n"))
    else:
        new_bib = diss_text.rstrip("\n") + "\n\n" + block
    new_bib = re.sub(r"\n{3,}", "\n\n", new_bib).rstrip("\n") + "\n"

    # --- _quarto.yml ---
    qy = read(os.path.join(ROOT, "_quarto.yml"))
    need(f"    - {OUT_CHAPTER}\n" in qy, f"_quarto.yml: {OUT_CHAPTER} is not in the chapters list")
    if f"    - {OUT_APPENDIX}\n" not in qy:
        anchor = "    - Appendix_B_Chapter_3_Supplement.qmd\n"
        need(anchor in qy, "_quarto.yml: Appendix_B_Chapter_3_Supplement.qmd not found (needed as anchor)")
        qy = qy.replace(anchor, anchor + f"    - {OUT_APPENDIX}\n")

    # --- preamble (managed block at the end of the file) ---
    pre = read(os.path.join(ROOT, "ucr-preamble.tex"))
    need("\\usepackage{newunicodechar}" in pre, "ucr-preamble.tex does not load newunicodechar")
    if PREAMBLE_MARK in pre:  # managed block: replace it where it is
        a = pre.index(PREAMBLE_MARK)
        e = pre.index(PREAMBLE_END, a) + len(PREAMBLE_END)
        pre = pre[:a].rstrip("\n") + "\n" + PREAMBLE_ADD.strip("\n") + "\n" + pre[e:].lstrip("\n")
    else:
        pre = pre.rstrip("\n") + "\n" + PREAMBLE_ADD.strip("\n") + "\n"

    # --- index.qmd co-authorship sentence ---
    idx = read(os.path.join(ROOT, "index.qmd"))
    sentence = (
        f"Chapter 4 is in preparation for submission for publication as {AUTHORS} (in prep.). "
        f"{sentence_case(title)}. "
        "This chapter was conducted under the direction of Ilana J. Bennett and Aaron R. Seitz. "
    )
    idx = INDEX_RE.sub("", idx)
    need(idx.count(INDEX_ANCHOR) == 1, "index.qmd: funding sentence for Chapters 2, 3, and 4 not found")
    idx = idx.replace(INDEX_ANCHOR, sentence + INDEX_ANCHOR)

    try:
        commit = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = "unknown"
    source_txt = (
        "Chapter 4 assets, copied by tools/sync_ch4.py. Do not edit here.\n"
        "Source repo: modeling-pupil-DDM\n"
        f"Source commit: {commit}\n"
        f"Source file: {SRC_QMD}\n"
        f"Tables: {tables_dir}\n"
        f"Figures: {figures_dir}\n"
        f"Synced: {datetime.date.today().isoformat()}\n"
    )
    return dict(map_detail=mapping, chapter=chapter, appendix=appendix, setup=setup_r, helper=helper, bib=new_bib,
                quarto=qy, preamble=pre, index=idx, source_txt=source_txt, tables=tables,
                figures=figures, labels=labels, new_keys=new_keys, mapping=mapping, commit=commit)


def sentence_case(title):
    words = title.split(" ")
    return " ".join([words[0]] + [w if (w.isupper() and len(w) > 1) else w.lower() for w in words[1:]])


def write(src, r):
    def w(rel, txt):
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as fh:
            fh.write(txt)

    out = os.path.join(ROOT, OUT_DIR)
    for sub in ("tables", "figures", "neuropsych", "R"):
        shutil.rmtree(os.path.join(out, sub), ignore_errors=True)
        os.makedirs(os.path.join(out, sub))
    for f in r["tables"]:
        shutil.copy2(os.path.join(src, f), os.path.join(out, "tables", os.path.basename(f)))
    for f in r["figures"]:
        shutil.copy2(os.path.join(src, f), os.path.join(out, "figures", os.path.basename(f)))
    for f in NEURO_FILES:
        shutil.copy2(os.path.join(src, SRC_NEURO, f), os.path.join(out, "neuropsych", f))
    w(os.path.join(OUT_DIR, "R", "ch3_report_helpers.R"), r["helper"])
    w(os.path.join(OUT_DIR, "setup.R"), r["setup"])
    w(os.path.join(OUT_DIR, "SOURCE.txt"), r["source_txt"])
    w(OUT_CHAPTER, r["chapter"])
    w(OUT_APPENDIX, r["appendix"])
    w("references.bib", r["bib"])
    w("_quarto.yml", r["quarto"])
    w("ucr-preamble.tex", r["preamble"])
    w("index.qmd", r["index"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="path to a local checkout of modeling-pupil-DDM")
    ap.add_argument("--check", action="store_true", help="run every check but write nothing")
    args = ap.parse_args()
    src = os.path.abspath(args.src)
    if not os.path.isfile(os.path.join(ROOT, "_quarto.yml")):
        sys.exit("ERROR: run from the dissertation repo root (folder with _quarto.yml).")
    for f in (SRC_QMD, SRC_BIB, SRC_HELPER):
        if not os.path.isfile(os.path.join(src, f)):
            sys.exit(f"ERROR: missing in chapter repo: {f}")
    try:
        r = build(src)
    except SyncError as e:
        sys.exit(f"NOTHING WAS CHANGED. Check failed: {e}")
    summary = (f"source commit {r['commit']}; {len(r['tables'])} tables, {len(r['figures'])} figures; "
               f"{len(r['labels'])} labels prefixed; {len(r['mapping'])} citation keys mapped to existing entries; "
               f"{len(r['new_keys'])} Chapter 4 entries in references.bib")
    if args.check:
        print("CHECK OK: " + summary + ". Nothing written.")
        return
    write(src, r)
    print("SYNC OK: " + summary + ".")


if __name__ == "__main__":
    main()
