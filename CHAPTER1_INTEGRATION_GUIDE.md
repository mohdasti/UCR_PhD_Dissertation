# Chapter 1 Integration Guide

## ✅ What I've Done

1. **Created `Chapter_1.qmd`** - Your LCYA manuscript is now formatted as a Quarto chapter with:
   - Proper Quarto markdown syntax
   - Citation keys (e.g., `@westbrook2015cognitive`) ready for your bibliography
   - Figure references using Quarto cross-references (e.g., `@fig-performance`)
   - Section headers and formatting

2. **Created `figures/chapter1/` directory** with a README explaining which figures you need to copy from your LCYA repo

3. **The chapter is already listed in `_quarto.yml`** as `Chapter_1.qmd`

## 📋 What You Need to Do

### Step 1: Copy Figures from LCYA Repository

From your LCYA repository at `https://github.com/mohdasti/LCYA`, copy these figures:

```bash
cd ~/Documents/GitHub/UCR_PhD_Dissertation/figures/chapter1

# Copy from LCYA repo (adjust paths as needed)
cp ~/path/to/LCYA/figures/publication/Figure1_*.png figure1_task_schematics.png
cp ~/path/to/LCYA/figures/publication/Figure2_*.png figure2_performance.png
cp ~/path/to/LCYA/figures/publication/Figure3_*.png figure3_pupil_waveforms.png
cp ~/path/to/LCYA/figures/publication/Figure4_*.png figure4_auc_plots.png
```

**Note:** The original markdown had base64-encoded images. You'll need the actual PNG files from your LCYA repository's `figures/publication/` folder.

### Step 2: Add References to `references.bib`

Your Chapter 1 uses many citations. You need to add BibTeX entries for all references. Here are some key ones you'll need:

- `@westbrook2015cognitive` - Westbrook & Braver, 2015
- `@kahneman1966pupil` - Kahneman & Beatty, 1966
- `@beatty1982task` - Beatty, 1982
- `@azer2023detrimental` - Azer et al., 2023
- `@park2021concurrent` - Park et al., 2021
- ... (and many more from your manuscript)

**Option A:** Extract from your LCYA manuscript reference manager (Zotero, Mendeley, etc.)

**Option B:** I can help you convert the references from your manuscript if you provide them

### Step 3: Update `index.qmd` Front Matter

The `index.qmd` file has placeholder text. Update it with your actual dissertation info:

```latex
\title{Your Dissertation Title Here}
\author{Mohammad Dastgheib}
\chair{Your Chair's Name}
\committee{Chair Name, Chairperson \\ Member 2 \\ Member 3}
```

### Step 4: Test the Build

Try rendering your dissertation:

```bash
cd ~/Documents/GitHub/UCR_PhD_Dissertation
quarto render
```

This will create both HTML and PDF versions.

## 🔧 Optional: Create Chapter 2 and 3 Placeholders

If you want, I can create placeholder files for Chapter 2 and Chapter 3 (which are already listed in `_quarto.yml`).

## 📚 References Format

Your chapter uses Pandoc citation syntax:
- `[@author2020]` - Citation in parentheses
- `@author2020` - Author (2020) format
- `[@author2020; @another2021]` - Multiple citations

All citation keys need matching BibTeX entries in `references.bib`.

## 🖼️ Figure Notes

The figures are referenced using Quarto's cross-reference syntax:
- `@fig-task-schematics` refers to Figure 1
- `@fig-performance` refers to Figure 2
- `@fig-pupil-waveforms` refers to Figure 3
- `@fig-auc-plots` refers to Figure 4

These will automatically number and create clickable cross-references in your PDF/HTML output.

## ❓ Questions?

Let me know if you need help with:
- Extracting and formatting the bibliography
- Creating the other chapter files
- Adjusting the formatting
- Anything else!
