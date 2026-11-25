# English scan-rate benchmark

## Scope and setup

Tested 2026-11-16. 50 English clips × 3 scan settings = 150 successful extraction runs; 6 reference cues per clip (300 per setting). Source is a single 320×240, 15 FPS, 18.93-second video with synthetic burned-in subtitles. The GPU is an RTX 4070 with 12 GB VRAM; model detection and recognition sessions list CUDAExecutionProvider with CPU fallback. Startup also logged that no CUDA plugin EP device was found for device 0, and GPU utilization was not measured; treat these as GPU-configured timing estimates, not confirmed GPU throughput. 80% minimum OCR confidence; subtitle-specific and centered filters enabled; bottom 35% region. White clips use the White filter; yellow/cyan clips use Any color. Model initialization is excluded from per-clip timings. All settings are copied from the app’s Fast configuration except the sample_fps value. The frame selector uses an integer step of floor(video FPS / target FPS), so targets can produce different realized rates. The runner invokes the project’s Python OCR backend and extractor directly using its virtual environment; it does not automate the packaged EXE or UI. Model: PP-OCRv6; PaddleOCR 3.7.0, PaddleX 3.7.2 and ONNX Runtime GPU 1.30.0. Source file SHA-256: 521bdee29db5c6fb316170948697f9a952b443b01397beacf8259e020d15385f.

## Results

| Scan setting | Mean samples / clip | Realized FPS | Time matched | ≥95% similar | Exact text | Extra entries | CER | Mean per clip | Estimate per hour |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 FPS (Ultra Fast) | 19 | 1.00 | 290/300 (96.7%) | 290/300 (96.7%) | 279/300 (93.0%) | 12 | 7.2% | 0.71 s | 2.3 min |
| 3 FPS (Faster) | 57 | 3.01 | 300/300 (100.0%) | 300/300 (100.0%) | 294/300 (98.0%) | 33 | 13.2% | 1.84 s | 5.8 min |
| 6 FPS (Fast) | 142 | 7.50 | 299/300 (99.7%) | 299/300 (99.7%) | 293/300 (97.7%) | 99 | 40.0% | 4.17 s | 13.2 min |

| Mode | Strict exact clips, no extras | Punctuation-normalized exact clips, no extras | Median absolute start error | Median absolute end error | Both boundaries within 0.1 s | Both boundaries within 0.5 s | Exact text in cue time window |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 FPS (Ultra Fast) | 28/50 | 29/50 | 0.667 s | 0.400 s | 0/300 (0.0%) | 0/300 (0.0%) | 287/300 |
| 3 FPS (Faster) | 34/50 | 34/50 | 0.200 s | 0.133 s | 36/300 (12.0%) | 285/300 (95.0%) | 295/300 |
| 6 FPS (Fast) | 24/50 | 24/50 | 0.000 s | 0.067 s | 267/300 (89.0%) | 270/300 (90.0%) | 296/300 |

The clean clip count requires all six cues to be exact and no unmatched output entries. Timing errors omit unmatched cues. Exact text in cue time checks whether the exact label appeared in any output entry during that cue, even when the one-to-one matcher selected a different entry. Literal exact and similarity scores count every space and punctuation mark; the additional character-content comparison helps separate those formatting differences from letter or character recognition.

| Mode | Content characters exact in matched cue | Content characters exact somewhere in cue window | Full line after punctuation and spacing normalization |
|---|---:|---:|---:|
| 1 FPS (Ultra Fast) | 288/300 | 293/300 | 288/300 |
| 3 FPS (Faster) | 300/300 | 300/300 | 295/300 |
| 6 FPS (Fast) | 299/300 | 300/300 | 296/300 |

Content characters preserve letters, numbers, and combining marks while ignoring punctuation and whitespace. The punctuation-normalized result equates common Chinese and ASCII punctuation and ellipsis forms; for Chinese/Japanese it also ignores spaces. These are diagnostic comparisons, not substitutes for strict text accuracy: punctuation can change meaning, and the app’s actual SRT still contains whatever it recognized.

For this sample, 1 FPS (Ultra Fast) yielded 293/300 content-exact cues, 288/300 punctuation-normalized full lines, 12 unmatched entries, and 0.71 s/clip; 3 FPS (Faster) yielded 300/300 content-exact cues, 295/300 punctuation-normalized full lines, 33 unmatched entries, and 1.84 s/clip; 6 FPS (Fast) yielded 300/300 content-exact cues, 296/300 punctuation-normalized full lines, 99 unmatched entries, and 4.17 s/clip. Compare strict exact text, timing and extra-entry counts alongside normalized character measures; punctuation, spacing and extra-entry cleanup still affect the exported SRT.

## Examples requiring review

- en_001, 1 FPS (Ultra Fast), cue 1: expected "We will leave tomorrow 2026"; output (no qualifying single-entry time match; fragments may exist).
- en_006, 1 FPS (Ultra Fast), cue 2: expected "Did you say 19.95 or 90.15?"; output (no qualifying single-entry time match; fragments may exist).
- en_011, 1 FPS (Ultra Fast), cue 3: expected "The red door is on the left. 111"; output (no qualifying single-entry time match; fragments may exist).
- en_016, 1 FPS (Ultra Fast), cue 4: expected "Wait for me"; output (no qualifying single-entry time match; fragments may exist).
- en_021, 1 FPS (Ultra Fast), cue 5: expected "Wait... are we really going?"; output (no qualifying single-entry time match; fragments may exist).
- en_026, 1 FPS (Ultra Fast), cue 6: expected "We will leave tonight 2025"; output (no qualifying single-entry time match; fragments may exist).

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
- Timing estimates scale the mean measured extraction-plus-matching time linearly to 3,600 seconds, excluding model initialization and export. Each clip was run once per selected mode (1 FPS (Ultra Fast), 3 FPS (Faster), 6 FPS (Fast)) with a shared loaded model. Actual one-hour videos can differ substantially with resolution, frame rate, subtitle density, codec, hardware, warm-up and other workload.
- Style comparisons are exploratory: font, size, color, outline, cue text and timing are not randomized independently. Sample sizes vary; see the breakdown CSV. The 50 clips reuse the same background and seven base phrases, so these results are not a representative estimate or guarantee of real-world performance.
- Predicted SRT files preserve every extracted entry and can be compared with the matching dataset SRT. Timing is rounded to milliseconds for export. No manual review of all OCR errors was performed.

## Files

- `summary_by_mode.csv`: aggregate results, including min/median/max runtime and extra-entry breakdown.
- `per_run.csv`: timings, settings and counts for every clip and mode.
- `per_cue.csv`: expected text, matched output, similarity, timings and style for each reference cue.
- `extra_entries.csv`: every unmatched output with its time and text.
- `breakdown_by_style_and_duration.csv`: cue-level counts and rates by style, duration and mode.
- `content_char_accuracy.png`: style and duration breakdown for letters/numbers, excluding spaces and punctuation.
- `predicted-srt/`: all 150 extracted subtitle files.
- `../results.sqlite3` and the scan-rate experiment configuration: underlying run data and process log.
