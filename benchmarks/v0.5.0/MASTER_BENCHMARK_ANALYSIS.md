# HardSub Extractor benchmark master analysis

This is the consolidated analysis for the HardSub Extractor **0.5.0** benchmark. Preserve this report as the v0.5.0 record; future app versions should receive a new versioned benchmark directory. The dataset and method are documented in [the dataset guide](dataset/README.md); each language report contains per-cue data, SRT outputs and charts.

## Current evidence

The dataset contains 50 clips for each of 23 OCR language options. Each clip has six labelled subtitle cues, for 300 cues per language. The clips use one 320×240, 15 FPS source video and a small set of repeated phrase patterns with changes in punctuation and numbers. OCR confidence was 80%; subtitle-specific and centered filters were enabled; inference was configured for GPU on the RTX 4070; the model sessions reported CUDAExecutionProvider with CPU fallback. Startup also emitted an ONNX Runtime warning that no CUDA plugin EP device was found for device 0; GPU utilization was not measured, so speed and one-hour estimates are provisional. The benchmark calls the Python OCR backend and extraction engine directly; it does not automate the packaged app or test its interface. All 23 languages are complete (2,500 extraction runs): English, German, Simplified Chinese, and Japanese retain their original three-mode historical results; Korean, Arabic, Tamil, Russian, French, Spanish, Italian, Portuguese, Dutch, Traditional Chinese, Tagalog (the app’s Filipino option), Vietnamese, Ukrainian, Hindi, Indonesian, Malay, Turkish, Polish and Swedish were tested in Fast and Balanced only. The first four languages retain historical Accurate results; the other 19 were compared in Fast and Balanced. Accurate is not part of the completed two-mode comparisons.

English is the first completed language: 150 successful runs, 50 clips in each mode.

| Mode | Time-matched cues | Exact matched text | Unmatched output entries | Clips with all 6 exact and no extras | Both boundaries within 0.1 s | Mean clip time | Linear estimate for 1 hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fast | 299/300 (99.7%) | 293/300 (97.7%) | 99 | 24/50 | 267/300 (89.0%) | 4.29 s | 13.6 min |
| Balanced | 299/300 (99.7%) | 291/300 (97.0%) | 159 | 18/50 | 255/300 (85.0%) | 7.86 s | 24.9 min |
| Accurate | 299/300 (99.7%) | 291/300 (97.0%) | 159 | 18/50 | 255/300 (85.0%) | 9.35 s | 29.6 min |

Fast led this sample on speed, exact matches, and output cleanliness. Balanced and Accurate had equal aggregate cue and text counts here. Their boundary estimates differed slightly; mode names alone did not predict improved results on this benchmark.

The 99, 159 and 159 unmatched entries all overlapped reference subtitle time windows. Many were short fragments: 75 Fast extras and 132 extras in each other mode lasted under 0.5 seconds. A repeated word or punctuation/spacing change across frames can split a single expected cue into several entries. For example, cue 3 of `en_043` was represented by several short OCR entries, including exact text, but no one entry overlapped enough of its duration to satisfy the benchmark's 30% matching rule. This is why the time-match rate alone overstates usable SRT quality.

The exact text was found somewhere in an overlapping output entry for 296 of 300 expected English cues. The one-to-one benchmark matcher scores 293, 291 and 291 exact matched cues because it also accounts for time overlap and can match each output only once. These are different measures and should not be conflated.

Among matched cues, median absolute start and end errors were at most 0.067 seconds for Fast, 0 seconds for Balanced and 0.033 seconds for Accurate. The tails were worse: some matched boundaries were more than 0.5 seconds off, often when matching a fragment. Timing statistics exclude unmatched cues. Requiring both boundaries within 0.1 seconds lowers the rates to 89%, 85% and 85%, respectively.

The character error rate is 40.0% for Fast and 63.5% for Balanced and Accurate. It counts every unmatched output fragment as inserted characters, so it reflects fragmentation as well as recognition mistakes. Read it alongside exact cue text, extra entries, and timing rather than as a stand-alone character recognition measure.

### Supplemental English scan-rate experiment

The separate [scan-rate report](experiments/english-sampling-rate/README.md) reruns the same 50 English clips (300 labelled cues) at 1, 3, and 6 FPS targets, changing only the `sample_fps` value from the Fast configuration. It is an additional controlled experiment; it does not replace or rewrite the historical Fast/Balanced/Accurate results above. The source is 15 FPS, and the extractor uses `floor(source_fps / target_fps)` as its integer frame step. As a result, the nominal 6 FPS setting actually sampled at about 7.5 FPS.

| Target (label) | Measured scan rate | Mean samples / clip | Time-matched cues | Exact matched text | Unmatched entries | Median absolute start / end error | Both boundaries within 0.1 s | Mean time / clip | Estimated hour |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 FPS (Ultra Fast) | 1.00 FPS | 19 | 290/300 (96.7%) | 279/300 (93.0%) | 12 | 0.667 / 0.400 s | 0/300 | 0.71 s | 2.3 min |
| 3 FPS (Faster) | 3.01 FPS | 57 | 300/300 (100%) | 294/300 (98.0%) | 33 | 0.200 / 0.133 s | 36/300 (12.0%) | 1.84 s | 5.8 min |
| 6 FPS (Fast) | 7.50 FPS | 142 | 299/300 (99.7%) | 293/300 (97.7%) | 99 | 0.000 / 0.067 s | 267/300 (89.0%) | 4.17 s | 13.2 min |

On this synthetic set, 3 FPS was the strongest overall tradeoff: all cues were time-matched, it had the most exact text matches and the most fully exact clips with no extras (34/50), and it ran about 2.3 times faster than the current 6 FPS target. Six FPS produced the best median timing and 89% of cues had both boundaries within 0.1 seconds, but its 99 unmatched entries were three times the 3 FPS count. One FPS was about 2.6 times faster than 3 FPS, but missed 10 cues and had much coarser timing. The 6 FPS predictions and cue matches were identical to the original English Fast run, confirming that this is a scan-rate comparison of the current Fast behavior.

The 40.0% CER at 6 FPS is inflated by fragmented/unmatched entries being counted as inserted characters; it should not be read as a 40% error rate on matched subtitle text. GPU inference was configured and CUDAExecutionProvider appeared in both model sessions, but startup logged that no CUDA plugin EP device was found and GPU utilization was not sampled. Treat the timing estimates as provisional; these short, low-resolution synthetic clips also do not establish performance on real videos.

German is now complete: another 150 successful runs. The exact expected text appeared in an overlapping output entry for 299/300 cues in every mode. Exact matched entries were 296 for Fast and 295 for Balanced and Accurate. Fast took 4.35 seconds per clip and produced 113 unmatched entries; Balanced took 7.75 seconds with 203 extras; Accurate took 9.46 seconds with 203 extras. Every unmatched output entry overlapped a reference cue, again pointing mainly to fragmentation during subtitles rather than detections between cues. Only 18/50 Fast clips and 13/50 clips in each other mode had all six cues exact with no extra entries. Both boundaries were within 0.1 seconds for 85.3% of Fast cues and 80.7% in the other modes.

The English and German results agree on the current priorities: Fast gives the best time and fewer fragments for these samples, while mode changes do little to eliminate fragmentation. The findings are still from the same synthetic video, so do not yet establish a broadly best mode across languages and real footage. See the [German results](results/german/README.md) for per-cue examples and the full tables.

### French findings

The [French report](results/french/README.md) contains the 100 Fast and Balanced runs, extracted SRTs, cue-level comparisons, CSV data and figures. The benchmark used PP-OCRv6 configured for GPU on the RTX 4070; detector and recognizer sessions listed CUDAExecutionProvider with CPU fallback. It used 80% confidence, centered subtitle filtering and the bottom 35% region. Startup logs also contain an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. Actual GPU utilization was not sampled, so treat the timing and one-hour estimates as provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 299/300 (99.7%) | 295/300 (98.3%) | 266/300 (88.7%) | 300/300 | 271/300 (90.3%) | 126 | 10/50 | 257/300 (85.7%) | 265/300 (88.3%) | 4.83 s | 15.3 min |
| Balanced | 298/300 (99.3%) | 291/300 (97.0%) | 264/300 (88.0%) | 300/300 | 270/300 (90.0%) | 225 | 4/50 | 240/300 (80.0%) | 254/300 (84.7%) | 8.76 s | 27.7 min |

**Text capture:** all French letters and numbers appeared during every expected cue for both modes. That content-only check ignores spaces and punctuation. The more demanding punctuation-normalized full-line check reached 90.3% for Fast and 90.0% for Balanced, while literal exact matched text was 88.7% and 88.0%. Thus French character recognition is strong on this synthetic set, but complete cue wording and formatting are not yet at 95%.

**Timing and SRT cleanliness:** Fast time-matched 299 cues and Balanced 298, but only 10 Fast clips and 4 Balanced clips contained all six exact cues without extra entries. Every unmatched output overlapped a labelled subtitle interval (126 Fast, 225 Balanced), consistent with fragments or repeated readings rather than detections between subtitles. Both boundaries were within 0.1 seconds for 85.7% of Fast cues and 80.0% of Balanced cues; at 0.5 seconds the rates were 88.3% and 84.7%. Median boundary errors look small, but omit unmatched cues and therefore do not describe all expected subtitles.

**Conclusion:** Fast is the more practical setting in this test: similar text capture, 99 fewer extra entries, 3.93 seconds less per clip and somewhat better timing. French character reading is promising, but the finished SRT output does not meet a 95% clean-cue standard. Prioritize temporal consolidation and punctuation stability, then confirm on varied French footage with a fluent reviewer. The shared low-resolution synthetic source limits any real-world accuracy claim.

### Spanish findings

The [Spanish report](results/spanish/README.md) contains the 100 Fast and Balanced runs, per-cue comparisons, extracted SRTs, data and figures. The run used PP-OCRv6 configured for GPU; sessions listed CUDAExecutionProvider with CPU fallback. Startup also emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. GPU utilization was not sampled, so treat timing estimates as provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100%) | 297/300 (99.0%) | 256/300 (85.3%) | 300/300 | 256/300 (85.3%) | 131 | 3/50 | 251/300 (83.7%) | 263/300 (87.7%) | 4.49 s | 14.2 min |
| Balanced | 300/300 (100%) | 299/300 (99.7%) | 257/300 (85.7%) | 300/300 | 257/300 (85.7%) | 217 | 2/50 | 239/300 (79.7%) | 255/300 (85.0%) | 8.01 s | 25.4 min |

**Text capture versus usable subtitles:** all Spanish letters and numbers appeared somewhere during every expected cue for both modes, but that character-only measure ignores spaces and punctuation. Only 85.3% Fast and 85.7% Balanced cues had a complete punctuation-normalized line in the cue window, and exact matched text was at those same rates. Every cue passed the time-overlap rule, so the gap comes from the output text chosen for each cue rather than failure to detect the interval alone.

**Timing and SRT cleanliness:** both boundaries were within 0.1 seconds for 83.7% of Fast and 79.7% of Balanced cues. Every unmatched output entry overlapped a labelled subtitle interval (131 Fast, 217 Balanced), suggesting fragments or repeated readings during subtitles. Only 3/50 Fast and 2/50 Balanced clips contained all six exact cues with no extras. Balanced gained one exact cue and two ≥95%-similar cues but added 86 extra entries, nearly doubled runtime, and had weaker timing.

**Conclusion:** Fast is more practical here, but neither mode produces reliably clean Spanish SRTs: normalized complete-line accuracy is about 85% and clean clips are rare. The model appears to see the characters, while punctuation, line assembly and repeated readings reduce final output quality. Improve temporal consolidation and validate on varied Spanish footage before making accuracy claims.

### Italian findings

The [Italian report](results/italian/README.md) includes the same 100-run analysis, cue data, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback. Startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0; actual GPU utilization was not sampled, so runtime and one-hour estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 297/300 (99.0%) | 296/300 (98.7%) | 292/300 (97.3%) | 300/300 | 298/300 (99.3%) | 213 | 12/50 | 224/300 (74.7%) | 246/300 (82.0%) | 4.52 s | 14.3 min |
| Balanced | 294/300 (98.0%) | 293/300 (97.7%) | 289/300 (96.3%) | 300/300 | 298/300 (99.3%) | 357 | 6/50 | 206/300 (68.7%) | 237/300 (79.0%) | 8.30 s | 26.3 min |

**Text capture:** all Italian content letters and numbers appeared somewhere during every cue, and punctuation-normalized full lines appeared in 298/300 cue windows in both modes. Exact matched text was also high (97.3% Fast, 96.3% Balanced). This is a strong full-line result, slightly below German’s normalized score, but it does not mean the exported SRTs are clean.

**Timing and SRT cleanliness:** only 12 Fast and 6 Balanced clips had all six exact cues with no extras. All 213 Fast and 357 Balanced unmatched entries overlapped labelled cue intervals, consistent with fragmentation or repeated readings. Both timing boundaries met 0.1 seconds for 74.7% Fast and 68.7% Balanced cues. Fast had three more time-matched cues, three more exact matched cues, 144 fewer extras and about half the runtime.

**Conclusion:** Italian text recognition is strong on this controlled set, but subtitle timing and fragmented SRT events still need improvement. Fast is the clear practical choice. Prioritize stabilization and cue consolidation, then confirm with natural Italian footage and fluent review.

### Dutch findings

The [Dutch report](results/dutch/README.md) contains 100 Fast and Balanced runs, extracted SRTs, cue-level comparisons, CSVs and figures. It used PP-OCRv6 configured for GPU; sessions listed CUDAExecutionProvider with CPU fallback. Startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. GPU utilization was not sampled, so timing figures are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100%) | 300/300 (100%) | 294/300 (98.0%) | 300/300 | 296/300 (98.7%) | 79 | 23/50 | 269/300 (89.7%) | 276/300 (92.0%) | 4.06 s | 12.9 min |
| Balanced | 299/300 (99.7%) | 299/300 (99.7%) | 294/300 (98.0%) | 300/300 | 297/300 (99.0%) | 144 | 21/50 | 259/300 (86.3%) | 269/300 (89.7%) | 7.46 s | 23.6 min |

**Text capture:** all Dutch letters and numbers appeared during every expected cue in both modes. Fast had 294 exact matched cues and 296 punctuation-normalized full lines in cue windows; Balanced had 294 and 297 respectively. This is strong recognition on the controlled sample.

**Timing and SRT cleanliness:** both boundaries were within 0.1 seconds for 89.7% Fast and 86.3% Balanced cues. All extra entries overlapped labelled subtitle intervals (79 Fast, 144 Balanced), suggesting fragments or repeated readings during subtitle display. Strictly clean clips numbered 23 Fast and 21 Balanced. Balanced gained one normalized full line, but Fast had fewer extras, better timing and nearly half the processing time. Fast is the more practical choice; verify on varied Dutch footage.

### Portuguese findings

The [Portuguese report](results/portuguese/README.md) includes all 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs, CSV data and figures. It used PP-OCRv6 configured for GPU; detector and recognizer sessions listed CUDAExecutionProvider with CPU fallback. Startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. GPU utilization was not sampled, so runtime and one-hour estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100%) | 299/300 (99.7%) | 296/300 (98.7%) | 300/300 | 298/300 (99.3%) | 97 | 22/50 | 263/300 (87.7%) | 276/300 (92.0%) | 4.76 s | 15.1 min |
| Balanced | 298/300 (99.3%) | 298/300 (99.3%) | 295/300 (98.3%) | 300/300 | 299/300 (99.7%) | 212 | 16/50 | 247/300 (82.3%) | 266/300 (88.7%) | 8.65 s | 27.4 min |

**Text capture:** all Portuguese letters and numbers appeared during every expected cue in both modes. Fast produced 296 exact matched cues and 298 punctuation-normalized full lines in cue windows; Balanced produced 295 and 299 respectively. This is strong controlled-set text recognition, although the normalized full-line comparison is a diagnostic and does not replace review of the exported wording and punctuation.

**Timing and SRT cleanliness:** both boundaries were within 0.1 seconds for 87.7% of Fast cues and 82.3% of Balanced cues. Every extra entry overlapped a labelled subtitle interval (97 Fast, 212 Balanced), indicating fragments or repeated readings within subtitle display rather than detections between labelled cues. Only 22 Fast and 16 Balanced clips were fully exact with no extras. Balanced gained one normalized full line in a cue window but yielded fewer exact matched cues, 115 more extras, six fewer clean clips and nearly twice the runtime. Fast is the practical choice for Portuguese in this sample; event consolidation remains the main product issue.

### Tagalog (Filipino option) findings

The app labels this OCR option **Filipino**; this benchmark uses Tagalog text from the `tl` dataset. See the [Tagalog/Filipino report](results/filipino/README.md) for 100 Fast and Balanced runs, per-cue comparisons, extracted SRTs, CSVs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback. Startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0; GPU utilization was not sampled, so runtime figures are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 299/300 (99.7%) | 299/300 (99.7%) | 285/300 (95.0%) | 300/300 | 294/300 (98.0%) | 144 | 16/50 | 252/300 (84.0%) | 263/300 (87.7%) | 4.50 s | 14.2 min |
| Balanced | 299/300 (99.7%) | 299/300 (99.7%) | 284/300 (94.7%) | 300/300 | 295/300 (98.3%) | 239 | 12/50 | 236/300 (78.7%) | 257/300 (85.7%) | 8.17 s | 25.9 min |

**Text and timing:** Fast matched 299 cues and had 95.0% exact matched text. The punctuation-normalized whole line appeared in 294/300 cue windows; all Tagalog letters and numbers appeared in at least one output during all 300 expected cue windows. Both boundaries were within 0.1 seconds for 84.0% of Fast cues and 78.7% of Balanced cues.

**SRT quality:** there were 144 Fast and 239 Balanced extra entries, all overlapping labelled subtitle intervals. Only 16 Fast clips and 12 Balanced clips had six exact cues and no extras. Balanced gained one normalized full line but had one fewer exact matched cue, 95 more extras and almost twice the runtime. Fast is the practical choice. Tagalog recognition is promising on this controlled set, but extra cue cleanup and timing still matter; confirm on natural footage with fluent review.

### Vietnamese findings — Experimental

The [Vietnamese report](results/vietnamese/README.md) contains all 100 runs, outputs, per-cue comparisons and figures. Vietnamese remains **Experimental**. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. GPU utilization was not sampled, so runtime estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 259/300 (86.3%) | 120/300 (40.0%) | 40/300 (13.3%) | 43/300 (14.3%) | 43/300 (14.3%) | 916 | 0/50 | 124/300 (41.3%) | 149/300 (49.7%) | 7.15 s | 22.7 min |
| Balanced | 244/300 (81.3%) | 117/300 (39.0%) | 39/300 (13.0%) | 43/300 (14.3%) | 43/300 (14.3%) | 1,574 | 0/50 | 110/300 (36.7%) | 135/300 (45.0%) | 13.49 s | 42.8 min |

**Reading accuracy and usability are both poor.** Fast produced 40 exact matched cues and Balanced 39. Only 43/300 complete content-character sequences and normalized full lines appeared in any overlapping cue window. This is substantially worse than the Latin-script languages and confirms the known difficulty with Vietnamese tone-marked text. Neither mode produced any fully exact, no-extra clip.

**Timing and fragmentation:** 916 Fast and 1,574 Balanced unmatched entries all overlapped labelled cue intervals, consistent with severe fragmentation or repeated readings during subtitle display. Both boundaries met the 0.1-second tolerance for only 41.3% Fast and 36.7% Balanced cues. Fast was better, with 15 more time-matched cues, one more exact cue, 658 fewer extras and nearly half the runtime, but it still is not usable as a reliable Vietnamese subtitle extractor. Preserve Experimental status; a better Vietnamese recognizer and Vietnamese-speaker evaluation are needed before promotion.

### Ukrainian findings

The [Ukrainian report](results/ukrainian/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv5 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 216/300 (72.0%) | 209/300 (69.7%) | 170/300 (56.7%) | 294/300 | 282/300 (94.0%) | 1,417 | 0/50 | 70/300 (23.3%) | 7.23 s | 22.9 min |
| Balanced | 188/300 (62.7%) | 182/300 (60.7%) | 161/300 (53.7%) | 294/300 | 287/300 (95.7%) | 2,473 | 0/50 | 53/300 (17.7%) | 14.14 s | 44.8 min |

**Interpretation:** the exact sequence of letters and numbers appeared somewhere during 294/300 cues in each mode, and punctuation-normalized full lines appeared in 282 Fast and 287 Balanced cue windows. Yet one-to-one cue matching was much lower, there were 1,417/2,473 unmatched output entries, and no clip was clean under the strict all-cues/no-extras test. The extras all overlapped labelled subtitle intervals, which is consistent with repeated or fragmented readings but does not by itself prove the cause. Fast was more practical than Balanced, but neither produced dependable Ukrainian SRTs in this benchmark.

**Timing:** both cue boundaries were within 0.1 seconds for only 23.3% Fast and 17.7% Balanced of the expected cues. Median absolute start/end errors among matched cues were 0.067/0.067 seconds Fast and 0.000/0.067 seconds Balanced; these omit unmatched cues. Text showing up somewhere in a cue window does not establish usable text-to-time alignment.

### Hindi findings

The [Hindi report](results/hindi/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv5 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 189/300 (63.0%) | 167/300 (55.7%) | 143/300 (47.7%) | 248/300 (82.7%) | 227/300 (75.7%) | 1,909 | 0/50 | 43/300 (14.3%) | 6.98 s | 22.1 min |
| Balanced | 157/300 (52.3%) | 140/300 (46.7%) | 123/300 (41.0%) | 251/300 (83.7%) | 230/300 (76.7%) | 3,395 | 0/50 | 35/300 (11.7%) | 13.28 s | 42.1 min |

**Interpretation:** Fast outperformed Balanced on time-matched cues, near-exact and exact matched text, unmatched-entry count and runtime. Both modes found some complete content strings during many cue windows, but this optimistic “somewhere in the window” diagnostic did not translate into dependable SRT events: no clip was exact and free of extras, and every unmatched entry overlapped a labelled cue interval. The very high CER (652% Fast; 1,139% Balanced) reflects the severe combination of missed/incorrect text and surplus OCR entries under the benchmark’s CER definition; it is not a character-level accuracy percentage.

**Timing:** both boundaries were within 0.1 seconds on 14.3% Fast and 11.7% Balanced of expected cues. Median absolute boundary errors were 0.067/0.200 seconds Fast and 0.000/0.267 seconds Balanced, calculated only for matched cues. Hindi needs substantial recognition and event-consolidation work before these results would support a reliable extraction claim.

### Indonesian findings

The [Indonesian report](results/indonesian/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100.0%) | 300/300 (100.0%) | 296/300 (98.7%) | 300/300 | 298/300 (99.3%) | 121 | 25/50 | 260/300 (86.7%) | 4.15 s | 13.1 min |
| Balanced | 298/300 (99.3%) | 298/300 (99.3%) | 293/300 (97.7%) | 300/300 | 299/300 (99.7%) | 215 | 18/50 | 249/300 (83.0%) | 7.47 s | 23.7 min |

**Interpretation:** Indonesian was strong on this controlled sample: all content characters appeared somewhere within every cue window, and 296 Fast / 293 Balanced cues had exact matched text. Full lines after punctuation normalization occurred in 298/300 and 299/300 cue windows. Fast also had fewer extra entries (121 vs 215), more strictly clean clips (25/50 vs 18/50), and about 1.8× the throughput. This is the strongest of these three languages, but the remaining extras and half of Fast clips failing the strict no-extra test mean it still needs review and validation on varied natural footage.

**Timing:** both boundaries were within 0.1 seconds for 86.7% Fast and 83.0% Balanced expected cues. Median absolute boundary errors among matches were 0.000/0.067 seconds Fast and 0.000/0.000 seconds Balanced. The controlled result supports a promising Indonesian reading, not a general accuracy guarantee.

### Malay findings

The [Malay report](results/malay/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100.0%) | 300/300 (100.0%) | 296/300 (98.7%) | 300/300 | 297/300 (99.0%) | 95 | 23/50 | 261/300 (87.0%) | 4.09 s | 13.0 min |
| Balanced | 298/300 (99.3%) | 298/300 (99.3%) | 293/300 (97.7%) | 300/300 | 297/300 (99.0%) | 166 | 17/50 | 248/300 (82.7%) | 7.33 s | 23.2 min |

**Interpretation:** Malay performed strongly on this controlled sample. Fast matched all 300 cues in time and exactly matched 296; punctuation-normalized full lines appeared in 297 cue windows. Balanced was close on text, but produced more extra entries and ran slower. The extras all overlapped expected subtitle intervals, consistent with fragmentation or repeated readings; 23/50 Fast clips were strictly exact with no extras. Validate on varied natural Malay footage before generalizing this result.

**Timing:** both boundaries were within 0.1 seconds for 87.0% Fast and 82.7% Balanced of expected cues. Median absolute start/end errors among matched cues were 0.000/0.067 seconds Fast and 0.000/0.000 seconds Balanced. These values exclude unmatched cues.

### Turkish findings

The [Turkish report](results/turkish/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 251/300 (83.7%) | 188/300 (62.7%) | 174/300 (58.0%) | 217/300 (72.3%) | 217/300 (72.3%) | 982 | 0/50 | 119/300 (39.7%) | 6.40 s | 20.3 min |
| Balanced | 227/300 (75.7%) | 173/300 (57.7%) | 167/300 (55.7%) | 223/300 (74.3%) | 222/300 (74.0%) | 1,711 | 0/50 | 107/300 (35.7%) | 12.08 s | 38.3 min |

**Interpretation:** Turkish is a weak result on this controlled sample. Fast exactly matched 174/300 cues and Balanced 167/300; neither mode produced a strictly clean clip. The 982 Fast and 1,711 Balanced extras all overlapped expected cue intervals, suggesting the output is fragmented or repeated rather than cleanly assembled. Balanced’s modest gains in text appearing somewhere do not offset its lower cue matching, more extras and longer runtime. Review Turkish recognition and cue consolidation with a fluent reader.

**Timing:** both boundaries were within 0.1 seconds for 39.7% Fast and 35.7% Balanced of expected cues. Median absolute start/end errors among matched cues were 0.067/0.067 seconds Fast and 0.000/0.000 seconds Balanced; unmatched cues are excluded from these error summaries.

### Polish findings

The [Polish report](results/polish/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 271/300 (90.3%) | 254/300 (84.7%) | 233/300 (77.7%) | 273/300 (91.0%) | 273/300 (91.0%) | 730 | 1/50 | 142/300 (47.3%) | 5.57 s | 17.6 min |
| Balanced | 251/300 (83.7%) | 234/300 (78.0%) | 219/300 (73.0%) | 273/300 (91.0%) | 273/300 (91.0%) | 1,336 | 0/50 | 127/300 (42.3%) | 10.34 s | 32.8 min |

**Interpretation:** Polish content appeared somewhere during 273/300 expected cue windows, but only 233 Fast cues were exact one-to-one matches and the output contained 730 unmatched entries. Balanced had fewer exact matches and 1,336 extras. Only one Fast clip was strictly clean; none were clean in Balanced. The gap between “text somewhere” and a clean timed cue indicates that Polish recognition and temporal consolidation both need work. Validate Polish orthography and diacritics with a fluent reviewer.

**Timing:** both boundaries were within 0.1 seconds for 47.3% Fast and 42.3% Balanced of expected cues. Median absolute boundary errors among matched cues were 0.067/0.067 seconds Fast and 0.000/0.000 seconds Balanced; these exclude unmatched cues.

### Swedish findings

The [Swedish report](results/swedish/README.md) contains 100 Fast and Balanced runs, cue-level comparisons, extracted SRTs and figures. The PP-OCRv6 sessions listed CUDAExecutionProvider with CPU fallback; startup emitted a warning that no CUDA plugin EP device was found for device 0. GPU utilization was not sampled, so throughput estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Content characters somewhere in cue window | Normalized full lines in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 281/300 (93.7%) | 270/300 (90.0%) | 259/300 (86.3%) | 282/300 (94.0%) | 281/300 (93.7%) | 447 | 11/50 | 209/300 (69.7%) | 4.73 s | 15.0 min |
| Balanced | 273/300 (91.0%) | 265/300 (88.3%) | 257/300 (85.7%) | 282/300 (94.0%) | 281/300 (93.7%) | 748 | 8/50 | 188/300 (62.7%) | 8.71 s | 27.6 min |

**Interpretation:** Swedish is a relatively strong result in this set, with 259/300 Fast exact matches and 281/300 punctuation-normalized full lines. However, only 11/50 Fast clips had all six exact cues with no extras, so export cleanliness remains a meaningful gap. Fast outperformed Balanced on cue matching, exact text, extra-entry count, clean clips, timing and speed. Confirm with varied natural Swedish video.

**Timing:** both boundaries were within 0.1 seconds for 69.7% Fast and 62.7% Balanced of expected cues. Median absolute start/end errors among matched cues were 0.000/0.067 seconds Fast and 0.000/0.000 seconds Balanced.

### Cross-language checkpoint: Fast mode




| Language | ≥95% matched text | Exact matched text | Exact/normalized full line in cue window | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | Estimated 1 hour |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| English | 299/300 | 293/300 | 296/300 | 99 | 24/50 | 267/300 (89.0%) | 4.29 s | 13.6 min |
| German | 297/300 | 296/300 | 299/300 | 113 | 18/50 | 256/300 (85.3%) | 4.35 s | 13.8 min |
| Chinese (Simplified) | 153/300* | 131/300* | 150/300* | 138 | 0/50* | 256/300 (85.3%) | 4.50 s | 14.3 min |
| Japanese | 194/300* | 147/300* | 148/300* | 37 | 0/50* | 287/300 (95.7%) | 4.59 s | 14.6 min |
| Korean | 117/300 | 105/300 | 201/300 | 1,889 | 0/50 | 19/300 (6.3%) | 7.16 s | 22.7 min |
| Arabic | 85/300 | 51/300 | 101/300 | 2,333 | 0/50 | 17/300 (5.7%) | 9.25 s | 29.3 min |
| Tamil | 90/300 | 60/300 | 170/300 | 2,888 | 0/50 | 9/300 (3.0%) | 7.46 s | 23.6 min |
| French | 299/300 | 266/300 | 271/300 | 126 | 10/50 | 257/300 (85.7%) | 4.83 s | 15.3 min |
| Spanish | 300/300 | 256/300 | 256/300 | 131 | 3/50 | 251/300 (83.7%) | 4.49 s | 14.2 min |
| Italian | 297/300 | 292/300 | 298/300 | 213 | 12/50 | 224/300 (74.7%) | 4.52 s | 14.3 min |
| Portuguese | 300/300 | 296/300 | 298/300 | 97 | 22/50 | 263/300 (87.7%) | 4.76 s | 15.1 min |
| Dutch | 300/300 | 294/300 | 296/300 | 79 | 23/50 | 269/300 (89.7%) | 4.06 s | 12.9 min |
| Chinese (Traditional) | 127/300* | 104/300* | 233/300* | 23 | 0/50* | 291/300 (97.0%) | 4.33 s | 13.7 min |
| Tagalog (Filipino) | 299/300 | 285/300 | 294/300 | 144 | 16/50 | 252/300 (84.0%) | 4.50 s | 14.2 min |
| Vietnamese (Experimental) | 120/300 | 40/300 | 43/300 | 916 | 0/50 | 124/300 (41.3%) | 7.15 s | 22.7 min |
| Russian | 254/300 | 210/300 | 280/300 | 908 | 0/50 | 114/300 (38.0%) | 7.15 s | 22.7 min |
| Hindi | 167/300 | 143/300 | 227/300 | 1,909 | 0/50 | 43/300 (14.3%) | 6.98 s | 22.1 min |
| Indonesian | 300/300 | 296/300 | 298/300 | 121 | 25/50 | 260/300 (86.7%) | 4.15 s | 13.1 min |
| Ukrainian | 209/300 | 170/300 | 282/300 | 1,417 | 0/50 | 70/300 (23.3%) | 7.23 s | 22.9 min |
| Malay | 300/300 | 296/300 | 297/300 | 95 | 23/50 | 261/300 (87.0%) | 4.09 s | 13.0 min |
| Turkish | 188/300 | 174/300 | 217/300 | 982 | 0/50 | 119/300 (39.7%) | 6.40 s | 20.3 min |
| Polish | 254/300 | 233/300 | 273/300 | 730 | 1/50 | 142/300 (47.3%) | 5.57 s | 17.6 min |
| Swedish | 270/300 | 259/300 | 281/300 | 447 | 11/50 | 209/300 (69.7%) | 4.73 s | 15.0 min |

In the first four languages, Fast was quickest and had fewer extras; Balanced and Accurate were generally similar, with Japanese showing only a small punctuation-normalized full-line gain at substantially higher runtime and more extras. Korean, Arabic and Tamil are clear quality outliers: Fast outperformed Balanced on time-matched cue capture and output cleanliness in all three, but both modes produced severe fragmentation and poor subtitle timing. Russian is stronger: Fast produced more time-matched cues and fewer extras than Balanced, with exact content characters present somewhere in an overlapping output for all 300 cues, though timing tails and fragmentation remain. French shows high character capture but still has fragmentation and punctuation issues. Italian has near-complete normalized lines in cue windows but many extra fragments. Spanish matches every cue in time but substantially fewer complete lines are exact. Tagalog is comparatively strong, with 98.0% normalized full lines on Fast, though fragmentation remains. Portuguese and Dutch are also strong: Fast reached 98.7% exact matched text in Portuguese and 98.0% in Dutch, with fewer fragments than Balanced. Traditional Chinese preserved every Han-character and number sequence in this controlled sample, but punctuation/spacing reduced exact complete lines; timing was strong. Vietnamese performs very poorly in both modes and remains Experimental. Fast is more practical than Balanced in each of these languages on this sample. The asterisk-marked literal Chinese and Japanese scores count punctuation and all spaces exactly, so they do not measure CJK character reading fairly on their own. Their supplemental results below use script-aware text checks. Ukrainian and Hindi join the poor-output group, with low cue recovery, many overlapping extra entries and weak timing; Indonesian and Malay performed strongly on this controlled set, though extra entries remain. Turkish performed poorly, with low exact-text capture and substantial fragmentation. Polish is intermediate but heavily fragmented; Swedish is stronger, though its clean-clip rate remains limited. Fast outperformed Balanced in aggregate for these additions. No mode is proven best across real footage.

### Simplified Chinese findings

The complete [Chinese report](results/chinese_simplified/README.md) includes all extracted SRTs, per-cue comparisons and an extra figure measuring content-character reading by style and cue duration.

| Mode | Literal exact matched text | Han/letter/number content exact in matched entry | Content exact somewhere in cue window | Punctuation-normalized exact somewhere | Extra entries | Punctuation-normalized clean clips | Mean clip time |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fast | 131/300 (43.7%) | 299/300 (99.7%) | 300/300 | 295/300 (98.3%) | 138 | 24/50 | 4.50 s |
| Balanced | 131/300 (43.7%) | 296/300 (98.7%) | 300/300 | 295/300 (98.3%) | 224 | 22/50 | 8.20 s |
| Accurate | 131/300 (43.7%) | 296/300 (98.7%) | 300/300 | 295/300 (98.3%) | 224 | 22/50 | 10.17 s |

**Interpretation:** the low literal exact (43.7%) and ≥95% similarity (~50%) rates were heavily affected by spacing and punctuation. In 300/300 cues per mode, the exact sequence of Chinese content characters and numbers appeared in at least one output entry during the cue. Once common Chinese/ASCII punctuation variants and optional CJK spaces are normalized, the complete line matches in 295/300 cues in every mode. This suggests the model read the Chinese characters and digits well in this controlled sample, but its punctuation choices and the shape of the final SRT remain imperfect. This does not establish comparable performance on natural Chinese video: all clips share a background and seven base phrases.

Fragmentation remains the product issue. All 138 Fast and 224 Balanced/Accurate unmatched entries overlapped subtitle time windows; 115 and 201 respectively lasted under 0.5 seconds. No clip met the strict all six exact/no extras definition, but after CJK punctuation and spacing normalization 24 Fast clips and 22 clips in the other modes had all six text cues and no extras. This shows how literal metrics can understate Chinese content accuracy, while extra entries still require cleanup. Both cue boundaries were within 0.1 seconds for 85.3% of Fast cues and 84.0% for the other modes.

Fast again had the fewest extras and shortest time; Balanced and Accurate had identical aggregate text and extra-entry counts, with Accurate taking longer. No mode materially improved Chinese character reading. The next Chinese work should focus on stabilizing OCR output across frames and evaluating punctuation faithfully, with native-reader review of the labels and results. Do not strip punctuation from exported subtitles merely to improve a benchmark score.

### Traditional Chinese findings

The [Traditional Chinese report](results/chinese_traditional/README.md) contains all 100 runs, extracted SRTs, per-cue comparisons, CSV data and figures. It used PP-OCRv6 configured for GPU; sessions listed CUDAExecutionProvider with CPU fallback. Startup emitted an ONNX Runtime warning that no plugin EP device was found for CUDA device 0. GPU utilization was not sampled, so runtime estimates are provisional.

| Mode | Time-matched cues | ≥95% similar | Exact matched text | Han/letter/number content exact in matched cue | Content exact in cue window | Punctuation-normalized full lines | Extra entries | Fully exact, no-extra clips | Both boundaries within 0.1 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 300/300 (100%) | 127/300 (42.3%) | 104/300 (34.7%) | 300/300 | 300/300 | 233/300 (77.7%) | 23 | 0/50 | 291/300 (97.0%) | 4.33 s | 13.7 min |
| Balanced | 300/300 (100%) | 125/300 (41.7%) | 102/300 (34.0%) | 300/300 | 300/300 | 230/300 (76.7%) | 39 | 0/50 | 290/300 (96.7%) | 7.98 s | 25.3 min |

**Character reading versus full-line exactness:** after ignoring whitespace and punctuation, the exact Han-character and number sequence appeared for every cue in both modes. Full lines after punctuation/spacing normalization matched 233/300 Fast and 230/300 Balanced cues; literal exact matched text was 104 and 102 cues. Examples show many errors are missing spaces before numbers or changed/omitted punctuation. This distinction matters: the result supports strong character reading on this synthetic sample, but not 100% correct subtitle formatting or fully accurate exported SRTs.

**Timing and SRT cleanliness:** both boundaries were within 0.1 seconds for 97.0% Fast and 96.7% Balanced cues; at 0.5 seconds the rates were 98.3% and 98.0%. Extra entries were relatively few (23 Fast, 39 Balanced), all overlapping labelled cue windows. No clip was strictly exact with no extras; after punctuation normalization, only 3/50 clips were clean in either mode. Fast was faster, had three more normalized full lines and fewer extras. For this sample, character detection and timing are strong; punctuation and spacing stability are the main gaps. The shared low-resolution synthetic source does not establish general Traditional Chinese performance.

### Japanese findings

The full [Japanese report](results/japanese/README.md) includes the per-cue results, extracted SRTs, and figures.

| Mode | Literal exact matched text | Content characters exact in matched entry | Content exact somewhere in cue window | Punctuation-normalized full lines somewhere | Extras | Punctuation-normalized clean clips | Both boundaries within 0.1 s | Mean clip time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 147/300 (49.0%) | 300/300 | 300/300 | 293/300 (97.7%) | 37 | 34/50 | 287/300 (95.7%) | 4.59 s |
| Balanced | 148/300 (49.3%) | 299/300 | 300/300 | 295/300 (98.3%) | 65 | 34/50 | 284/300 (94.7%) | 8.15 s |
| Accurate | 148/300 (49.3%) | 299/300 | 300/300 | 295/300 (98.3%) | 65 | 34/50 | 286/300 (95.3%) | 9.46 s |

Japanese content characters and numbers appeared in the output during every cue in this controlled set. Strict exact text is low because it counts every space and punctuation form literally; after language-aware punctuation normalization, 293–295 complete lines match. Japanese had fewer extras than the other tested languages, and timing was strongest so far: both boundaries were within 0.5 seconds for 96.3–96.7% of cues. Still, only 34/50 clips in each mode yielded six normalized exact cues without extra entries. Balanced/Accurate gained just two normalized line matches over Fast while adding 28 unmatched entries and increasing mean clip time from 4.59 to 8.15/9.46 seconds. Fast is the more practical choice on this sample unless the small normalized text difference is confirmed on varied footage.

### Korean findings

The full [Korean report](results/korean/README.md) includes cue-level comparisons, all extracted SRTs, CSV data and figures. Both model sessions used `CUDAExecutionProvider`; the Korean pipeline loaded as PP-OCRv5. The result is poor for producing usable Korean subtitles, even though Hangul content often appears somewhere in the raw output.

| Mode | Time-matched cues | Exact matched text | Punctuation-normalized full line in cue window | Content characters somewhere in cue window* | Unmatched entries | Clean clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 190/300 (63.3%) | 105/300 (35.0%) | 201/300 (67.0%) | 294/300 (98.0%) | 1,889 | 0/50 | 19/300 (6.3%) | 42/300 (14.0%) | 7.16 s | 22.7 min |
| Balanced | 148/300 (49.3%) | 89/300 (29.7%) | 213/300 (71.0%) | 295/300 (98.3%) | 3,282 | 0/50 | 13/300 (4.3%) | 32/300 (10.7%) | 13.76 s | 43.6 min |

**Text capture versus usable cues:** ignoring spaces and punctuation, all Hangul letters and digits were present somewhere in an overlapping output entry for 294/300 Fast cues and 295/300 Balanced cues. This is only a diagnostic: Korean spacing marks word boundaries, and the high content-only rate hides severe fragmentation. A complete line under common punctuation normalization appeared in the cue window for 201/300 Fast and 213/300 Balanced cues, but only 190/300 and 148/300 cues respectively passed the one-entry temporal matching rule. Only 105 Fast and 89 Balanced cues were exact under the one-to-one matched-cue score. Neither mode produced a single clip with all six exact cues and no extras.

**Timing and output quality:** among matched cues, median absolute start error was 0.400 seconds in both modes; median end error was 0.267 seconds Fast and 0.333 seconds Balanced. The both-boundaries rates are low even when unmatched cues count as failures: 6.3%/4.3% within 0.1 seconds and 14.0%/10.7% within 0.5 seconds for Fast/Balanced. All 1,889 Fast and 3,282 Balanced extras overlapped true subtitle windows, consistent with fragmentation or duplicate entries rather than detections between the labelled cues. Fast took about half the time and yielded 1,393 fewer extras, 42 more time-matched cues, and six more cues with both boundaries within 0.1 seconds. Balanced had 12 more complete normalized lines somewhere during cue windows, but did not convert those into clean, properly timed SRT entries.

**Conclusion:** neither mode currently meets a useful Korean subtitle extraction standard on this test. Fast is the less damaging choice, but its 63.3% time-matched capture, 35.0% exact matched text, 6.3% strict timing-within-0.1-second rate, and 1,889 extra entries are far from a reliable completed SRT. The large gap between content characters appearing in fragments and usable matched cues points first to OCR event stabilization and cue aggregation, with Korean text-line handling and the low-resolution sample also needing investigation. Do not interpret the character-only rate as 98% end-to-end accuracy or claim Korean reliability from this synthetic dataset.

### Arabic findings

The full [Arabic report](results/arabic/README.md) contains all extracted SRTs, cue-level comparisons, figures and CSV data. The Arabic pipeline loaded PP-OCRv5; both detection and recognition sessions exposed `CUDAExecutionProvider` with CPU fallback. The rendered text is right-to-left Arabic on the same 320×240 background.

| Mode | Time-matched cues | Exact matched text | Normalized full line in cue window | Arabic letters/digits somewhere in cue window* | Unmatched entries | Clean clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 152/300 (50.7%) | 51/300 (17.0%) | 101/300 (33.7%) | 166/300 (55.3%) | 2,333 | 0/50 | 17/300 (5.7%) | 42/300 (14.0%) | 9.25 s | 29.3 min |
| Balanced | 116/300 (38.7%) | 47/300 (15.7%) | 109/300 (36.3%) | 179/300 (59.7%) | 4,272 | 0/50 | 11/300 (3.7%) | 28/300 (9.3%) | 18.47 s | 58.5 min |

**Text capture versus usable cues:** the character-only measure ignores spaces and punctuation, so it does not assess Arabic word separation or the complete line. Arabic letters and digits appeared in an overlapping output entry for 166/300 Fast cues and 179/300 Balanced cues. A complete line after common punctuation normalization appeared somewhere in its cue window for 101/300 and 109/300 cues, respectively. However, only 152 Fast and 116 Balanced cues passed the one-entry temporal matching rule, and only 51 and 47 matched cues were strictly exact. Neither mode produced any clip with all six exact cues and no unmatched output.

**Timing and output quality:** among matched cues, median absolute start/end errors were 0.267/0.300 seconds for Fast and 0.400/0.267 seconds for Balanced. Counting unmatched cues as timing failures, both boundaries were within 0.1 seconds for 5.7%/3.7% and within 0.5 seconds for 14.0%/9.3% of all expected cues. Every unmatched entry overlapped a true cue window: 2,333 for Fast and 4,272 for Balanced. This points to extensive splitting or duplication during subtitle intervals rather than output appearing between labelled subtitles. Balanced found eight more normalized full lines in cue windows, but Fast produced 36 more time-matched cues, four more strictly exact matched cues, 1,939 fewer extras, and roughly half the runtime.

**Conclusion:** neither mode currently produces reliable Arabic SRTs on this controlled test. Fast is the better choice of the two, but it matched only half the cues in time, had 17.0% exact matched text, and placed both boundaries within 0.1 seconds for just 5.7% of expected cues. The normalized line and character-only rates do not offset the poor cue matching, timing, and fragmentation. Improving temporal OCR stabilization and subtitle event aggregation should be investigated before marketing Arabic extraction as reliable; native-speaker review and varied real Arabic footage are needed to diagnose text shaping, diacritics, spacing, and right-to-left rendering effects.

### Tamil findings

The full [Tamil report](results/tamil/README.md) includes cue-level results, extracted SRTs, CSV data, and figures. The app used the PP-OCRv5 Tamil recognizer; detection and recognition sessions exposed `CUDAExecutionProvider` with CPU fallback. The test uses the generated Tamil subtitles on the same low-resolution video background.

| Mode | Time-matched cues | Exact matched text | Normalized full line in cue window | Content characters somewhere in cue window* | Unmatched entries | Clean clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 102/300 (34.0%) | 60/300 (20.0%) | 170/300 (56.7%) | 212/300 (70.7%) | 2,888 | 0/50 | 9/300 (3.0%) | 26/300 (8.7%) | 7.46 s | 23.6 min |
| Balanced | 71/300 (23.7%) | 48/300 (16.0%) | 186/300 (62.0%) | 224/300 (74.7%) | 5,262 | 0/50 | 8/300 (2.7%) | 17/300 (5.7%) | 14.63 s | 46.4 min |

**Text capture versus usable cues:** the character-only score ignores spaces and punctuation, so it does not establish correct Tamil word spacing or line formatting; it does retain letters, numbers, and combining marks. Those content characters appeared in an overlapping OCR entry for 212/300 Fast cues and 224/300 Balanced cues. After the report's punctuation and spacing normalization, 170 and 186 complete lines appeared somewhere in their cue windows. Yet only 102 Fast and 71 Balanced cues passed the one-entry time-match rule, and only 60 and 48 matched cues were strictly exact. Neither mode produced any clip with six exact cues and no unmatched output.

**Timing and output quality:** among matched cues, median absolute start/end errors were 0.367/0.400 seconds for Fast and 0.333/0.333 seconds for Balanced. With unmatched cues counted as failures, both boundaries were within 0.1 seconds for only 3.0%/2.7% and within 0.5 seconds for 8.7%/5.7% of all expected cues. Every unmatched entry overlapped a labelled subtitle: 2,888 Fast and 5,262 Balanced extras. Fast produced 31 more time-matched cues, 12 more exact matched cues, 2,374 fewer unmatched entries, and took about half the time. Balanced found 16 more normalized full lines somewhere within their cue windows, but this did not produce better matched cues or clean SRT files.

**Conclusion:** Tamil extraction is not reliable enough to produce finished SRTs on this test. Fast is the less poor mode, but it time-matched only 34.0% of cues, had 20.0% exact matched text, and met the strict 0.1-second boundary tolerance for 3.0% of expected cues. The high extras and absence of clean clips point to severe OCR event fragmentation. Improving temporal stabilization and Tamil-aware cue assembly should precede any accuracy claims; native-speaker review and varied Tamil footage are needed to distinguish model recognition, vowel-sign shaping, and subtitle segmentation issues.

### Russian findings

The [Russian report](results/russian/README.md) includes per-cue comparisons, extracted SRTs, figures, and CSV data. The pipeline used the PP-OCRv5 multilingual Cyrillic recognizer (`eslav_PP-OCRv5_mobile_rec`); detection and recognition sessions exposed CUDA with CPU fallback.

| Mode | Time-matched cues | Exact matched text | Normalized full line in cue window | Content characters somewhere in cue window | Unmatched entries | Clean clips | Both boundaries within 0.1 s | Both within 0.5 s | Mean clip time | 1-hour estimate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fast | 261/300 (87.0%) | 210/300 (70.0%) | 280/300 (93.3%) | 300/300 | 908 | 0/50 | 114/300 (38.0%) | 147/300 (49.0%) | 7.15 s | 22.7 min |
| Balanced | 239/300 (79.7%) | 201/300 (67.0%) | 284/300 (94.7%) | 300/300 | 1,556 | 0/50 | 99/300 (33.0%) | 126/300 (42.0%) | 14.10 s | 44.7 min |

**Text recognition is promising, but the completed SRT still needs cleanup.** All Russian content letters and numbers appeared in an overlapping OCR entry for all 300 cues in each mode, and punctuation/spacing-normalized whole lines appeared for 280 Fast and 284 Balanced cues. However, the one-to-one time matcher qualified 261 and 239 cues, and only 210 and 201 matched cues were literally exact. Every unmatched output overlapped a labelled cue window (908 Fast, 1,556 Balanced), suggesting fragmentation or duplicate readings during subtitles rather than detections between cues. Neither mode produced any clip with all six literal exact cues and no extras.

**Timing limits:** median absolute start/end errors among matched cues were 0.067/0.067 seconds in Fast and 0/0 seconds in Balanced. Those medians hide a substantial tail: both boundaries were within 0.1 seconds for only 38.0%/33.0% of all expected cues and within 0.5 seconds for 49.0%/42.0%. Unmatched cues count as timing failures in these rates. Balanced gained four normalized full lines somewhere in their time windows but yielded 22 fewer time-matched cues, nine fewer exact matched cues, 648 more extras, and nearly twice the runtime.

**Conclusion:** Russian recognition is substantially stronger than the recent Korean, Arabic, and Tamil results, but timing and fragmentation still prevent consistently clean subtitles. Fast is the more practical mode on this benchmark. Preserve the raw detected text while improving temporal consolidation, then verify the timing and text on varied real Russian footage before calling the output reliable.

### English, Chinese and Japanese comparison: text and timing

This comparison applies the same content-character check to English, Simplified Chinese, and Japanese. It counts letters, CJK characters, and numbers while ignoring punctuation and whitespace. The full-line check normalizes common punctuation; it preserves English spacing and treats spacing as optional for Chinese and Japanese. Korean is reported separately because whitespace is meaningful for Hangul word boundaries and its severe fragmentation makes the content-only score particularly easy to misread. Boundary success means both cue start and end are within the stated tolerance. All rates use 300 expected cues as the denominator; an unmatched cue counts as a timing failure.

| Language | Mode | Content exact in matched cue | Content exact somewhere in cue window | Full line after language-aware punctuation normalization | Both boundaries within 0.1 s | Both boundaries within 0.5 s | Extra entries | Clips with six normalized exact cues and no extras |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| English | Fast | 299/300 | 300/300 | 296/300 | 267/300 (89.0%) | 270/300 (90.0%) | 99 | 24/50 |
| English | Balanced | 299/300 | 300/300 | 297/300 | 255/300 (85.0%) | 263/300 (87.7%) | 159 | 19/50 |
| English | Accurate | 299/300 | 300/300 | 297/300 | 255/300 (85.0%) | 263/300 (87.7%) | 159 | 19/50 |
| Chinese (Simplified) | Fast | 299/300 | 300/300 | 295/300 | 256/300 (85.3%) | 269/300 (89.7%) | 138 | 24/50 |
| Chinese (Simplified) | Balanced | 296/300 | 300/300 | 295/300 | 252/300 (84.0%) | 264/300 (88.0%) | 224 | 22/50 |
| Chinese (Simplified) | Accurate | 296/300 | 300/300 | 295/300 | 252/300 (84.0%) | 265/300 (88.3%) | 224 | 22/50 |
| Japanese | Fast | 300/300 | 300/300 | 293/300 | 287/300 (95.7%) | 290/300 (96.7%) | 37 | 34/50 |
| Japanese | Balanced | 299/300 | 300/300 | 295/300 | 284/300 (94.7%) | 289/300 (96.3%) | 65 | 34/50 |
| Japanese | Accurate | 299/300 | 300/300 | 295/300 | 286/300 (95.3%) | 289/300 (96.3%) | 65 | 34/50 |

**What this says about accuracy:** for these test phrases, Chinese content-character capture is comparable to English: the exact characters and numbers appeared in an overlapping OCR entry for every cue in both languages. The strict literal Chinese exact score of 131/300 (43.7%) is misleading on its own because optional spaces and punctuation variants count as errors; the language-aware full-line score is 295/300 (98.3%). The punctuation-normalized score is still a diagnostic, since some punctuation carries meaning and the emitted SRT contains the actual recognized marks.

**What it says about finished subtitles:** all three languages read their underlying characters well on these synthetic phrases, but English and Chinese Fast had 99 and 138 unmatched entries, while Japanese Fast had 37. Both boundaries were within 0.1 seconds for 89.0% of English cues, 85.3% of Chinese cues, and 95.7% of Japanese cues. At 0.5 seconds, the rates were 90.0%, 89.7%, and 96.7%. Japanese timing and extra-entry counts are encouraging; still, only 34 of 50 Japanese clips produced six normalized exact lines with no extras. The complete SRT output in every language may need review.

For product work, retain separate measures for characters, punctuation, cue fragmentation, and time boundaries. The current evidence points to output stabilization as a higher-priority improvement than swapping the Chinese model on the basis of strict punctuation-sensitive exact scores alone. Check these findings against real Chinese videos and have a fluent reader review punctuation and labels before changing the extraction behavior.

## Overall analysis across all 23 languages

The aggregate files [overall_summary_by_mode.csv](results/overall_summary_by_mode.csv), [overall_language_metrics.csv](results/overall_language_metrics.csv) and [overall_language_comparison.png](results/overall_language_comparison.png) combine the 23 language reports. Fast and Balanced each contain 1,150 clips and 6,900 expected cues.

| Pooled measure | Fast | Balanced |
|---|---:|---:|
| Time-matched cues | 6,063/6,900 (87.9%) | 5,788/6,900 (83.9%) |
| ≥95% similar text | 5,210/6,900 (75.5%) | 5,018/6,900 (72.7%) |
| Exact matched text | 4,697/6,900 (68.1%) | 4,587/6,900 (66.5%) |
| Unmatched output entries | 15,835 | 28,074 |
| Strictly clean clips: all six exact, no extras | 188/1,150 (16.3%) | 135/1,150 (11.7%) |
| Both boundaries within 0.1 s | 4,260/6,900 (61.7%) | 3,998/6,900 (57.9%) |
| Mean time per 18.93-second clip | 5.50 s | 10.31 s |
| Linear one-hour estimate | 17.4 min | 32.7 min |

**Fast versus Balanced:** Fast was quicker in all 23 languages, produced fewer unmatched entries in all 23, and had more cues with both boundaries within 0.1 seconds in all 23. It had more time-matched cues in 19 languages and tied in four; it had more exact matched cues in 19, tied in two, and trailed in two. Fast yielded more strictly clean clips in 12 languages and tied in 11. This supports Fast as the practical default for this benchmark. Balanced did not provide a consistent quality gain that offsets its runtime and fragmentation.

**Text recognition is language-dependent.** Using strict exact matched cue text, Fast reached at least 95% in eight of 23 languages: Dutch, English, German, Indonesian, Italian, Malay, Portuguese and Tagalog. This literal measure understates some CJK performance because spaces and punctuation vary: the language-aware full-line score was 295/300 (98.3%) for Simplified Chinese and 293/300 (97.7%) for Japanese, while Traditional Chinese reached 233/300 (77.7%). Conversely, Turkish, Ukrainian, Hindi, Korean, Arabic, Tamil and Vietnamese had significant text or cue-capture gaps. Polish and Swedish sit between the strongest Latin-script group and the weakest results; their detailed sections show the difference between recognizing characters and producing clean subtitle events.

**Output construction is a cross-language bottleneck.** The one-to-one matcher left 15,835 Fast and 28,074 Balanced entries unmatched; all overlapped a labelled cue interval. This pattern is consistent with duplicates or fragments during visible subtitle intervals, though overlap does not prove the cause. Only 16.3% of Fast clips and 11.7% of Balanced clips had all six exact cues with no extras. High cue text scores alone therefore do not establish that the exported SRT is clean. Cue stabilization, frame-to-frame agreement and careful fragment merging are the most broadly supported pipeline priorities.

**Timing remains weaker than basic character presence.** Across the pooled cue set, both boundaries met a strict 0.1-second tolerance for 61.7% Fast and 57.9% Balanced. The metric counts unmatched cues as timing failures; it is a practical end-to-end measure, not just boundary error among successful matches. Languages such as Traditional Chinese and Japanese show that the pipeline can time cues well when the recognizer and segmentation cooperate, while several scripts remain far behind.

**Product conclusion:** do not present all 23 language options as equally reliable. The synthetic benchmark supports strong text capture for a subset, but no single pooled score represents each script, and clean-clip rates show that most language exports still need review. Keep language-aware reporting, label weaker results conservatively, and prioritize native-speaker checks for low-scoring scripts.

**Limits:** each language uses 50 variants of one 320×240 source background and seven repeated base phrases. These results are controlled comparisons, not 23 independent real-world evaluations. The engine was called directly; the packaged EXE and UI were not exercised. ONNX Runtime listed CUDA and CPU providers but also warned that no CUDA plugin device was found, and GPU utilization was not measured. Runtime estimates are therefore provisional and cannot establish that inference ran fully on the RTX 4070.

## Product improvement recommendations

1. **Prioritize cue stabilization and merging.** Combine adjacent output fragments when their times touch, their subtitle positions agree, and normalized text is the same or a small OCR variation. Avoid merging genuinely different consecutive lines. This targets the recurring pattern across the tested languages: one visible subtitle becoming multiple SRT cues.
2. **Use frame-to-frame agreement before finalizing text.** A temporary missing space, punctuation mark, or one-character recognition variation should not immediately create a new cue. Keep confidence-weighted candidates within a subtitle interval and finalize the clearest supported wording after enough frames agree.
3. **Measure cue quality with script-aware outcomes.** Track whether content characters appeared, whether punctuation was right, whether a line was exact under a language-appropriate comparison, whether it was fragmented, and whether its boundaries meet timing tolerances. For CJK, report strict text, content characters with spaces/punctuation removed, and punctuation-normalized text separately. Keep the app's actual SRT unchanged by scoring normalization.
4. **Use Fast and Balanced as the default benchmark comparison.** Across all 23 languages Fast was faster, created fewer unmatched entries and had tighter 0.1-second cue boundaries; it also improved time matching and exact text in 19 languages each. Keep the original Accurate runs as historical data, but do not add it without evidence of a practical gain.
5. **Treat Korean as an OCR/output-stability issue before promoting it.** The Hangul content appears across fragments, but only 63.3% of Fast cues pass time matching, 35.0% have exact matched text, no clip is clean, and only 6.3% have both boundaries within 0.1 seconds. Investigate Korean-specific segmentation and temporal consensus, then re-test on varied, higher-resolution Korean footage with native-speaker review.
6. **Investigate Arabic segmentation and right-to-left handling before promoting it.** Fast time-matched 50.7% of cues; only 51/300 expected cues (17.0%) had exact matched text; no clip was clean; and just 5.7% had both boundaries within 0.1 seconds. Review output fragmentation, Arabic word spacing/diacritics and RTL rendering with a fluent reader on varied footage.
7. **Investigate Tamil recognition and cue assembly before promoting it.** Fast only time-matched 34.0% of cues, 20.0% of expected cues had exact matched text, no clip was clean, and 97% of cues failed the strict 0.1-second timing check. Review Tamil spacing and vowel-sign shaping with a fluent reader, then test temporal stabilization on varied footage.
8. **Polish Russian cue consolidation and timing.** Character capture is strong, but only 87.0% of Fast cues passed time matching; 908 extras were produced, and both timing boundaries were within 0.1 seconds for 38.0% of expected cues. Fast is preferable to Balanced in this sample; validate cue stabilization on real Russian videos.
9. **Improve French cue consolidation and punctuation stability.** Fast read content characters for all 300 expected cues, but only 90.3% had a punctuation-normalized full line in the cue window and 10/50 clips were exact with no extras. Fast reduced extras and runtime versus Balanced; validate on varied French footage.
10. **Consolidate Spanish and Italian OCR events before export.** Both runs found the content characters in every expected cue, but only 85.3% of Spanish Fast cues formed a normalized full line, and just 3/50 Spanish clips were clean. Italian full-line recognition was stronger (99.3% Fast), yet only 12/50 clips were clean and 213 unmatched entries remained. Fast reduced fragmentation in both languages; validate cue merging on varied videos.
11. **Keep Vietnamese Experimental and evaluate a Vietnamese-specific recognizer.** Fast produced only 40/300 exact matched cues, complete text in 43/300 cue windows, 916 extra entries and no clean clips; Balanced was worse on each output-quality measure. The result supports the existing Experimental status. Test tone-mark coverage with a Vietnamese-speaking reviewer before changing it.
12. **Validate Portuguese on varied natural footage and improve cue consolidation.** Fast produced 296/300 exact matched cues and 298/300 punctuation-normalized full lines, with 97 extra entries and 22/50 clean clips. It outperformed Balanced on exact matches, extras, timing and runtime; verify on natural Portuguese footage.
13. **Validate Tagalog on varied natural footage.** Fast had 95.0% exact matched text and 98.0% punctuation-normalized full lines, but 144 extra entries and only 16/50 fully clean clips. Fast is preferable to Balanced here; confirm with varied Tagalog video and fluent review.
14. **Validate Dutch on varied natural footage.** Fast had 98.0% exact matched text and 98.7% normalized full lines, with 79 extras and 23/50 strict clean clips. It outperformed Balanced on extras, timing and runtime; confirm on natural Dutch videos.
15. **Improve Traditional Chinese punctuation and spacing stability.** Fast recovered the exact Han-character/number sequence for all 300 cues, but only 233 full lines matched after the report’s punctuation/spacing normalization and no clip was strictly exact with no extras. Timing was within 0.1 seconds for 97.0% of cues, so prioritize text formatting and stability while preserving the strong timing result. Validate with native Traditional Chinese readers.
16. **Test the 80% confidence threshold as part of a wider quality trade-off.** Confidence alone did not prevent short fragments from entering the output. Future comparisons should measure both removed false detections and any true subtitle text lost at higher thresholds.
17. **Validate across representative videos before making accuracy claims.** Use multiple resolutions, frame rates, codecs, source backgrounds, font sizes, colors, outlines, short and long cue durations, two-line subtitles, and natural phrase variety. Include a native-language review of labels. This synthetic dataset is suitable for controlled mode comparisons, not a general real-world accuracy guarantee.
18. **Test the packaged app after engine improvements.** The benchmark exercises the Python engine directly. Confirm that the packaged Windows executable uses the same extraction logic and settings, and check export, queue operation, and the visible SRT after integration.

19. **Investigate Ukrainian event consolidation and timing.** Although content characters appeared somewhere in 294/300 cue windows, Fast matched only 216/300 cues, produced 1,417 extra entries, had no clean clips and met the 0.1-second two-boundary check for only 23.3% of cues. Improve temporal stability and validate Cyrillic wording with a Ukrainian reader.
20. **Treat Hindi as a recognition and output-quality gap.** Fast exactly matched 143/300 cues, produced 1,909 extras and had no clean clips; Balanced was weaker and produced 3,395 extras. Inspect Devanagari shaping/recognition and cue assembly with a Hindi reader before promoting the language.
21. **Validate Indonesian on varied natural footage.** Fast scored 296/300 exact matched cues and 298/300 punctuation-normalized full lines, but 121 unmatched entries remained and only 25/50 clips were strict-clean. Keep Fast as the practical mode in this sample and validate on diverse real Indonesian video.
22. **Validate Malay on varied natural footage.** Fast exactly matched 296/300 cues with 95 extras and 23/50 strictly clean clips. The controlled result is strong, but confirm it across real Malay videos and fluent review.
23. **Investigate Turkish recognition and cue assembly.** Fast exactly matched 174/300 cues, produced 982 extras and had no strictly clean clips; Balanced produced 1,711 extras. Examine Turkish character recognition and temporal consolidation with a fluent reviewer before making reliability claims.
24. **Improve Polish recognition and consolidation.** Fast matched 77.7% of cues exactly, with 730 extras and only one strictly clean clip. The content appeared somewhere in 273/300 cue windows, so inspect both text recognition and event assembly with a Polish reviewer.
25. **Validate Swedish across real footage and reduce fragments.** Fast exactly matched 86.3% of cues and met both 0.1-second boundaries for 69.7%, but only 11/50 clips were strictly clean. Confirm performance on varied Swedish videos and reduce duplicate/fragment output.


## How to interpret the evidence

- The cue matcher requires at least 30% temporal overlap with one unique detected entry. It prioritizes matching the number of cues and then text similarity. A matched cue can still have wrong text; an unmatched cue can still have its text among several fragments.
- Exact text comparison uses Unicode NFC and whitespace normalization; punctuation and case count. The ≥95% score uses normalized Levenshtein similarity. Missed cues count as errors.
- “Extra” means an output entry left unmatched after one-to-one comparison. Overlap with a real cue suggests a duplicate or fragment, but timing overlap by itself does not prove what caused the entry.
- One-hour times are linear extrapolations from 18.93-second clips. They exclude model initialization and export. They are not runtime guarantees for longer, higher-resolution or more complex footage.
- The 50 clips reuse one low-resolution moving background and seven base phrases per language. They are repeated controlled tests, not 50 independent real-world videos; cue totals should not be treated as an independent random sample of subtitle use.

## Language progress

| Language | Status | Report |
|---|---|---|
| English | Complete: 50 clips × 3 historical modes | [English results](results/english/README.md) |
| German | Complete: 50 clips × 3 historical modes | [German results](results/german/README.md) |
| Chinese (Simplified) | Complete: 50 clips × 3 historical modes | [Chinese results](results/chinese_simplified/README.md) |
| Japanese | Complete: 50 clips × 3 historical modes | [Japanese results](results/japanese/README.md) |
| Korean | Complete: 50 clips × Fast and Balanced | [Korean results](results/korean/README.md) |
| Arabic | Complete: 50 clips × Fast and Balanced | [Arabic results](results/arabic/README.md) |
| Tamil | Complete: 50 clips × Fast and Balanced | [Tamil results](results/tamil/README.md) |
| Russian | Complete: 50 clips × Fast and Balanced | [Russian results](results/russian/README.md) |
| French | Complete: 50 clips × Fast and Balanced | [French results](results/french/README.md) |
| Spanish | Complete: 50 clips × Fast and Balanced | [Spanish results](results/spanish/README.md) |
| Italian | Complete: 50 clips × Fast and Balanced | [Italian results](results/italian/README.md) |
| Portuguese | Complete: 50 clips × Fast and Balanced | [Portuguese results](results/portuguese/README.md) |
| Dutch | Complete: 50 clips × Fast and Balanced | [Dutch results](results/dutch/README.md) |
| Chinese (Traditional) | Complete: 50 clips × Fast and Balanced | [Traditional Chinese results](results/chinese_traditional/README.md) |
| Tagalog (Filipino option) | Complete: 50 clips × Fast and Balanced | [Tagalog results](results/filipino/README.md) |
| Vietnamese (Experimental) | Complete: 50 clips × Fast and Balanced | [Vietnamese results](results/vietnamese/README.md) |
| Ukrainian | Complete: 50 clips × Fast and Balanced | [Ukrainian results](results/ukrainian/README.md) |
| Hindi | Complete: 50 clips × Fast and Balanced | [Hindi results](results/hindi/README.md) |
| Indonesian | Complete: 50 clips × Fast and Balanced | [Indonesian results](results/indonesian/README.md) |
| Malay | Complete: 50 clips × Fast and Balanced | [Malay results](results/malay/README.md) |
| Turkish | Complete: 50 clips × Fast and Balanced | [Turkish results](results/turkish/README.md) |
| Polish | Complete: 50 clips × Fast and Balanced | [Polish results](results/polish/README.md) |
| Swedish | Complete: 50 clips × Fast and Balanced | [Swedish results](results/swedish/README.md) |
