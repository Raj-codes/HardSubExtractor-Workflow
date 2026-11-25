# Chinese (Simplified) OCR benchmark

**App version under test:** `0.5.0` (release tag `v0.5.0`).

## Scope and setup

50 Chinese (Simplified) clips × 3 modes = 150 successful extraction runs; six reference cues per clip (300 per mode). Source is a single 320×240, 15 FPS, 18.93-second video with synthetic burned-in subtitles. RTX 4070 12 GB; model detection and recognition sessions list CUDAExecutionProvider with CPU fallback. 80% minimum OCR confidence; subtitle-specific and centered filters enabled; bottom 35% region. White clips use the White filter; yellow/cyan clips use Any color. Model initialization is excluded from per-clip timings. The runner invokes the project’s Python OCR backend and extractor directly using its virtual environment; it does not automate the packaged EXE or UI. Model: PP-OCRv6; PaddleOCR 3.7.0, PaddleX 3.7.2 and ONNX Runtime GPU 1.30.0. Source file SHA-256: 521bdee29db5c6fb316170948697f9a952b443b01397beacf8259e020d15385f.

## Results

| Mode | Time matched | ≥95% similar | Exact text | Extra entries | CER | Mean per clip | Estimate per hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fast | 299/300 (99.7%) | 153/300 (51.0%) | 131/300 (43.7%) | 138 | 59.4% | 4.50 s | 14.3 min |
| Balanced | 296/300 (98.7%) | 151/300 (50.3%) | 131/300 (43.7%) | 224 | 92.3% | 8.20 s | 26.0 min |
| Accurate | 296/300 (98.7%) | 151/300 (50.3%) | 131/300 (43.7%) | 224 | 92.3% | 10.17 s | 32.2 min |

| Mode | Strict exact clips, no extras | Punctuation-normalized exact clips, no extras | Median absolute start error | Median absolute end error | Both boundaries within 0.1 s | Exact text in cue time window |
|---|---:|---:|---:|---:|---:|---:|
| Fast | 0/50 | 24/50 | 0.000 s | 0.067 s | 256/300 (85.3%) | 150/300 |
| Balanced | 0/50 | 22/50 | 0.000 s | 0.000 s | 252/300 (84.0%) | 154/300 |
| Accurate | 0/50 | 22/50 | 0.033 s | 0.033 s | 252/300 (84.0%) | 154/300 |

The clean clip count requires all six cues to be exact and no unmatched output entries. Timing errors omit unmatched cues. Exact text in cue time checks whether the exact label appeared in any output entry during that cue, even when the one-to-one matcher selected a different entry. Literal exact and similarity scores count every space and punctuation mark; the additional character-content comparison helps separate those formatting differences from letter or character recognition.

| Mode | Content characters exact in matched cue | Content characters exact somewhere in cue window | Text exact with common punctuation and CJK spacing normalized |
|---|---:|---:|---:|
| Fast | 299/300 | 300/300 | 295/300 |
| Balanced | 296/300 | 300/300 | 295/300 |
| Accurate | 296/300 | 300/300 | 295/300 |

Content characters preserve letters, numbers, and combining marks while ignoring punctuation and whitespace. The punctuation-normalized result equates common Chinese and ASCII punctuation and ellipsis forms; for Chinese/Japanese it also ignores spaces. These are diagnostic comparisons, not substitutes for strict text accuracy: punctuation can change meaning, and the app’s actual SRT still contains whatever it recognized.

For this sample, the content characters and numbers appeared exactly in an overlapping output entry for 300/300 cues in every mode; the punctuation-normalized whole-string match was 295/300 in Fast and 295/300 in each of Balanced and Accurate. This is a useful diagnostic alongside the strict exact score, while punctuation, spacing, and extra-entry cleanup still affect the exported SRT.

## Examples requiring review

- ch_019, Balanced, cue 3: expected "请等我一下 119"; output (no qualifying single-entry time match; fragments may exist).
- ch_019, Accurate, cue 3: expected "请等我一下 119"; output (no qualifying single-entry time match; fragments may exist).
- ch_020, Balanced, cue 3: expected "等等……我们真的要走吗？ 120"; output (no qualifying single-entry time match; fragments may exist).
- ch_020, Accurate, cue 3: expected "等等……我们真的要走吗？ 120"; output (no qualifying single-entry time match; fragments may exist).
- ch_031, Balanced, cue 3: expected "你说的是19.95还是90.15？ 131"; output (no qualifying single-entry time match; fragments may exist).
- ch_031, Accurate, cue 3: expected "你说的是19.95还是90.15？ 131"; output (no qualifying single-entry time match; fragments may exist).

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
- Timing estimates scale the mean measured extraction-plus-matching time linearly to 3,600 seconds, excluding model initialization and export. Each clip was run once per mode in fixed Fast, Balanced, Accurate order with a shared loaded model. Actual one-hour videos can differ substantially with resolution, frame rate, subtitle density, codec, hardware, warm-up and other workload.
- Style comparisons are exploratory: font, size, color, outline, cue text and timing are not randomized independently. Sample sizes vary; see the breakdown CSV. The 50 clips reuse the same background and seven base phrases, so these results are not a representative estimate or guarantee of real-world performance.
- Predicted SRT files preserve every extracted entry and can be compared with the matching dataset SRT. Timing is rounded to milliseconds for export. No manual review of all OCR errors was performed.

## Files

- `summary_by_mode.csv`: aggregate results, including min/median/max runtime and extra-entry breakdown.
- `per_run.csv`: timings, settings and counts for every clip and mode.
- `per_cue.csv`: expected text, matched output, similarity, timings and style for each reference cue.
- `extra_entries.csv`: every unmatched output with its time and text.
- `breakdown_by_style_and_duration.csv`: cue-level counts and rates by style, duration and mode.
- `content_char_accuracy.png`: style and duration breakdown for letters/numbers, excluding spaces and punctuation.
- [Predicted SRT files for all runs](../audit/predicted-srt.zip).
- [Underlying structured run data](../results.sqlite3) and [sanitized benchmark logs](../audit/run-logs.zip).
