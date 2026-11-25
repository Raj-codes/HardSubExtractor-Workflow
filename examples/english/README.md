# English CLI example

`en_015-cli.srt` is the SRT produced by running `workflow/video_to_srt.py` on the local 18.93-second `en_015.mp4` benchmark clip.

Settings: English, Balanced (3 sample FPS), CPU, bottom 35% crop, 80% minimum confidence, white text, centered filter. The OCR models were fetched from the official Paddle model host and cached temporarily for this run; the model files are not included here.

The source clip's reference SRT has six labeled cues. This output has six cues with matching text; the largest start or end boundary difference is 0.034 seconds. The result is from one controlled clip and should not be read as a real-world accuracy estimate. The [app screenshot gallery](../../sample_app_images/README.md) shows separate English and Japanese runs.
