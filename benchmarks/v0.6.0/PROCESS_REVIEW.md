# Benchmark process review and pipeline changes

**Release:** HardSub Extractor 0.6.0

**Historical evidence:** [v0.5.0 master analysis](../v0.5.0/MASTER_BENCHMARK_ANALYSIS.md) and [English 1/3/6 FPS experiment](../v0.5.0/experiments/english-sampling-rate/README.md)

This review separates defects in the benchmark process, pipeline behavior that can be changed without replacing OCR, and recognition limits that likely require a stronger language model. The v0.5.0 report is preserved as historical evidence; the v0.6.0 measurements are stored separately.

## Problems found in the earlier process

| Problem | Evidence from v0.5.0 | Why it matters | v0.6.0 change / treatment |
|---|---|---|---|
| Integer frame stride did not match the configured rate | The 1/3/6 FPS test used `floor(source_fps / target_fps)` on 15 FPS video. A 6 FPS target became 7.5 FPS; the old 6 FPS output duplicated the earlier Fast result. | Mode comparisons were mislabeled and sampling phase depended on source FPS. | Schedule samples against elapsed video time. Current Fast and Balanced target 1 and 3 FPS, capped by source FPS. |
| Synthetic set was narrow | 50 clips per language were variations of seven phrase patterns over one 320x240, 15 FPS moving source, with a controlled set of fonts, colors, outlines, and durations. The 2.05 GB videos are not in Git. | It measures repeatability on the authored sample, not performance on varied natural video, codec, resolution, scene, or subtitle design. | Versioned v0.6 report uses generated clear and stress fixtures and explicitly marks them diagnostic, not real-world accuracy evidence. Original dataset metadata and historical results remain intact. |
| Strict one-to-one matching conflated text reading with cue assembly | The master report records 15,835 Fast and 28,074 Balanced unmatched output entries across 6,900 reference cues per mode; all unmatched entries overlapped a labelled cue interval. | Text could be recognizable across fragments while the final SRT still had unusable entries. | Report cue recall, text-correct cues, exact text, extra entries, and timing separately. The updated v0.6 harness also records boundary errors. |
| Character error rate over-penalized fragments | The v0.5 English CER was 40.0% for Fast and 63.5% for Balanced, with fragments counted as inserted text. Chinese/Korean spacing and CJK strict matching also distorted literal comparisons. | One metric mixed OCR character quality with duplicate/fragment behavior; language-specific spacing was not handled consistently. | The app uses script-aware comparison only for stabilization and boundary checks. It does not normalize or rewrite final SRT text. Reports keep literal output and diagnostic normalization separate. |
| Frame-to-frame OCR variation fragmented a visible cue | Many unmatched entries overlapped real cue intervals; Korean captured the character sequence in many windows but only 105/300 Fast cues were exact and none of 50 clips was strict-clean. | Small recognition changes or whitespace shifts could split one subtitle into multiple SRT entries. | Group repeated readings by script-specific similarity, use confidence-weighted consensus, retain screen position, tolerate configured short blanks, and merge only short-gap near-duplicates at a similar position. |
| Boundary refinement required exact OCR equality | Balanced binary checks treated a character/spacing variation as a non-match even if it was the same subtitle. | The boundary search could move away from a real event due to one noisy recognition. | Boundary checks now use conservative language-aware similarity; CJK/Hangul stability ignores whitespace only. |
| OCR enhancement retry ran too often | The prior recognizer retried virtually every accepted read below 98% confidence. | Added inference work increased latency and could replace a good read with a slightly higher-confidence but worse variant. | Retry is limited to borderline confidence or plausible rejected candidates; a retry replaces the first reading only when confidence improves by more than 0.01. This is a performance heuristic, not a guaranteed accuracy gain. |
| GPU throughput was not verified end to end | v0.5 sessions listed CUDAExecutionProvider, but the logs also reported a missing CUDA plugin device and utilization was not sampled. v0.6 listed CUDA + CPU and a single live sample showed 3% GPU utilization / 3,315 MiB in use, while the plugin-device warning remained. | Provider labels and a single utilization sample do not establish per-inference GPU execution or dependable performance projections. | Keep provider and hardware details; do not present the short-run times as confirmed GPU throughput. Future runs should capture sustained utilization and provider-level profiling. |
| Aggregate claims hid weak languages | Fast achieved at least 95% exact cue text in only 8 of 23 languages. v0.5 reported exact matched cues of 40/300 Vietnamese, 51/300 Arabic, 60/300 Tamil, 174/300 Turkish, and 143/300 Hindi. | The long language menu implied more reliability than the evidence supported. | Removed Vietnamese, Arabic, Tamil, Turkish, and Hindi. The remaining 18 are still not certified at 95%; each still needs a representative real-video evaluation. |
| Version records could become mixed | The old benchmark folder described the 0.5.0 app and contained the original modes, while the later English FPS experiment used a new scan-rate setting. | Rewriting historical reports would make future app/version comparisons hard to audit. | Keep `benchmarks/v0.5.0/` and tag `v0.5.0` immutable; use a new `benchmarks/v0.6.0/` snapshot and tag. |

## v0.6.0 pipeline changes

1. **Two explicit scan rates:** Fast is 1 FPS; Balanced is 3 FPS and performs three rounds of targeted boundary refinement. A timeline scheduler selects frames instead of using an integer divisor. This corrects the old 6-to-7.5 FPS oversampling behavior, but it does not make 1 FPS suitable for short subtitles.
2. **Event stabilization:** collect distinct OCR results (cached repeats are not counted as independent votes), compare normalized readings with language/script-specific thresholds, and select a representative by recurrence and confidence. Latin/Cyrillic accents and diacritics remain significant. CJK/Hangul whitespace is ignored only for matching.
3. **Position-aware cleanup:** retain OCR bounding-box centers and merge near-duplicate entries only when they are text-similar, spatially close, and separated by a short gap. Fast tolerates 0.45 seconds of blank OCR; Balanced tolerates 0.28 seconds. The shorter Balanced gap was chosen after the v0.6 fixture sweep showed the old 0.52-second value merging two identical cues separated by a visible gap.
4. **Script-aware sensitivity:** lower visual skip thresholds for CJK/Hangul and modestly for Cyrillic so changed glyphs are less likely to be hidden by frame caching. The language recognizer itself remains PaddleOCR's language-specific model.
5. **Lower retry overhead:** run the contrast enhancement retry only for borderline reads and require a meaningful confidence improvement before using its result.
6. **Language menu scoped to evidence:** retain 18 requested options and remove the five weak language options above. Model capability is not inferred from the fact that a language code is accepted by PaddleOCR.

## v0.6.0 fixture result

The final source-matched run completed 36 synthetic cases in each mode (144 expected cues per mode). Fast captured 72/144 cues (50.0%), with 72 exact matched texts, 0 extras, 0.450s mean start error and 0.650s mean end error on matched cues; both boundaries were within 0.5s for 36/144 expected cues. Balanced captured 142/144 (98.6%), all 142 matched texts were exact, there were 0 extras, mean matched-cue start/end errors were 0.055/0.013s, and both boundaries were within 0.5s for 142/144 expected cues. Average extraction times were 0.495s and 1.549s per 3.6s fixture (model initialization excluded), respectively. Japanese was 6/8; the other 17 options were 8/8 in Balanced. Both modes fail the strict 95% per-language recall/text gate because Fast's cadence misses short cues and Japanese remains below 95% in Balanced.

The fixture set intentionally includes short cues and repeated text, which strongly penalizes 1 FPS. It is only eight cues per language and cannot represent general accuracy. The Balanced result is promising on this generated text, but not sufficient to claim a 95% real-video capture rate. See the [raw run data and figure](README.md#results). GPU was selected and CUDA/CPU providers were present; this does not mean these short-run times are verified GPU throughput.

## What these changes can and cannot solve

Pipeline work can reduce duplicate/fragment SRT cues, suppress small OCR flicker, avoid wasteful retries, make the configured sampling cadence honest, and improve boundary matching when spacing or a small number of glyphs vary.

Pipeline changes cannot recover a symbol absent from the recognizer's output vocabulary, guarantee high-quality readings for a poorly supported script, or compensate for subtitle cues shorter than the sample interval. Model-language gaps require a suitable recognizer/dictionary and review by fluent speakers. The removed five options should return only after language-specific tests show that the model can recognize the script and the full pipeline produces acceptable subtitle cues.

## Evaluation safeguards for later releases

- Do not use repeated synthetic phrases as a substitute for independent, annotated real videos.
- Report text capture and cue assembly separately: content characters, exact/normalized cue text, cue recall, extra/fragment entries, and start/end timing.
- Include different source resolutions/frame rates, scene backgrounds, subtitle sizes, outlines/colors, cue lengths, and multi-line cases.
- Match each expected cue to at most one output; publish the matcher and thresholds with the results.
- Record source hashes, app/source hash, model versions, settings, device, software environment, active providers, elapsed time, and run errors.
- Do not claim a 95% capture target without a sufficiently varied, held-out, annotated real-video set and language reviewer.
