# Video OCR pipeline

The workflow starts from video frames. It does not transcribe audio, read selectable subtitle tracks, or remove text from the picture.

The CLI in this repository follows the same broad OCR stages and settings used by the desktop app, but it is a separately maintained reference implementation. Changes to this script do not update the desktop app. The app source, executable, and installers are distributed separately.

## Steps

1. Open the video with OpenCV and read its dimensions, frame rate and duration.
2. Convert a normalized rectangle to pixel coordinates and crop that region from sampled frames. The default covers the bottom 35 percent.
3. Sample the timeline at 1 FPS in Fast mode or 3 FPS in Balanced mode. A language-aware image signature can reuse an OCR result when the crop has not changed enough to justify another inference.
4. Upscale short crops to improve the pixel height of small captions. Borderline readings get one retry with local contrast enhancement and sharpening. PaddleOCR runs text detection and recognition with ONNX Runtime on CPU or NVIDIA CUDA.
5. Drop text below the confidence threshold. Optional filters check detected-box color and horizontal position; these filters reduce unrelated text but cannot identify subtitles perfectly.
6. Group readings that are similar and in roughly the same position into a cue. A confidence-weighted consensus chooses a stable reading. Script-specific comparisons use different similarity thresholds and ignore whitespace for CJK and Hangul.
7. Join very short gaps between matching cues. Balanced mode also performs three rounds of OCR boundary checks between sampled times. Fast keeps the coarser sample-based boundaries.
8. Write cue text and timings as UTF-8 SRT.

## Parameters and tradeoffs

| Setting | Fast | Balanced |
| --- | --- | --- |
| Frame sampling | 1 FPS | 3 FPS |
| Boundary refinement | Off | Three OCR checks per boundary bracket |
| Intended use | Quick pass; short cues may be missed | More coverage and finer timing; more inference work |

The default confidence is 0.80. Raising it can suppress weak or unrelated detections but can also discard real subtitle text. Lowering it can retain more text along with more false detections. For captions outside the default crop, change `--region`; for non-white text, set `--color` or use `any`. A crop that is too large exposes more signs and overlay text to OCR, while a crop that is too small can cut off subtitle strokes.

## Accuracy notes

Post-processing can stabilize repeated readings, join short gaps and improve timing between samples. It cannot restore a character the recognizer never detected or recognized. The frame cadence also puts a hard limit on short-cue coverage. The 80 percent OCR confidence value is not an accuracy guarantee.

The benchmark archive records controlled synthetic clips and earlier versions of this pipeline. It is useful for regression checks and for comparing settings on the same material. It does not establish performance on ordinary films or varied real-world video, and it does not validate this standalone script as a packaged product. See the [v0.6 benchmark master report](../benchmarks/v0.6.0/second-benchmark/MASTER_BENCHMARK_ANALYSIS.md) for scope and limitations.

See the [desktop app guide](APP_GUIDE.md), the [CLI setup guide](../workflow/README.md), and the [sample capture gallery](../sample_app_images/README.md) for the visible workflow and one recorded CLI result.
