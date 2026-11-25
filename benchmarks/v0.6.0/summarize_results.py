"""Create pooled CSV summaries and figures from the v0.6.0 benchmark JSON."""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
MODES = (("fast", "Fast (1 FPS)"), ("balanced", "Balanced (3 FPS)"))


def load_runs():
    return {label: json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8"))
            for name, label in MODES}


def aggregate(report):
    runs = report["results"]
    expected = sum(r.get("expected_cues", 0) for r in runs)
    detected = sum(r.get("detected_cues", 0) for r in runs)
    correct = sum(r.get("text_correct_cues", 0) for r in runs)
    exact = sum(r.get("exact_text_cues", 0) for r in runs)
    extras = sum(r.get("extra_cues", 0) for r in runs)
    starts = [r["mean_start_error_seconds"] * r["detected_cues"] for r in runs
              if r.get("detected_cues") and r.get("mean_start_error_seconds") is not None]
    ends = [r["mean_end_error_seconds"] * r["detected_cues"] for r in runs
            if r.get("detected_cues") and r.get("mean_end_error_seconds") is not None]
    matched_boundaries = sum(r.get("detected_cues", 0) for r in runs)
    within = sum(r.get("boundaries_within_0_5_seconds", 0) for r in runs)
    elapsed = [r.get("elapsed_seconds", 0.0) for r in runs]
    init = [r.get("model_initialization_seconds", 0.0) for r in runs]
    samples = [r.get("scan", {}).get("samples", 0) for r in runs]
    ocr_calls = [r.get("scan", {}).get("ocr_calls", 0) for r in runs]
    return {
        "mode": report["mode"], "target_fps": report["target_sample_fps"], "runs": len(runs),
        "expected_cues": expected, "detected_cues": detected,
        "cue_recall_pct": 100 * detected / max(1, expected),
        "text_correct_cues": correct, "text_correct_pct_of_expected": 100 * correct / max(1, expected),
        "exact_text_cues": exact, "exact_pct_of_expected": 100 * exact / max(1, expected),
        "extra_entries": extras, "cue_precision_pct": 100 * detected / max(1, detected + extras),
        "mean_start_error_seconds_matched_only": sum(starts) / max(1, matched_boundaries),
        "mean_end_error_seconds_matched_only": sum(ends) / max(1, matched_boundaries),
        "both_boundaries_within_0_5s": within,
        "both_boundaries_within_0_5s_pct_of_expected": 100 * within / max(1, expected),
        "mean_extraction_seconds_per_3_6s_fixture": statistics.mean(elapsed),
        "median_extraction_seconds_per_3_6s_fixture": statistics.median(elapsed),
        "mean_model_initialization_seconds_per_run": statistics.mean(init),
        "mean_sampled_frames_per_fixture": statistics.mean(samples),
        "mean_ocr_calls_per_fixture": statistics.mean(ocr_calls),
        "mean_speedup_to_hour_estimate": "not reported for short synthetic clips",
    }


def main():
    reports = load_runs()
    summaries = {mode: aggregate(report) for mode, report in reports.items()}
    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(next(iter(summaries.values()))))
        writer.writeheader()
        writer.writerows(summaries.values())

    languages = list(reports["Fast (1 FPS)"]["results"])
    names = list(dict.fromkeys(row["language"] for row in languages))
    language_rows = []
    for name in names:
        row = {"language": name}
        for mode, report in reports.items():
            cases = [r for r in report["results"] if r["language"] == name]
            prefix = "fast" if mode.startswith("Fast") else "balanced"
            expected = sum(r.get("expected_cues", 0) for r in cases)
            detected = sum(r.get("detected_cues", 0) for r in cases)
            row.update({f"{prefix}_detected": detected, f"{prefix}_expected": expected,
                        f"{prefix}_recall_pct": round(100 * detected / max(1, expected), 2),
                        f"{prefix}_exact_text": sum(r.get("exact_text_cues", 0) for r in cases),
                        f"{prefix}_extras": sum(r.get("extra_cues", 0) for r in cases),
                        f"{prefix}_mean_seconds_per_fixture": round(statistics.mean(r.get("elapsed_seconds", 0) for r in cases), 3)})
        language_rows.append(row)
    with (RESULTS / "per_language.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(language_rows[0]))
        writer.writeheader()
        writer.writerows(language_rows)

    labels = ["Fast (1 FPS)", "Balanced (3 FPS)"]
    colors = ["#3979da", "#2d9b80"]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.3), constrained_layout=True)
    metric_fields = ["cue_recall_pct", "both_boundaries_within_0_5s_pct_of_expected", "mean_extraction_seconds_per_3_6s_fixture"]
    titles = ["Cue recall", "Both boundaries within 0.5 s", "Extraction time per 3.6 s fixture"]
    units = ["% of expected cues", "% of expected cues", "seconds (excluding model load)"]
    for ax, field, title, unit in zip(axes, metric_fields, titles, units):
        vals = [summaries[label][field] for label in labels]
        bars = ax.bar(labels, vals, color=colors, width=.58)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_ylabel(unit, fontsize=9)
        ax.grid(axis="y", alpha=.22)
        ax.set_axisbelow(True)
        for bar, value in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{value:.1f}" + ("%" if "%" in unit else "s"),
                    ha="center", va="bottom", fontsize=9)
        ax.tick_params(axis="x", labelrotation=12, labelsize=8)
    fig.suptitle("HardSub Extractor v0.6.0 - generated stress fixtures (18 OCR options)", fontsize=13, weight="bold")
    fig.savefig(RESULTS / "mode_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 7.2), constrained_layout=False)
    fig.subplots_adjust(left=.27, right=.96, top=.84, bottom=.10)
    y = list(range(len(language_rows)))
    fast_bars = ax.barh([v + .18 for v in y], [r["fast_recall_pct"] for r in language_rows], height=.34, color=colors[0], label=labels[0])
    balanced_bars = ax.barh([v - .18 for v in y], [r["balanced_recall_pct"] for r in language_rows], height=.34, color=colors[1], label=labels[1])
    for bars in (fast_bars, balanced_bars):
        for bar in bars:
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{bar.get_width():.0f}%",
                    va="center", ha="left", fontsize=7.5)
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Cue recall (% of 8 expected cues per language)")
    fig.suptitle("Cue recall by OCR language - generated fixture set", fontsize=12, weight="bold", y=.98)
    ax.grid(axis="x", alpha=.22)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.03), ncol=2, frameon=False)
    fig.savefig(RESULTS / "language_recall.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps({"summary": summaries, "languages": language_rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
