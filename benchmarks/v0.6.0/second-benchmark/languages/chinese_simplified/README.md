# Chinese (Simplified) OCR benchmark

**App version under test:** `0.6.0` (release tag `v0.6.0`).
**Pipeline source SHA-256:** `8d9bb3010092d24a9df5cf1826427446997fb72e53f25735384086cabfc0a503`.
**Dataset source-video SHA-256:** `280cb385b84657c8cd83c30184a3b3f2c9b0c5e3bc2b46db5a799a50026c7070`.

## Scope and setup

50 Chinese (Simplified) clips × 2 modes = 100 successful extraction runs; 6 reference cues per clip (300 per mode). Source is a single 320×240, 15 FPS, 18.93-second video with synthetic burned-in subtitles. RTX 4070 12 GB; model detection and recognition sessions list CUDAExecutionProvider with CPU fallback. 80% minimum OCR confidence; subtitle-specific and centered filters enabled; bottom 35% region. White clips use the White filter; yellow/cyan clips use Any color. Model initialization is excluded from per-clip timings. The runner invokes the project’s Python OCR backend and extractor directly using its virtual environment; it does not automate the packaged EXE or UI. Model: PP-OCRv6; PaddleOCR 3.7.0, PaddleX 3.7.2 and ONNX Runtime GPU 1.30.0.
Dataset source clip: 320×240 at 15 FPS, 18.93 s.
Pipeline code SHA-256: `8d9bb3010092d24a9df5cf1826427446997fb72e53f25735384086cabfc0a503`. Model initialization is excluded from clip timings.

## Results

| Mode | Time matched | ≥95% similar | Exact text | Extra entries | CER | Mean per clip | Estimate per hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fast | 290/300 (96.7%) | 150/300 (50.0%) | 129/300 (43.0%) | 5 | 10.4% | 0.71 s | 2.2 min |
| Balanced | 300/300 (100.0%) | 146/300 (48.7%) | 122/300 (40.7%) | 5 | 7.9% | 2.94 s | 9.3 min |

| Mode | Strict exact clips, no extras | Punctuation-normalized exact clips, no extras | Median absolute start error | Median absolute end error | Both boundaries within 0.1 s | Both boundaries within 0.5 s | Exact text in cue time window |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fast | 1/50 | 36/50 | 0.667 s | 0.400 s | 0/300 (0.0%) | 0/300 (0.0%) | 132/300 |
| Balanced | 0/50 | 44/50 | 0.025 s | 0.017 s | 297/300 (99.0%) | 299/300 (99.7%) | 122/300 |

The clean clip count requires all six cues to be exact and no unmatched output entries. Timing errors omit unmatched cues. Exact text in cue time checks whether the exact label appeared in any output entry during that cue, even when the one-to-one matcher selected a different entry. Literal exact and similarity scores count every space and punctuation mark; the additional character-content comparison helps separate those formatting differences from letter or character recognition.

| Mode | Content characters exact in matched cue | Content characters exact somewhere in cue window | Full line after punctuation and spacing normalization |
|---|---:|---:|---:|
| Fast | 288/300 | 292/300 | 290/300 |
| Balanced | 299/300 | 299/300 | 296/300 |

Content characters preserve letters, numbers, and combining marks while ignoring punctuation and whitespace. The punctuation-normalized result equates common Chinese and ASCII punctuation and ellipsis forms; for Chinese/Japanese it also ignores spaces. These are diagnostic comparisons, not substitutes for strict text accuracy: punctuation can change meaning, and the app’s actual SRT still contains whatever it recognized.

For this sample, Fast yielded 292/300 content-exact cues, 290/300 punctuation-normalized full lines, 5 unmatched entries, and 0.71 s/clip; Balanced yielded 299/300 content-exact cues, 296/300 punctuation-normalized full lines, 5 unmatched entries, and 2.94 s/clip. Compare strict exact text, timing and extra-entry counts alongside normalized character measures; punctuation, spacing and extra-entry cleanup still affect the exported SRT.

## Examples requiring review

- ch_001, Fast, cue 1: expected "我们明天早上出发 2026"; output (no qualifying single-entry time match; fragments may exist).
- ch_006, Fast, cue 2: expected "你说的是19.95还是90.15？"; output (no qualifying single-entry time match; fragments may exist).
- ch_011, Fast, cue 3: expected "红色的门在左边。 111"; output (no qualifying single-entry time match; fragments may exist).
- ch_016, Fast, cue 4: expected "请等我一下"; output (no qualifying single-entry time match; fragments may exist).
- ch_021, Fast, cue 5: expected "等等……我们真的要走吗？"; output (no qualifying single-entry time match; fragments may exist).
- ch_026, Fast, cue 6: expected "我们明天晚上出发 2025"; output (no qualifying single-entry time match; fragments may exist).

![Results overview](overview.png)

![Style and duration](style_and_duration.png)

![Content character reading](content_char_accuracy.png)

![Processing time](processing_time.png)

## Interpretation and definitions

- A time match requires at least 30% of the reference cue duration to overlap one unique output entry; text can still be wrong. Matches maximize the number of time-matched cues first, then text similarity. One output can match only one reference cue.
- Text similarity is 1 − Levenshtein distance / max(reference length, output length), after Unicode NFC and whitespace normalization. Case and punctuation count. The ≥95% and exact rates use all 300 reference cues as denominator, so missed cues count against both.
- Extra entries are outputs left unmatched after one-to-one matching. An extra overlapping a reference cue may be a fragment or duplicate; an extra outside reference timings may be a false positive. These timing categories alone do not prove the cause.
- Median absolute start and end timing errors and the mean overlap fraction for matched cues are available in the summary CSV. These timing figures omit unmatched cues; exact text does not imply exact timing.
- Character error rate (CER) counts edits in matched text, all characters of unmatched reference cues as deletions, and all characters of unmatched output entries as insertions, divided by the number of reference characters. It can exceed 100%.
- Timing estimates scale the mean measured extraction-plus-matching time linearly to 3,600 seconds, excluding model initialization and export. Each clip was run once per selected mode (Fast, Balanced) with a shared loaded model. Actual one-hour videos can differ substantially with resolution, frame rate, subtitle density, codec, hardware, warm-up and other workload.
- Style comparisons are exploratory: font, size, color, outline, cue text and timing are not randomized independently. Sample sizes vary; see the breakdown CSV. The 50 clips reuse the same background and seven base phrases, so these results are not a representative estimate or guarantee of real-world performance.
- The local run folder contains all predicted SRTs for comparison with the dataset labels; those SRT files are excluded from the repository report. Per-cue CSVs retain the prediction used for scoring. No manual review of every OCR error was performed.

## Files

- `summary_by_mode.csv`: aggregate results, including min/median/max runtime and extra-entry breakdown.
- `per_run.csv`: timings, settings and counts for every clip and mode.
- `per_cue.csv`: expected text, matched output, similarity, timings and style for each reference cue.
- `extra_entries.csv`: every unmatched output with its time and text.
- `breakdown_by_style_and_duration.csv`: cue-level counts and rates by style, duration and mode.
- `content_char_accuracy.png`: style and duration breakdown for letters/numbers, excluding spaces and punctuation.
- The local run folder contains all predicted SRTs for comparison with the dataset labels; those SRT files are excluded from the repository report. Per-cue CSVs retain the prediction used for scoring.
- The SQLite database and run log are retained in the local benchmark results folder and excluded from Git; see the reproduction instructions for rerunning the benchmark.
