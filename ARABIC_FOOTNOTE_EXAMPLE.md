# Arabic Footnote Example for Quarto

## How to Use Arabic Text in Footnotes

In your Quarto markdown files (`.qmd`), you can now use Arabic text in footnotes using the inline footnote syntax combined with the `\ar{}` command we defined in `ucr-preamble.tex`.

### Syntax

```markdown
Regular English text^[\ar{Arabic text here}] continues in English.
```

### Example 1: Simple Arabic Footnote

```markdown
The concept of gratitude is deeply embedded in many cultures^[\ar{شكراً}] and plays an important role in human relationships.
```

**Result:** The word "شكراً" (shukran, meaning "thank you") will appear in the footnote in Arabic script with proper right-to-left rendering.

### Example 2: Mixed English and Arabic in Footnote

```markdown
This research was conducted in collaboration with colleagues from Iran^[The Persian word for "research" is \ar{تحقیق} (tahghigh).] and builds upon previous work in cognitive psychology.
```

**Result:** The footnote will contain both English and Arabic text, with proper right-to-left rendering for the Arabic portion.

### Example 3: Multiple Arabic Words

```markdown
The participants expressed their appreciation^[\ar{با تشکر از شما} - "with thanks to you" in Persian] for being part of this study.
```

### Example to Add to Chapter_1.qmd

Here's a concrete example you can add to your Chapter 1:

```markdown
## Acknowledgments (in the chapter body, not front matter)

We are grateful to all participants who volunteered their time for this study^[\ar{با سپاس} - with gratitude]. Their dedication made this research possible.
```

### Important Notes

1. **Font Requirement:** The Amiri font must be installed on your system. It's a free, open-source Arabic font that comes pre-installed on macOS.

2. **XeLaTeX Required:** Make sure you're using XeLaTeX as your PDF engine (already configured in `_quarto.yml`).

3. **Right-to-Left Text:** The `\textarabic{}` command handles right-to-left text rendering automatically.

4. **Testing:** After adding Arabic text, render your PDF with:
   ```bash
   quarto render --to pdf
   ```

5. **Troubleshooting:** If Arabic text doesn't render:
   - Verify Amiri font is installed: `fc-list | grep Amiri`
   - Check the LaTeX log for font errors
   - Try alternative fonts like "Arial" or "Scheherazade New"

### Alternative Fonts

If Arial Unicode MS doesn't work on your system, you can change the font in `ucr-preamble.tex`:

```latex
% Instead of Arial Unicode MS, try:
\newfontfamily\arabicfont[Script=Arabic]{Geeza Pro}
% or
\newfontfamily\arabicfont[Script=Arabic]{Baghdad}
% or (if you install it)
\newfontfamily\arabicfont[Script=Arabic]{Amiri}
```

## Persian vs. Arabic Script

Note: Persian (Farsi) uses the Arabic script with a few additional letters. The configuration above works for both Arabic and Persian text. The `\ar{}` command handles both scripts correctly.

## Why `\ar{}` instead of `\textarabic{}`?

We use a simpler approach with `fontspec` instead of `polyglossia` to avoid package loading conflicts with the UCR LaTeX class. The `\ar{}` command:
- Switches to the Arabic font
- Enables right-to-left text direction (`\textdir TRT`)
- Works seamlessly in footnotes and inline text

This approach is more compatible with complex LaTeX templates while still providing proper Arabic text rendering.
