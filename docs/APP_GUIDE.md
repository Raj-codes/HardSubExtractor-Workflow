# Desktop app guide

HardSub Extractor reads subtitle text that is visible in a video image and saves it as an editable SRT. The app runs OCR locally. It does not transcribe the audio, extract selectable subtitle tracks, translate text, or remove subtitle pixels from the video.

## Get the desktop app

The app is free to download from the [Ko-fi Shop](https://ko-fi.com/s/d468456083), [Patreon](https://www.patreon.com/ChumuDieKatze/posts/hardsubextractor-176361705), or [Payhip](https://payhip.com/b/aAZS8). The app build and installers are distributed separately and are not stored in this repository.

**System requirements:** For GPU inference, use an NVIDIA CUDA-compatible GPU with at least 4 GB VRAM (estimated minimum; 6–8 GB recommended). CPU inference is also available.

**Installation instructions:** See `INSTALL_FIRST.txt` inside the ZIP file.

The app package does not include every OCR model. During setup or first use, select the languages needed for the video. The app downloads those model files, and the model manager can add languages later. An internet connection is needed for a model’s first download; already downloaded models are kept on the device for later runs.

## Extract subtitles

1. Load a video. Add more videos to the queue when processing a batch.
2. Set the subtitle region to the bottom 35% or full frame. The crop should include the complete subtitle line while excluding unrelated text where possible.
3. Select the OCR language and mode. Fast samples at 1 FPS; Balanced samples at 3 FPS and refines cue boundaries. Balanced is the recommended starting point for normal subtitle pacing.
4. Choose CPU or NVIDIA GPU inference. CPU mode works without CUDA; GPU mode requires a compatible NVIDIA setup and installed runtime.
5. Set the minimum OCR confidence and filters. The app can filter by subtitle text color and centered placement. A stricter confidence value can reduce weak or unrelated detections, but it can also discard real text.
6. Start extraction. The preview and cue table show the current video frame, recognized text, timing, and OCR confidence.
7. Review the SRT cues. Edit wording or timing, delete a cue from the subtitle result, and export the SRT when it is ready.

Deleting a cue removes it from the SRT result only. It does not erase burned-in text from the video.

## Queue and export

Multiple videos can be added from the file browser. The app processes the queue in order, exports completed SRTs to the chosen output folder when automatic export is enabled, and loads the next queued video. The output folder can also be opened from the app.

## Interface options

The app includes a light theme and interface language choices for English, German, French, Spanish, Chinese, Korean, Japanese, Portuguese, and Italian. OCR language is selected separately from interface language.

The app supports 18 OCR language choices: English, German, French, Spanish, Italian, Portuguese, Dutch, Japanese, Korean, Simplified Chinese, Traditional Chinese, Russian, Ukrainian, Indonesian, Malay, Filipino/Tagalog, Polish, and Swedish. The OCR model mapping is in [MODELS.md](../workflow/MODELS.md).

## Accuracy and review

OCR is sensitive to subtitle size, contrast, outline, motion blur, screen position, and sampling cadence. Short cues can fall between sampled frames. Confidence is a recognition score, not a word-accuracy measure. Treat every generated SRT as a draft and compare it with the video.

The [benchmark reports](../benchmarks/README.md) describe controlled synthetic tests. They are useful for comparing versions on the same clips; they do not guarantee real-world accuracy or timing on a particular film or video.
