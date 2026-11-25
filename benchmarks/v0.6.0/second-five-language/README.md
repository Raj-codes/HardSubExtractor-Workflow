# v0.6.0 second benchmark: five-language corpus run

This follow-up processes the curated 50-clip corpus for English, German, Italian, Spanish, and French using v0.6.0 Fast (1 FPS) and Balanced (3 FPS). It completed 500 extraction runs with no run failures. The media, predicted SRTs, SQLite database, and logs are excluded from this repository; reports preserve per-run/per-cue output and scoring.

- [Master analysis, findings, and recommendations](MASTER_BENCHMARK_ANALYSIS.md)
- [Expanded fourteen-language second-benchmark master](../second-benchmark/MASTER_BENCHMARK_ANALYSIS.md) — all fourteen languages are now included in the expanded master.
- [Pooled mode statistics](summary_by_mode.csv)
- [Per-language statistics](per_language.csv)
- [Short versus regular cue results](duration_breakdown.csv)
- [Same-corpus v0.5 comparison](v0.5_to_v0.6_comparison.csv)
- [Dataset identity check](dataset_hash_check.csv)
- [Per-language detailed reports](languages/)
- [Run environment and settings](run_metadata.json)

Fast missed all 50 sub-second cues in this corpus and Balanced captured all 50. Balanced matched all 1,500 cues overall, reached 98.7% near-exact text and 92.8% strict exact text, and had both boundaries within 0.1 seconds for all expected cues. These are results on controlled synthetic fixtures, not real-world accuracy guarantees.
