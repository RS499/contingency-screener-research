# URTC camera-ready edits vs the STS body — overlap check (lead, 2026-09-27)

Why: `notes/ai-prompt-log.md` 2026-09-13 records an AI session that applied text edits to the URTC
camera-ready, and the STS .tex header (l.3) says the body is "VERBATIM from the URTC conference version".
The exact pre/post-09-13 files are not in git (logged sha256 55e2ba28… / 510fb930… match no commit), so
AI-edited spans cannot be isolated exactly. Upper bound used here: sentences present in the committed
camera-ready (`8b88a99`) but absent from the submitted version (`8cefaa7`, 08-08) — this set mixes AI and
human edits. Sentences split on terminal punctuation, ≥ 8 words, comments/bibliography dropped, we/our → I/my.

- Camera-ready sentences: 81; new vs submitted: 33; STS body sentences: 128.
- Camera-ready sentences verbatim in STS: 18 (all of them already in the submitted version).
- **New (possibly AI-edited) sentences verbatim in STS: 0.**
- New sentences with similarity ≥ 0.8 to an STS sentence: 4; ≥ 0.6: 12.

Interpretation (fact only): the STS body does not carry any camera-ready-only sentence verbatim; the
near matches below are the only candidates for AI-refined wording surviving into the STS report. RULES2027
App. 4: "Guidance or refinement after the initial document has been completed can be done with explicit
citation and a log." Whether to cite, rewrite, or both is the author's decision (ledger P-002 / P-012).

## Candidates (similarity ≥ 0.6), camera-ready sentence → closest STS sentence

**0.97**
- URTC camera-ready: \cite{christianson2025} designed an input-convex network that completely removes false negatives, although that claim is only relevant to DC power flow models, not the AC model our study uses.
- STS: \cite{christianson2025} designed an input-convex network that completely removes false negatives, although that claim is only relevant to DC power flow models, not the AC power flow model my study uses.

**0.91**
- URTC camera-ready: The two algorithms are a ridge linear regression using standardized inputs and a histogram-based gradient-boosted tree ensemble \cite{sklearn}.
- STS: The two algorithms used in this study are a ridge linear regression model using standardized inputs and a histogram-based gradient-boosted tree ensemble \cite{sklearn}.

**0.87**
- URTC camera-ready: \section{Background} A per-unit voltage normalizes power grid values into simple decimals (where 1.0 is nominal), so 0.94 per unit indicates a 6\ An AC power flow solver gets the final voltages across a network after a single-element failure.
- STS: \section{Background} \label{sec:background} A per-unit (pu) voltage normalizes power grid values into simple decimals (where 1.0 is nominal), where 0.94 per unit indicates a 6\ An AC power flow solver is used to get the final voltages across a network after a single-element failure.

**0.84**
- URTC camera-ready: That method bounds the proportion of skipped cases that are unsafe, while our gate subtracts a margin of error from each prediction.
- STS: That method uses a bound for the proportion of skipped cases that are unsafe, while the gate uses a margin of error that is subtracted from each prediction.

**0.79**
- URTC camera-ready: Several approaches employ surrogate models for N-1 contingency tests.
- STS: There have been several approaches when it comes to employing surrogate models for N-1 contingency tests.

**0.77**
- URTC camera-ready: Because the math is non-linear, it takes several milliseconds for one scenario, and the time multiplies across the whole grid.
- STS: Due to the math being complex and non-linear, it takes around 9 milliseconds for one scenario on an Apple M5 processor, and the time multiplies across the whole grid.

**0.72**
- URTC camera-ready: The data is split 60\ \subsection{One-sided conformal band} The split-conformal prediction approach converts the residuals from the calibration dataset into a coverage guarantee (the number of cases the band is guaranteed to contain)\cite{lei2018,vovk2005}.
- STS: The data is split into 60\ \subsection{One-sided conformal band} The split-conformal prediction approach converts the residuals from the calibration dataset into a coverage guarantee (the probability that the true voltage is at or above the band's lower end)\cite{lei2018,vovk2005,angelopoulos2023}.

**0.66**
- URTC camera-ready: Split conformal prediction is correct on average but not necessarily on any one case.
- STS: This establishes the lower bound because, in split conformal prediction, I can be correct on average but not necessarily inside the band.

**0.65**
- URTC camera-ready: The gradient-boosted model is far more accurate than the linear one, and at 0.90 coverage it is also faster.
- STS: It can be said that the gradient-boosted model is much more accurate than the linear model, and has a 3.29 times speedup compared to 2.04 times.

**0.64**
- URTC camera-ready: By contrast, a machine learning model can predict the single minimum voltage in a fraction of a millisecond.
- STS: By contrast, a prediction from a machine learning model can take a fraction of a millisecond for predicting the single minimum voltage out of the whole grid.

**0.62**
- URTC camera-ready: Alc\'antara and Chatzivasileiadis \cite{alcantara2026} use an AI foundation model and conformal prediction to produce a binary risk flag for post-element outages.
- STS: Alc\'antara and Chatzivasileiadis \cite{alcantara2026} use an AI foundation model and conformal prediction to create a binary yes/no switch for post-element outages to determine whether there's a present risk or not.

**0.61**
- URTC camera-ready: The check itself comes from an AC power flow solve, run for each potential contingency, and for a network with hundreds of elements it becomes time-consuming.
- STS: Normally, the check itself comes from a physics calculation called an AC power flow solve, run for each potential contingency.

