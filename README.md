# Androgens, estradiol and subthreshold endurance adaptation

An evidence-audited research article and reproducible computational companion for jump-rope and HYROX-oriented aerobic training.

**Version 1.0 | 16 November 2026 | Critical narrative review and methods paper**

Read the [complete article](manuscript.md) or the [typeset PDF](output/pdf/endurance_adaptation_review.pdf).

Serum testosterone and estradiol alone cannot identify an optimal work interval, rest duration, training intensity, or expected aerobic improvement. Established androgen effects on muscle and erythropoiesis do not supply the missing endurance dose-response function. Estradiol of 30 pg/mL does not, by itself, establish estrogen deficiency or impaired muscle glucose transport.

## Contents

| File | Purpose |
| --- | --- |
| [manuscript.md](manuscript.md) | Complete article, numbered references and study proposal |
| [CLAIM_AUDIT.md](CLAIM_AUDIT.md) | Corrections to the starting analysis |
| [METHODS.md](METHODS.md) | Search scope, equations and validation |
| [references.json](references.json) | Machine-readable source register |
| [evidence.csv](evidence.csv) | Study design, population and applicability |
| [model.py](model.py) | Scheduling, hypothetical kinetics and original-score audit |
| [reproduce.py](reproduce.py) | Regenerate CSV and SVG outputs |
| [results](results) | Exact arithmetic and illustrative kinetic calculations |
| [tests/test_model.py](tests/test_model.py) | Arithmetic, boundary and numerical-integration checks |
| [build_article.py](build_article.py) | Rebuild the PDF with PyMuPDF |

## Reproduction

Python 3.10 or later; numerical calculations use only the standard library.

```bash
python reproduce.py
python -m unittest discover -s tests -v
```

For the PDF, install `requirements-pdf.txt`, then run `python build_article.py`.

The scripts do not ingest personal health data, estimate hormone doses, or predict adaptation. The original score is reproduced only to demonstrate its structural defects.

Prepared for Peter Kosanyi, with literature synthesis, writing and computational auditing assisted by OpenAI Codex. No academic affiliation, clinical credentials, peer review, original human experiment, or independent replication is claimed. Scenarios are hypothetical; the originating conversation and personal medical information are excluded.

This is an educational research synthesis. Training examples are evaluation candidates, not validated individualized prescriptions. Hormonal manipulation is outside scope. No third-party full-text papers are redistributed. No open-source or content license is granted by this repository.
