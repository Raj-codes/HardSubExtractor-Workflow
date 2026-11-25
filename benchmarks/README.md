# Historical benchmark archive

I kept the earlier controlled runs here because they show how sampling and OCR cleanup behaved on the same generated fixtures. They were run against earlier versions of the extraction pipeline, not this standalone command-line script.

- [v0.5.0 benchmark baseline](v0.5.0/README.md) — 23 language choices and per-cue results.
- [English 1/3/6 FPS experiment](v0.5.0/experiments/english-sampling-rate/README.md) — a separate sampling-rate comparison.
- [v0.6.0 process review](v0.6.0/README.md) — changes made to the benchmark method and pipeline.
- [English, German, Italian, Spanish and French report](v0.6.0/second-five-language/MASTER_BENCHMARK_ANALYSIS.md).
- [Expanded 14-language report](v0.6.0/second-benchmark/MASTER_BENCHMARK_ANALYSIS.md).

These runs used short synthetic subtitle clips, so they are useful for controlled comparisons, not a promise of real-video accuracy. The v0.5 and v0.6 pipeline versions changed sampling cadence and cleanup together; that comparison does not isolate one change. The original benchmark videos are not included. Several manifests, plots and cue-level tables are kept for reference.
