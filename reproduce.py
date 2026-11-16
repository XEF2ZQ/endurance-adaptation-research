"""Regenerate deterministic numerical outputs using Python's standard library."""
import csv
import json
from pathlib import Path
from model import PROTOCOLS, kinetic_proxy, original_score, equal_work_retention

ROOT = Path(__file__).resolve().parent


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    timing = [{"protocol": p.name, "repetitions": p.repetitions,
               "work_min_each": p.work_min, "rest_min_each": p.rest_min,
               "work_total_min": p.work_total, "rest_total_min": p.rest_total,
               "main_set_min": p.elapsed, "density_pct": round(100 * p.density, 6),
               "with_15min_warmup_cooldown": p.elapsed + 15} for p in PROTOCOLS]
    write_csv(output / "protocols.csv", timing)
    kinetics = []
    for tau in (30, 60, 90):
        for p in PROTOCOLS:
            kinetics.append({"protocol": p.name, "assumed_tau_s": tau,
                             **{k: round(v, 9) for k, v in kinetic_proxy(p, tau).items()},
                             "status": "hypothetical acute proxy; not adaptation"})
    write_csv(output / "kinetic_sensitivity.csv", kinetics)
    original = [{"work_min": w, "rest_min": r, "unvalidated_score": round(original_score(w, r), 9)}
                for w in (3, 4, 6, 8) for r in (1.5, 2, 3, 4)]
    original.sort(key=lambda x: x["unvalidated_score"], reverse=True)
    write_csv(output / "original_score_audit.csv", original)
    summary = {"status": "arithmetic and hypothetical sensitivity analysis only",
               "original_grid_maximum": original[0],
               "quality_break_even_32_vs_30": equal_work_retention(32, 30),
               "quality_scenarios": [{"retained_quality_32min": q, "weighted_min_32min": 32 * q,
                                      "weighted_min_30min": 30} for q in (1.0, .95, .90)],
               "hormone_coefficients": None, "adaptation_prediction": None}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="590" viewBox="0 0 1000 590">',
             '<rect width="1000" height="590" fill="#f7f9fc"/>',
             '<g font-family="Arial,sans-serif" fill="#172d45">',
             '<text x="35" y="40" font-size="24" font-weight="bold">Equal minutes do not imply equal adaptation</text>',
             '<text x="35" y="68" font-size="15">Exact schedules: dark = work, pale = recovery. No final rest.</text>']
    for i, p in enumerate(PROTOCOLS):
        y, current = 105 + 49 * i, 230
        parts.append(f'<text x="35" y="{y+21}" font-size="16">{p.name}</text>')
        for rep in range(p.repetitions):
            width = p.work_min * 15
            parts.append(f'<rect x="{current}" y="{y}" width="{width}" height="28" rx="2" fill="#176b87"/>')
            current += width
            if rep < p.repetitions - 1:
                width = p.rest_min * 15
                parts.append(f'<rect x="{current}" y="{y}" width="{width}" height="28" fill="#c8d8e4"/>')
                current += width
        parts.append(f'<text x="850" y="{y+21}" font-size="15">{p.work_total:g} / {p.elapsed:g} min</text>')
    for minute in range(0, 41, 5):
        parts.append(f'<text x="{230+minute*15}" y="525" font-size="13">{minute}</text>')
    parts.extend(['<text x="230" y="550" font-size="14">Main-set elapsed minutes; warm-up and cool-down excluded</text>',
                  '<text x="850" y="550" font-size="13">Work / elapsed</text>', '</g></svg>'])
    (output / "protocol_timing.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
