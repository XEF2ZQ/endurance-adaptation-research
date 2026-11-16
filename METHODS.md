# Methods, provenance and computational contract

## Literature scope

Search date: 16 November 2026. Targeted searches were performed using public web indexing, prioritizing PubMed, PubMed Central, original journal pages and Endocrine Society guidance. Query families were testosterone dose response; testosterone aerobic performance; testosterone hepcidin erythropoietin; estradiol male physiology and assay; human exercise GLUT4; critical power versus FTP; threshold interval duration; oxygen uptake kinetics; glycogen resynthesis; and prospective anabolic-steroid cardiac effects.

This was a narrative evidence audit. There was no exhaustive database search, independent duplicate screening, preregistration, pooled estimate or GRADE assessment. Titles, identifiers, populations and available endpoints were checked. `references.json` records access level and source URLs; `evidence.csv` records applicability. The phrase 'not identified' means these searches and sources do not supply an applicable estimate, not that no relevant publication could exist.

## Input provenance and privacy

The starting prose was a supplied text containing an incomplete endocrine-performance discussion. A matching analysis open in the browser exposed its Python score, which was reconstructed mathematically for auditing. The source text is not a scientific reference. Its conversation, browser URL, personal identifiers and any purported personal laboratory results are not included. Hormonal concentrations and training constraints are generalized hypothetical scenarios.

## Exact quantities

- Main-set time: n*w + (n-1)*r, minutes.
- Work time: n*w, minutes.
- Work density: work time / main-set time.
- Whole-session examples add 15 minutes for warm-up and cool-down. This is an accounting assumption, not a physiological constant.
- Testosterone conversion: ng/dL * 0.03467 = nmol/L, rounded for display.
- Original score: the expression in article section 5, reconstructed without NumPy.
- Original search grid: work [3,4,6,8] minutes; rest [1.5,2,3,4] minutes; intensity fixed at 0.88.
- Original grid maximum: 8 / 4 minutes; arbitrary score 4.482283383.
- Quality break-even: 30/32 = 0.9375. This is arithmetic for an assumed work-weighted proxy.

## Hypothetical kinetic model

`q` is dimensionless and is not measured oxygen uptake or a percentage of a physiological threshold. Within each work or recovery segment:

`dq/dt = (target - q)/tau`

`q_end = target + (q_start-target)*exp(-duration/tau)`

`integral = target*duration + (q_start-target)*tau*(1-exp(-duration/tau))`

The illustrative initial/recovery value is 0.35 and work target is 0.88. A single shared time constant is varied over 30, 60 and 90 seconds. These are scenario values, not estimates, priors or confidence limits. State persists between bouts. Only work integrals are accumulated; recovery consumes session time and changes the state but contributes no area to the reported work-only metric. Internal integration uses seconds; output integral units are arbitrary response-minutes. No numerical time step is used in production calculations.

The model excludes delay, slow component, drift, exercise economy changes, local fatigue, impact load, hormonal actions, glycogen and adaptation. An exponential primary response is physiologically motivated, but this use is uncalibrated and cannot establish an interval prescription. `None` is recorded for hormonal coefficients and adaptation prediction to prevent confusing absence of estimates with numerical zero effects.

## Validation

Unit tests check independent timing examples, absence of a final rest, continuous/split equivalence at zero recovery, equilibrium and zero-duration boundaries, analytic area against independent midpoint integration, rejection of invalid inputs, the original score's grid maximum, and break-even ranking reversal. Successful tests establish computational consistency only. They are not physiological validation.

`python reproduce.py` recreates all files in `results/`. No personal data or network access is required. `python build_article.py` generates the article PDF from Markdown and renders its pages for visual review; that optional step requires PyMuPDF.

## Research integrity

No effect size has been assigned to 2,000 versus 2,500 versus 3,000 ng/dL testosterone. No p-values, participant data, confidence intervals or adaptation gains were simulated and presented as observed. Source-reported results and original arithmetic retain separate labels. A future model requires a prespecified outcome, measured predictors, longitudinal data and independent evaluation.
