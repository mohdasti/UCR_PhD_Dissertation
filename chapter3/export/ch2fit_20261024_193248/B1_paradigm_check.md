# B1. Paradigm figure

The image is `07_manuscript/chapter2/output/figures/Paradigm.png`. It was read and not edited. The qmd includes it with `stopifnot(file.exists(paradigm_path))`.

## Printed times and labels

- "1.5 - 4.5s" on the inter-trial interval.
- "3s" on the grip gauge.
- Then, in order, "0.25s", "0.5s", "0.1s", "0.5s", "0.1s", "0.25s", "3s", "3s".
- A total of "10.7s" along the arrow.
- "Low (5% MVC) or High (40% MVC)".
- "MVC", "grip gauge and feedback", "hold until blue frame".
- "blank", "fixation".
- Auditory: "standard 1000 Hz tone", "ISI", "1000 + offset Hz tone".
- Visual: "Standard patch", "ISI", "Standard patch + offset Contrast".
- "blank", "response 1", "Same or Different?".
- "response 2", "Confidence?", buttons "1 2 3 4".
- "Offsets: 0.06, 0.12, 0.24, or 0.48".

No absolute clock time is printed. In particular the image does not print 3.00, 3.25, 3.75, 3.85, 4.35, 4.45, 4.70, 7.70, or 10.70.

## Comparison with the design

The printed durations are 3 + 0.25 + 0.5 + 0.1 + 0.5 + 0.1 + 0.25 + 3 + 3 = 10.7 s. That sum matches the design intervals:

| Printed duration | Design interval |
|---|---|
| 3 s gauge | 0–3.00 s |
| 0.25 s blank | 3.00–3.25 s |
| 0.5 s fixation | 3.25–3.75 s |
| 0.1 s standard | 3.75–3.85 s |
| 0.5 s ISI | 3.85–4.35 s |
| 0.1 s probe | 4.35–4.45 s |
| 0.25 s blank | 4.45–4.70 s |
| 3 s response | 4.70–7.70 s |
| 3 s confidence | 7.70–10.70 s |

ITI 1.5–4.5 s matches. Effort levels 5% and 40% MVC match. Visual offsets 0.06, 0.12, 0.24, and 0.48 match. Auditory standard 1000 Hz matches the design frequency; the image does not use a thousands separator.

## Mismatches

- The image gives durations, not the clock times used in the chapter (standard at 3.75 s, probe at 4.35 s, release at 4.45 s, response 4.70–7.70 s).
- "hold until blue frame" is the release instruction on the figure. The figure does not say that a release cue occurred at 4.45 s. Whether that cue was shown is an open item in `B_open_items.md`.
- The auditory labels are "1000 Hz" and "1000 + offset Hz". The chapter text uses "1,000 Hz". The image was not edited.
