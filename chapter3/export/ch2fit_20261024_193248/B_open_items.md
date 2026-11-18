# Open items

These were not resolved in this phase. None of them changed a model or a sentence outside Part E.

## Confirm with Mohammad

- **[CONFIRM: unit]** The pupil time-course y-axis is "Pupil diameter change from pre-squeeze baseline (a.u.)". No pupil unit is stated in the chapter or in the waveform file. The estimates (for example the grip-window and TEPR coefficients) are on that same unstated scale.
- **[CONFIRM: downsampling]** The chapter says the eye tracker sampled at 2,000 Hz and that the analyzed files are the 250 Hz recordings. The step that took 2,000 Hz to 250 Hz is not in the files this export reads.
- **[CONFIRM: release cue]** The chapter says grip release was cued at 4.45 s. The paradigm image says "hold until blue frame" and shows a 0.25 s blank between the probe and the response screen. It does not print 4.45 s. This sentence was not edited.

## Not in the supplied files

- **T-MoCA.** It is not a column in `LC Aging Subject Data master spreadsheet - demographics.csv` or in `bap_beh_subjxtaskdata_v2.csv`. The preprint's neuropsych spreadsheet is not in the share. Table 1 has no T-MoCA column and no placeholder.
- **Education coding.** All 68 behavioral participants match the demographics file and all 68 have a numeric age. Four do not have a numeric education year: BAP001 and BAP003 are blank; BAP122 is "less than 12"; BAP172 is "<12". The education mean uses the 64 numeric values. Age mean is 69.57 (printed 69.6) against the preprint's 69.5. The SD is 6.42 (printed 6.4) against 6.4. Female is 34/68 = 50%, which matches. The preprint figures were not adjusted.

## Not run

- Refit of M1 without the top offset.
- A grip-force adherence sentence. The chapter still points at the manipulation check in the preprint.

## Figure notes

- The pupil smooth uses `winsorize_subject_waveforms` and then `mgcv::gam(y ~ s(t, k = 10), method = "REML")`. It does not call `fit_tepr_gam_curves`, because that helper subtracts the smooth at squeeze onset and would undo the pre-squeeze baseline.
- Helper copy: `R/tepr_waveform_helpers.R`, md5 recorded in `run_log.txt`.
- Participant-mean P(different) is higher, not lower, under high effort in one cell: visual offset 0.24. The trial-mean difference is negative in all 10 cells, which is what the Results sentence states. The sentence was not rewritten. The figure points are participant means.
