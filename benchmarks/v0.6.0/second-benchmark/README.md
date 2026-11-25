# HardSub Extractor v0.6.0 second benchmark

This is the final second-benchmark report tied to release tag `v0.6.0`. It covers 14 of the 18 retained OCR options; Ukrainian, Malay, Polish, and Swedish were not tested. The 14-language corpus uses the curated 50 clips per language with Fast (1 FPS) and Balanced (3 FPS): all 1,400 extraction runs completed successfully (700 per mode).

Balanced time-matched all 4,200 cues and placed both boundaries within 0.1 seconds for 98.2%; strict exact full-line text was 77.3%. Fast matched 96.7% of cues and was about 4.2× quicker, but matched only 1 of 140 sub-second cues. These synthetic results do not establish real-video accuracy or a universal 95% accuracy level.

- [Master analysis, final conclusions, and recommendations](MASTER_BENCHMARK_ANALYSIS.md)
- [Pooled statistics](summary_by_mode.csv)
- [Language comparison](per_language.csv)
- [Short versus regular cues](duration_breakdown.csv)
- [Detailed language reports](languages/)

Raw media, predicted SRTs, SQLite databases, and run logs remain local.
