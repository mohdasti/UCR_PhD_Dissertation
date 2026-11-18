#!/usr/bin/env python3
"""
sync_ch3.py  —  Bring dissertation Chapter 3 in from the Psychometrics_Pupillometry repo
=======================================================================================
Usage (from the dissertation repo root):

    python3 tools/sync_ch3.py --src ../Psychometrics_Pupillometry

The chapter repo stays the single source of truth. Re-run this script whenever
the chapter changes there (e.g., after committee edits); it regenerates the
dissertation files below from scratch and never edits the chapter repo.

Reads (from --src):
    07_manuscript/chapter2/reports/chapter2_dissertation.qmd   chapter source
    07_manuscript/chapter2/reports/references.bib              its references
    07_manuscript/chapter2/export/<run id>/                    locked model export
    07_manuscript/chapter2/output/figures/{Paradigm,fig_predictions}.png
    R/ch2_report_helpers.R                                     number formatters

Writes (in the dissertation repo):
    Chapter_2.qmd        dissertation Chapter 3 (main text; numbers filled in by R)
    Appendix_B.qmd       its supplementary materials (Appendix B)
    chapter3/            setup.R, R helper, export, figures, SOURCE.txt
    references.bib       managed block of Chapter 3-only entries (between markers)
    _quarto.yml          adds Appendix_B.qmd to the appendices (once)
    ucr-preamble.tex     adds float/placeins/needspace (once)

Conversion rules (so the chapter matches Chapter 2 and UCR format):
  * Title becomes the chapter heading; the YAML abstract becomes
    "## Abstract {.unnumbered}", as in Chapter 2. Standalone fonts, margins,
    spacing, and font size are dropped: the UCR class controls them book-wide.
  * Main-text headings move down one level (the chapter title is level 1).
  * Per-chapter References are dropped; citations go to the single reference
    list at the end of the dissertation (UCR's preferred placement).
  * "Supplementary Materials" becomes Appendix B; its tables number B.1, B.2 ...
    (the standalone "Table S" counter hacks are removed).
  * Dissertation-only blocks are kept; manuscript-only blocks are dropped.
  * Every sec-/fig-/tbl- label gets a "ch3-" prefix so later chapters cannot
    collide with it.
  * Citation keys for works already in the dissertation bibliography are
    mapped to the existing keys, so no work is listed twice.
  * "the Supplementary Materials (Section ...)" in the main text becomes
    "Appendix B (Section ...)".
  * Chapter numbers in the prose follow the dissertation (the CR:PI paper is
    Chapter 2, the DDM study Chapter 4).
  * Tables are single-spaced and \\small book-wide (UCR permits slightly
    smaller type in tables), so Chapter 2's and Chapter 3's tables match.
  * Full-width figures taller than wide are drawn at 85% so figure and
    caption fit on one page.
  * Fixed table column widths that would overrun the UCR 6.0 in text width
    are narrowed (wide columns only).

Safety: everything is computed and checked in memory first. If any check
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

SRC_QMD = "07_manuscript/chapter2/reports/chapter2_dissertation.qmd"
SRC_BIB = "07_manuscript/chapter2/reports/references.bib"
SRC_EXPORT = "07_manuscript/chapter2/export"
SRC_FIGS = "07_manuscript/chapter2/output/figures"
SRC_HELPER = "R/ch2_report_helpers.R"
FIG_FILES = ["Paradigm.png", "fig_predictions.png"]

OUT_CHAPTER = "Chapter_2.qmd"
OUT_APPENDIX = "Appendix_B.qmd"
OUT_DIR = "chapter3"

CH_LABEL = "sec-ch3"
APP_LABEL = "sec-appendix-b"
APP_TITLE = "Supplementary Materials for Chapter 3"
PREFIX = "ch3-"

# Chapter-3 key -> existing dissertation key (same work, same edition).
KEY_MAP = {
    "astonjones2005": "Aston-Jones2005-dg",
    "azer2023": "Azer2023-ft",
    "barr2013": "Barr2013-maximal",
    "bates2015": "bates2015fitting",
    "beatty1982": "Beatty1982-wg",
    "brainard1997": "Brainard1997-fk",
    "carrasco2011": "Carrasco2011-wc",
    "dastgheib_inpress_effects": "Dastgheib2026-crpi",
    "gilzenrat2010": "Gilzenrat2010-ye",
    "kahneman1973": "Kahneman1973-jw",
    "murphy2011": "Murphy2011-nr",
    "vanderwel2018": "Van_der_Wel2018-ko",
    "wickens2008": "Wickens2008-pj",
    "zenon2014": "Zenon2014-ze",
}

# Fixed-effects table (Model, Term, Estimate, SE, Statistic, 95% CI, p): wider
# numeric columns so "Estimate", CIs, and "< .001" do not wrap at 6.0 in.
FIXED_WIDTHS = [1.15, 1.35, 0.55, 0.38, 0.95, 0.95, 0.42]


BIB_BEGIN = "% ===== BEGIN Chapter 3 references (managed by tools/sync_ch3.py; do not edit by hand) ====="
BIB_END = "% ===== END Chapter 3 references ====="

PREAMBLE_MARK = "% --- Chapter 3 float helpers (added by tools/sync_ch3.py) ---"
PREAMBLE_ADD = (
    "\n" + PREAMBLE_MARK + "\n"
    "\\usepackage{float}     % fig-pos: H\n"
    "\\usepackage{placeins}  % \\FloatBarrier\n"
    "\\usepackage{needspace} % \\Needspace\n"
    "% Tables in every chapter: single-spaced, and \\small unless the table\n"
    "% already chose a smaller size (UCR allows slightly smaller type in tables)\n"
    "\\makeatletter\n"
    "\\AtBeginEnvironment{longtable}{\\singlespacing\\ifx\\@currsize\\normalsize\\small\\fi}\n"
    "\\makeatother\n"
)


class SyncError(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise SyncError(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ----------------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------------
def split_front_matter(text):
    need(text.startswith("---\n"), "chapter qmd does not start with YAML front matter")
    end = text.index("\n---\n", 4)
    return text[4:end], text[end + 5:]


def yaml_title(yaml):
    m = re.search(r'^title:\s*"(.*)"\s*$', yaml, re.M)
    need(m is not None, "could not find a double-quoted title in the YAML")
    return m.group(1).replace('\\"', '"')


def yaml_abstract(yaml):
    lines = yaml.split("\n")
    need("abstract: |" in lines, "could not find 'abstract: |' in the YAML")
    i = lines.index("abstract: |") + 1
    out = []
    while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
        out.append(lines[i][2:])
        i += 1
    abstract = "\n".join(out).strip()
    need(len(abstract) > 200, "abstract looks empty")
    return abstract


def take_setup_chunk(body):
    m = re.search(r"^```\{r setup\}\n(.*?)^```\n", body, re.S | re.M)
    need(m is not None, "could not find the ```{r setup} chunk")
    code = m.group(1)
    code = re.sub(r"^#\|.*\n", "", code, flags=re.M)
    return code, body[:m.start()] + body[m.end():]


def iter_lines_outside_code(text):
    """Yield (line, in_code) for every line, tracking ``` fences."""
    in_code = False
    for line in text.split("\n"):
        fence = line.lstrip().startswith("```")
        yield line, in_code or fence
        if fence:
            in_code = not in_code


def resolve_meta_divs(text):
    """Keep content-visible when-meta=dissertation, drop content-hidden ones."""
    out, stack = [], []  # stack of 'keep' / 'drop' / 'plain'
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


def drop_raw_latex_blocks(text, must_contain):
    """Remove ```{=latex} blocks whose content mentions any of must_contain."""
    def repl(m):
        return "" if any(k in m.group(1) for k in must_contain) else m.group(0)
    return re.sub(r"```\{=latex\}\n(.*?)```\n", repl, text, flags=re.S)


def demote_headings(text):
    out = []
    for line, in_code in iter_lines_outside_code(text):
        if not in_code and re.match(r"#{1,5} ", line):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def clean_headings(text):
    out = []
    for line, in_code in iter_lines_outside_code(text):
        if not in_code and line.startswith("#"):
            line = line.replace(" (dissertation only)", "")
        out.append(line)
    return "\n".join(out)


def collect_labels(text):
    labels = set(re.findall(r"\{#((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\}", text))
    labels |= set(re.findall(r"^#\| label: ((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\s*$", text, re.M))
    return labels


def prefix_labels(text, labels):
    def lab(name):
        kind, rest = name.split("-", 1)
        return f"{kind}-{PREFIX}{rest}"

    def def_repl(m):
        return "{#" + lab(m.group(1)) + "}" if m.group(1) in labels else m.group(0)

    def chunk_repl(m):
        return "#| label: " + lab(m.group(1)) if m.group(1) in labels else m.group(0)

    def ref_repl(m):
        name = m.group(2)
        return m.group(1) + lab(name) if name in labels else m.group(0)

    text = re.sub(r"\{#((?:sec|fig|tbl)-[A-Za-z0-9_-]+)\}", def_repl, text)
    text = re.sub(r"^#\| label: ((?:sec|fig|tbl)-[A-Za-z0-9_-]+)(?=\s*$)", chunk_repl, text, flags=re.M)
    text = re.sub(r"(@)((?:sec|fig|tbl)-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*)", ref_repl, text)
    return text


def map_citation_keys(text):
    for old, new in KEY_MAP.items():
        text = re.sub(r"(?<![\w.])@" + re.escape(old) + r"(?![\w:-]*\w)", "@" + new, text)
    return text


TEXT_WIDTH_IN = 6.0  # UCR: 8.5 in page, 1.5 in left and 1 in right margins


def fit_widths(text, default_sep_pt=6.0):
    """Fit fixed table column widths to the UCR text width.

    Each run of consecutive lines holding p{...in} widths is one table's column
    vector. Its rendered width is the sum of the widths plus 2 x tabcolsep per
    column (tabcolsep is read from the same code chunk when the chunk sets it,
    else LaTeX's default 6 pt). If that exceeds the text width, the excess is
    taken only from the wide (>= 1 in) columns, in proportion to their width,
    so narrow numeric columns keep their size.
    """
    parts = re.split(r"(^```\{r[^}]*\}\n.*?^```$)", text, flags=re.S | re.M)
    out = []
    for part in parts:
        m = re.search(r'tabcolsep = "([0-9.]+)pt"', part)
        sep = float(m.group(1)) if m else default_sep_pt
        out.append(_fit_part(part, sep))
    text = "".join(out)
    # let long cells wrap inside the narrower columns
    return text.replace('\\\\mbox{Did not converge}', "Did not converge")


def _fit_part(text, sep_pt):
    lines = text.split("\n")
    pat = re.compile(r"p\{([0-9]*\.?[0-9]+)in\}")
    i = 0
    while i < len(lines):
        if not pat.search(lines[i]):
            i += 1
            continue
        j = i
        while j < len(lines) and pat.search(lines[j]):
            j += 1
        widths = [float(m.group(1)) for ln in lines[i:j] for m in pat.finditer(ln)]
        avail = TEXT_WIDTH_IN - len(widths) * 2 * sep_pt / 72.27 - 0.03
        excess = sum(widths) - avail
        wide = sum(w for w in widths if w >= 1.0)
        if excess > 0 and wide > excess:
            factor = (wide - excess) / wide
            def repl(m):
                w = float(m.group(1))
                return "p{%.2fin}" % (w * factor if w >= 1.0 else w)
            for k in range(i, j):
                lines[k] = pat.sub(repl, lines[k])
        i = j
    return "\n".join(lines)


def fit_tall_figures(text):
    """A full-width figure taller than it is wide does not fit on a UCR page
    with its caption; draw such figures at 85% width."""
    def repl(m):
        chunk = m.group(0)
        w = re.search(r"^#\| fig-width: ([0-9.]+)", chunk, re.M)
        h = re.search(r"^#\| fig-height: ([0-9.]+)", chunk, re.M)
        if w and h and float(h.group(1)) > 0.9 * float(w.group(1)):
            chunk = chunk.replace('#| out-width: "100%"', '#| out-width: "85%"')
        return chunk
    return re.sub(r"^```\{r[^}]*\}\n.*?^```$", repl, text, flags=re.S | re.M)


def renumber_chapters(text):
    """The chapter repo numbers chapters as Ch1 = CR:PI paper, Ch3 = DDM study.
    In the dissertation they are Chapter 2 and Chapter 4 (Chapter 1 is the
    General Introduction). Order matters: 3 -> 4 before 1 -> 2."""
    text = re.sub(r"\bChapter 3\b", "Chapter 4", text)
    text = re.sub(r"\bChapter 1\b", "Chapter 2", text)
    return text


def rewrite_paths(text):
    text = text.replace('"07_manuscript", "chapter2", "export"', '"chapter3", "export"')
    text = text.replace('"07_manuscript", "chapter2", "output", "figures"', '"chapter3", "figures"')
    return text


# ----------------------------------------------------------------------------
# Bibliography
# ----------------------------------------------------------------------------
def bib_entries(text):
    """Return {key: raw entry text} for a .bib file."""
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


def cited_keys(text):
    keys = set()
    for m in re.finditer(r"(?<![\w.])@([A-Za-z][\w:.-]*)", text):
        k = m.group(1).rstrip(".:-")
        if re.match(r"(sec|fig|tbl)-", k):
            continue
        keys.add(k)
    return keys


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
SETUP_HEADER = '''# Chapter 3 setup — GENERATED by tools/sync_ch3.py from the chapter repo.
# Do not edit here; edit the chapter repo and re-run the sync.
# Sourced by Chapter_2.qmd and Appendix_B.qmd.

'''

ROOT_FINDER = '''proj_root <- normalizePath(".")
while (!file.exists(file.path(proj_root, "_quarto.yml"))) {
  parent <- dirname(proj_root)
  if (identical(parent, proj_root)) stop("could not find the dissertation root (_quarto.yml)")
  proj_root <- parent
}
'''

FRONT = '''---
execute:
  echo: false
  warning: false
  message: false
---

'''

SETUP_CHUNK = '''```{r ch3-setup}
#| include: false
source(file.path("chapter3", "setup.R"), local = knitr::knit_global())
```
'''


def build(src):
    qmd_path = os.path.join(src, SRC_QMD)
    need(os.path.isfile(qmd_path), f"not found: {qmd_path} (is --src the chapter repo?)")
    raw = read(qmd_path)
    yaml, body = split_front_matter(raw)
    title = yaml_title(yaml)
    abstract = yaml_abstract(yaml)

    run_m = re.search(r'"export", "(ch2fit_[0-9_]+)"', raw)
    need(run_m is not None, "could not find the export run id in the setup chunk")
    run_id = run_m.group(1)
    need(os.path.isdir(os.path.join(src, SRC_EXPORT, run_id)), f"export folder missing: {run_id}")

    setup_code, body = take_setup_chunk(body)

    # setup.R: dissertation root finder, helper path, export path
    pr = re.search(r"^proj_root <- if \(.*?\n\}\n", setup_code, re.S | re.M)
    need(pr is not None, "could not find the proj_root block in the setup chunk")
    setup_code = setup_code[:pr.start()] + ROOT_FINDER + setup_code[pr.end():]
    old_src = 'source(file.path(proj_root, "R/ch2_report_helpers.R"))'
    need(old_src in setup_code, "helper source() line not found in setup chunk")
    setup_code = setup_code.replace(old_src, 'source(file.path(proj_root, "chapter3", "R", "ch2_report_helpers.R"))')
    setup_code = rewrite_paths(fit_widths(setup_code, default_sep_pt=2.5))
    fw = re.search(r"^fixed_widths <- c\(\n(.*?)\n\)\n", setup_code, re.S | re.M)
    need(fw is not None, "fixed_widths vector not found in setup chunk")
    need(len(re.findall(r"p\{", fw.group(1))) == len(FIXED_WIDTHS), "fixed_widths has an unexpected number of columns")
    setup_code = setup_code[:fw.start()] + "fixed_widths <- c(\n" + ",\n".join(
        '  ">{\\\\raggedright\\\\arraybackslash}p{%.2fin}"' % w for w in FIXED_WIDTHS
    ) + "\n)\n" + setup_code[fw.end():]
    need("07_manuscript" not in setup_code, "setup still refers to 07_manuscript")

    # split main text / supplement
    ref_hdr = "\n# References {.unnumbered}\n"
    sup_hdr = "\n# Supplementary Materials\n"
    need(ref_hdr in body and sup_hdr in body, "References / Supplementary Materials headings not found")
    main = body[:body.index(ref_hdr)]
    supp = body[body.index(sup_hdr) + len(sup_hdr):]
    need(main.lstrip().startswith("# Introduction"), "main text should start with '# Introduction'")

    # transforms
    main = resolve_meta_divs(main)
    supp = resolve_meta_divs(supp)
    supp = drop_raw_latex_blocks(supp, ["ch2maintable", "\\thetable"])
    main = demote_headings(main)
    main, supp = clean_headings(main), clean_headings(supp)
    labels = collect_labels(main) | collect_labels(supp)
    main, supp = prefix_labels(main, labels), prefix_labels(supp, labels)
    main, supp = map_citation_keys(main), map_citation_keys(supp)
    main, supp = fit_widths(main), fit_widths(supp)
    main, supp = fit_tall_figures(main), fit_tall_figures(supp)
    main, supp = rewrite_paths(main), rewrite_paths(supp)
    main = re.sub(r"\bthe Supplementary Materials \((@sec-[A-Za-z0-9_-]+)\)", r"Appendix B (\1)", main)
    need("Supplementary Materials" not in main, "main text still says 'Supplementary Materials'")
    abstract = renumber_chapters(abstract)
    main, supp = renumber_chapters(main), renumber_chapters(supp)
    for name, t in (("main text", main), ("supplement", supp)):
        need("07_manuscript" not in t, f"{name} still refers to 07_manuscript")
        need("when-meta" not in t, f"{name} still has a when-meta div")
        need("ch2maintable" not in t, f"{name} still uses the Table S counter")
    for lbl in labels:  # no un-prefixed reference may remain
        need(not re.search(r"@" + re.escape(lbl) + r"(?![A-Za-z0-9_-])", main + supp), f"unprefixed reference left: @{lbl}")

    chapter = FRONT + (
        "<!-- GENERATED by tools/sync_ch3.py from the Psychometrics_Pupillometry repo.\n"
        "     Do not edit here: edit the chapter repo and re-run the sync. -->\n\n"
        f"# {title} {{#{CH_LABEL}}}\n\n"
        + SETUP_CHUNK + "\n"
        "## Abstract {.unnumbered}\n\n"
        f"{abstract}\n\n"
        + main.strip() + "\n"
    )
    appendix = FRONT + (
        "<!-- GENERATED by tools/sync_ch3.py from the Psychometrics_Pupillometry repo.\n"
        "     Do not edit here: edit the chapter repo and re-run the sync. -->\n\n"
        f"# {APP_TITLE} {{#{APP_LABEL}}}\n\n"
        + SETUP_CHUNK + "\n"
        + supp.strip() + "\n"
    )

    # bibliography
    src_bib = bib_entries(read(os.path.join(src, SRC_BIB)))
    diss_bib_text = read(os.path.join(ROOT, "references.bib"))
    if BIB_BEGIN in diss_bib_text:
        a = diss_bib_text.index(BIB_BEGIN)
        b = diss_bib_text.index(BIB_END) + len(BIB_END)
        diss_bib_text = diss_bib_text[:a].rstrip("\n") + "\n" + diss_bib_text[b:].lstrip("\n")
    diss_bib = bib_entries(diss_bib_text)
    cited = cited_keys(chapter + appendix)
    for k in KEY_MAP.values():
        need(k not in cited or k in diss_bib, f"mapped key not in dissertation bib: {k}")
    new_keys = sorted(k for k in cited if k not in diss_bib)
    missing = [k for k in new_keys if k not in src_bib]
    need(not missing, "cited but in neither bibliography: " + ", ".join(missing))
    block = BIB_BEGIN + "\n\n" + "\n\n".join(src_bib[k] for k in new_keys) + "\n\n" + BIB_END + "\n"
    new_bib = diss_bib_text.rstrip("\n") + "\n\n" + block

    # _quarto.yml
    qy = read(os.path.join(ROOT, "_quarto.yml"))
    need("  appendices:\n    - Appendix_A.qmd\n" in qy, "_quarto.yml: appendices block not found")
    if "Appendix_B.qmd" not in qy:
        qy = qy.replace("  appendices:\n    - Appendix_A.qmd\n", "  appendices:\n    - Appendix_A.qmd\n    - Appendix_B.qmd\n")
    need("    - Chapter_2.qmd\n" in qy, "_quarto.yml: Chapter_2.qmd not in chapters")

    pre = read(os.path.join(ROOT, "ucr-preamble.tex"))
    if PREAMBLE_MARK not in pre:
        pre = pre.rstrip("\n") + "\n" + PREAMBLE_ADD

    try:
        commit = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = "unknown (not a git checkout)"
    source_txt = (
        "Chapter 3 assets, copied by tools/sync_ch3.py. Do not edit here.\n"
        f"Source repo: Psychometrics_Pupillometry\n"
        f"Source commit: {commit}\n"
        f"Export run: {run_id}\n"
        f"Synced: {datetime.date.today().isoformat()}\n"
    )
    return {
        "chapter": chapter, "appendix": appendix, "setup": SETUP_HEADER + setup_code,
        "bib": new_bib, "quarto": qy, "preamble": pre, "source_txt": source_txt,
        "run_id": run_id, "new_keys": new_keys, "labels": labels, "commit": commit,
    }


def write(src, r):
    def w(rel, txt):
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as fh:
            fh.write(txt)

    out = os.path.join(ROOT, OUT_DIR)
    for sub in ("export", "figures", "R"):
        shutil.rmtree(os.path.join(out, sub), ignore_errors=True)
    os.makedirs(os.path.join(out, "R"), exist_ok=True)
    os.makedirs(os.path.join(out, "figures"), exist_ok=True)
    shutil.copytree(os.path.join(src, SRC_EXPORT, r["run_id"]), os.path.join(out, "export", r["run_id"]))
    for f in FIG_FILES:
        shutil.copy2(os.path.join(src, SRC_FIGS, f), os.path.join(out, "figures", f))
    shutil.copy2(os.path.join(src, SRC_HELPER), os.path.join(out, "R", "ch2_report_helpers.R"))
    w(os.path.join(OUT_DIR, "setup.R"), r["setup"])
    w(os.path.join(OUT_DIR, "SOURCE.txt"), r["source_txt"])
    w(OUT_CHAPTER, r["chapter"])
    w(OUT_APPENDIX, r["appendix"])
    w("references.bib", r["bib"])
    w("_quarto.yml", r["quarto"])
    w("ucr-preamble.tex", r["preamble"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="path to a local checkout of Psychometrics_Pupillometry")
    ap.add_argument("--check", action="store_true", help="run every check but write nothing")
    args = ap.parse_args()
    src = os.path.abspath(args.src)
    if not os.path.isfile(os.path.join(ROOT, "_quarto.yml")):
        sys.exit("ERROR: run from the dissertation repo root (folder with _quarto.yml).")
    for f in FIG_FILES:
        if not os.path.isfile(os.path.join(src, SRC_FIGS, f)):
            sys.exit(f"ERROR: figure missing in chapter repo: {SRC_FIGS}/{f}")
    if not os.path.isfile(os.path.join(src, SRC_HELPER)):
        sys.exit(f"ERROR: helper missing in chapter repo: {SRC_HELPER}")
    try:
        r = build(src)
    except SyncError as e:
        sys.exit(f"NOTHING WAS CHANGED. Check failed: {e}")
    if args.check:
        print(f"CHECK OK: source commit {r['commit']}, export {r['run_id']}, "
              f"{len(r['labels'])} labels, {len(r['new_keys'])} new bib entries. Nothing written.")
        return
    write(src, r)
    print(f"SYNC OK: source commit {r['commit']}, export {r['run_id']}; wrote {OUT_CHAPTER}, "
          f"{OUT_APPENDIX}, {OUT_DIR}/; {len(r['labels'])} labels prefixed; "
          f"{len(r['new_keys'])} Chapter 3 entries in references.bib.")


if __name__ == "__main__":
    main()
