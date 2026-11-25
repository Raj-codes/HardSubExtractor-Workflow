# Set up the CLI workflow

This repository includes a command-line reference workflow for burned-in subtitle OCR. It opens one video, samples frames, runs OCR in a chosen region, groups readings into timed cues, and writes an SRT draft. It uses the same broad extraction stages as the desktop app, but it is a separate entry point; the app source and build are not included here.

The CLI does not read audio or selectable subtitle tracks, and it does not alter the video. The output is an SRT draft for review.

## 1. Create a Python environment

Python 3.12 is the version used for the recorded dependency snapshot. From the repository root, create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 2. Install one inference backend

For CPU inference, install the CPU ONNX Runtime package:

```bash
python -m pip install -r workflow/requirements-cpu.txt
```

For NVIDIA inference, install the GPU ONNX Runtime package instead. Use a supported NVIDIA GPU and driver. The pinned ONNX Runtime 1.30 package uses CUDA 13 by default; check the [ONNX Runtime CUDA compatibility table](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html) for your driver and CUDA/cuDNN combination.

```bash
python -m pip install -r workflow/requirements-nvidia.txt
```

Do not install both requirements files in the same environment. CPU mode works without CUDA. GPU mode raises an error if ONNX Runtime cannot see its CUDA provider.

## 3. Run an extraction

The first run downloads the selected OCR model files to PaddleX's local model cache. The script sets that cache to `~/.cache/video-subtitle-ocr/paddlex` unless `PADDLE_PDX_CACHE_HOME` is already set. Internet access is needed for this first download.

To choose a different cache directory, set `PADDLE_PDX_CACHE_HOME` before running the command. For example, in PowerShell:

```powershell
$env:PADDLE_PDX_CACHE_HOME = "$env:LOCALAPPDATA\HardSubExtractor\models"
```

CPU example:

```bash
python workflow/video_to_srt.py \
  --video "samples/episode.mp4" \
  --language english \
  --mode balanced \
  --device cpu \
  --region 0,0.65,1,1 \
  --confidence 0.80 \
  --color white \
  --output "output/episode.srt"
```

PowerShell uses backticks for line continuation, or put the command on one line:

```powershell
python workflow/video_to_srt.py --video "samples\episode.mp4" --language english --mode balanced --device gpu --region 0,0.65,1,1 --confidence 0.80 --color white --output "output\episode.srt"
```

The command-line arguments choose the video, OCR language, sampling mode, device, normalized crop, minimum confidence, text color, and output path. `--region` is `x1,y1,x2,y2`, with each value from 0 to 1 relative to the frame. The default `0,0.65,1,1` covers the bottom 35 percent. Use `--no-centered` if subtitles are not near the horizontal center, or `--color any` to disable color filtering.

## 4. Review the SRT

Open the output in a subtitle editor and compare it with the video. Check missed cues, spelling, cue splits, false readings and timing. OCR confidence is a model score; it does not mean that a cue is correct. The workflow creates a draft and does not modify the video or audio.

See [pipeline notes](../docs/PIPELINE.md), [model references](MODELS.md), and the [benchmark archive](../benchmarks/README.md).

## Example output

The repository contains the SRT from a real CPU run on the local English benchmark clip: [`examples/english/en_015-cli.srt`](../examples/english/en_015-cli.srt). The video is not included. Its six text lines matched the reference labels in that run; the largest start/end difference was 0.034 seconds. This result is only for that short controlled clip.

The desktop app screenshots in [`sample_app_images/`](../sample_app_images/README.md) show separate English and Japanese video runs. They demonstrate the interface; they are not images from the CLI test clip.
