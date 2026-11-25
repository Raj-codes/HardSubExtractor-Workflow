#!/usr/bin/env python3
"""Extract burned-in subtitle text from a video and write an SRT file."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


LANGUAGES = {
    "english": ("en", "PP-OCRv6", "latin"),
    "german": ("de", "PP-OCRv6", "latin"),
    "french": ("fr", "PP-OCRv6", "latin"),
    "spanish": ("es", "PP-OCRv6", "latin"),
    "italian": ("it", "PP-OCRv6", "latin"),
    "portuguese": ("pt", "PP-OCRv6", "latin"),
    "dutch": ("nl", "PP-OCRv6", "latin"),
    "japanese": ("japan", "PP-OCRv6", "cjk"),
    "korean": ("korean", "PP-OCRv5", "hangul"),
    "chinese-simplified": ("ch", "PP-OCRv6", "cjk"),
    "chinese-traditional": ("chinese_cht", "PP-OCRv6", "cjk"),
    "russian": ("ru", "PP-OCRv5", "cyrillic"),
    "ukrainian": ("uk", "PP-OCRv5", "cyrillic"),
    "indonesian": ("id", "PP-OCRv6", "latin"),
    "malay": ("ms", "PP-OCRv6", "latin"),
    "filipino": ("tl", "PP-OCRv6", "latin"),
    "polish": ("pl", "PP-OCRv6", "latin"),
    "swedish": ("sv", "PP-OCRv6", "latin"),
}

MODE = {
    "fast": {"fps": 1.0, "blank_grace": 0.45, "visual_skip": 2.0, "refine": 0, "min_duration": 0.20},
    "balanced": {"fps": 3.0, "blank_grace": 0.28, "visual_skip": 1.5, "refine": 3, "min_duration": 0.18},
}
SCRIPT = {
    "latin": {"event": 0.92, "boundary": 0.84, "visual_scale": 1.0, "ignore_space": False},
    "cjk": {"event": 0.88, "boundary": 0.78, "visual_scale": 0.78, "ignore_space": True},
    "hangul": {"event": 0.90, "boundary": 0.80, "visual_scale": 0.72, "ignore_space": True},
    "cyrillic": {"event": 0.92, "boundary": 0.84, "visual_scale": 0.88, "ignore_space": False},
}
COLOR_HUES = {"yellow": (15, 40), "green": (36, 85), "cyan": (82, 105), "blue": (95, 135), "magenta": (135, 169)}
COLORS = ("any", "white", "yellow", "green", "cyan", "blue", "magenta", "red")


@dataclass
class OCRRead:
    text: str = ""
    confidence: float = 0.0
    center_x: Optional[float] = None
    center_y: Optional[float] = None


@dataclass
class Cue:
    start: float
    end: float
    text: str
    confidence: float
    start_low: Optional[float] = None
    start_high: Optional[float] = None
    end_low: Optional[float] = None
    end_high: Optional[float] = None
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    readings: list[tuple[str, float]] = field(default_factory=list)


def clean_text(value: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)


def comparison_text(value: str, script: str) -> str:
    value = unicodedata.normalize("NFC", clean_text(value)).casefold().replace("|", "l")
    value = "".join(ch for ch in value if unicodedata.category(ch)[0] in "LNM" or ch.isspace())
    value = re.sub(r"\s+", " ", value).strip()
    if SCRIPT[script]["ignore_space"]:
        value = "".join(value.split())
    return value


def similarity(a: str, b: str, script: str) -> float:
    left, right = comparison_text(a, script), comparison_text(b, script)
    return SequenceMatcher(None, left, right).ratio() if left and right else float(left == right)


def time_srt(seconds: float) -> str:
    total = int(round(max(0.0, seconds) * 1000))
    hours, rem = divmod(total, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds_i, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_i:02d},{millis:03d}"


def parse_region(value: str, width: int, height: int) -> tuple[int, int, int, int]:
    try:
        parts = [float(part.strip()) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Region must be four comma-separated fractions, e.g. 0,0.65,1,1") from exc
    if len(parts) != 4 or any(part < 0 or part > 1 for part in parts):
        raise argparse.ArgumentTypeError("Region values must be x1,y1,x2,y2 fractions between 0 and 1")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("Region x2/y2 must be greater than x1/y1")
    return (max(0, min(width - 1, round(x1 * width))), max(0, min(height - 1, round(y1 * height))),
            max(1, min(width, round(x2 * width))), max(1, min(height, round(y2 * height))))


def crop(frame: np.ndarray, roi: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = roi
    return frame[y1:y2, x1:x2]


def upscale(frame: np.ndarray) -> np.ndarray:
    height, width = frame.shape[:2]
    if height < 220:
        scale = min(2.0, 220.0 / max(1, height))
        frame = cv2.resize(frame, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_CUBIC)
    return frame


def signature(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    target_w = 192
    target_h = max(24, min(96, round(target_w * gray.shape[0] / max(1, gray.shape[1]))))
    return cv2.GaussianBlur(cv2.resize(gray, (target_w, target_h), interpolation=cv2.INTER_AREA), (3, 3), 0).astype(np.float32)


def difference(a: Optional[np.ndarray], b: np.ndarray) -> float:
    if a is None or a.shape != b.shape:
        return math.inf
    delta = np.abs(a - b)
    tiles = cv2.resize(delta, (max(1, b.shape[1] // 8), max(1, b.shape[0] // 8)), interpolation=cv2.INTER_AREA)
    return float(tiles.max())


def color_ratio(patch: np.ndarray, target: str) -> float:
    if not patch.size:
        return 0.0
    hue, saturation, value = cv2.split(cv2.cvtColor(patch, cv2.COLOR_BGR2HSV))
    if target == "white":
        mask = (saturation <= 80) & (value >= 140)
    elif target == "red":
        mask = ((hue <= 10) | (hue >= 170)) & (saturation >= 70) & (value >= 95)
    else:
        low, high = COLOR_HUES[target]
        mask = (hue >= low) & (hue <= high) & (saturation >= 70) & (value >= 95)
    return float(np.mean(mask))


class PaddleBackend:
    def __init__(self, language: str, device: str, confidence: float, color: str, centered: bool):
        self.language = language
        lang_code, ocr_version, _script = LANGUAGES[language]
        cache = Path(os.environ.get(
            "PADDLE_PDX_CACHE_HOME",
            Path.home() / ".cache" / "video-subtitle-ocr" / "paddlex",
        )).expanduser()
        cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache))
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
        if device == "gpu":
            try:
                import onnxruntime as ort
                if "CUDAExecutionProvider" not in ort.get_available_providers():
                    raise RuntimeError("CUDAExecutionProvider is missing. Install the GPU requirements and check the NVIDIA driver/runtime.")
                if hasattr(ort, "preload_dlls"):
                    ort.preload_dlls(directory="")
            except Exception as exc:
                raise RuntimeError(f"Could not prepare ONNX Runtime GPU support: {exc}") from exc
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                lang=lang_code,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                engine="onnxruntime",
                device=device,
                text_det_thresh=0.25,
                text_det_box_thresh=0.50,
                ocr_version=ocr_version,
            )
        except Exception as exc:
            raise RuntimeError(f"PaddleOCR could not initialize ({device}): {exc}") from exc
        self.confidence = confidence
        self.color = color
        self.centered = centered
        self.width = 0
        self.height = 0

    def read(self, image: np.ndarray) -> OCRRead:
        if not image.size or float(np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))) < 1.0:
            return OCRRead()
        result = self._read_once(image, image)
        retry_threshold = min(0.92, self.confidence + 0.12)
        borderline_empty = (not result.text and max(0.45, self.confidence - 0.35) <= self.candidate_score < self.confidence)
        if borderline_empty or (result.text and result.confidence < retry_threshold):
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            enhanced = cv2.addWeighted(enhanced, 1.5, cv2.GaussianBlur(enhanced, (0, 0), 0.8), -0.5, 0)
            retry = self._read_once(enhanced, image)
            if retry.text and retry.confidence > result.confidence + 0.01:
                result = retry
        return result

    def _read_once(self, image: np.ndarray, color_reference: np.ndarray) -> OCRRead:
        self.candidate_score = 0.0
        self.height, self.width = image.shape[:2]
        results = list(self.ocr.predict(image))
        if not results:
            return OCRRead()
        raw = results[0].json
        if isinstance(raw, str):
            raw = json.loads(raw)
        data = raw.get("res", raw) if isinstance(raw, dict) else {}
        texts = data.get("rec_texts")
        scores_raw = data.get("rec_scores")
        texts = [] if texts is None else list(texts)
        scores_raw = [] if scores_raw is None else list(scores_raw)
        boxes = data.get("rec_boxes")
        try:
            scores = [float(value) for value in scores_raw]
        except (TypeError, ValueError):
            scores = []
        self.candidate_score = max(scores, default=0.0)
        records = []
        for i, raw_text in enumerate(texts):
            text = clean_text(str(raw_text))
            score = scores[i] if i < len(scores) else 1.0
            if not text or score < self.confidence:
                continue
            box = None
            if boxes is not None:
                try:
                    box = [int(round(float(v))) for v in boxes[i][:4]]
                except (IndexError, TypeError, ValueError):
                    box = None
            if box and len(box) == 4:
                x1, y1, x2, y2 = box
                x1, x2 = max(0, x1), min(self.width, x2)
                y1, y2 = max(0, y1), min(self.height, y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                if self.color != "any":
                    threshold = 0.018 if self.color == "white" else 0.010
                    if color_ratio(color_reference[y1:y2, x1:x2], self.color) < threshold:
                        continue
                if self.centered and abs((x1 + x2) / 2 - self.width / 2) > self.width * 0.35:
                    continue
            records.append((text, score, box))
        if not records:
            return OCRRead()
        records.sort(key=lambda row: ((row[2][1] + row[2][3]) / 2) if row[2] else 0)
        lines: list[tuple[float, float, list]] = []
        for record in records:
            box = record[2]
            if box is None:
                lines.append((0.0, 0.0, [record]))
                continue
            center = (box[1] + box[3]) / 2
            line_height = max(1, box[3] - box[1])
            if lines and lines[-1][2][0][2] is not None and abs(center - lines[-1][0]) <= .45 * max(line_height, lines[-1][1]):
                lines[-1][2].append(record)
            else:
                lines.append((center, line_height, [record]))
        separator = "" if LANGUAGES[self.language][2] == "cjk" else " "
        text_lines = []
        for _center, _height, line in lines:
            line.sort(key=lambda row: row[2][0] if row[2] else 0)
            text_lines.append(separator.join(row[0] for row in line))
        valid_boxes = [r[2] for r in records if r[2] is not None]
        center_x = float(np.mean([(b[0] + b[2]) / 2 for b in valid_boxes])) if valid_boxes else None
        center_y = float(np.mean([(b[1] + b[3]) / 2 for b in valid_boxes])) if valid_boxes else None
        return OCRRead("\n".join(text_lines), sum(r[1] for r in records) / len(records), center_x, center_y)


class Extractor:
    def __init__(self, args: argparse.Namespace, backend: PaddleBackend, roi: tuple[int, int, int, int], fps: float, duration: float):
        self.args, self.backend, self.roi = args, backend, roi
        self.info_fps, self.duration = fps, duration
        self.profile = SCRIPT[LANGUAGES[args.language][2]]
        self.mode = MODE[args.mode]
        self.sample_fps = min(self.mode["fps"], fps)
        self.interval = 1.0 / self.sample_fps
        self.entries: list[Cue] = []

    def spatial_match(self, cue: Cue, read: OCRRead) -> bool:
        roi_w, roi_h = max(1, self.roi[2] - self.roi[0]), max(1, self.roi[3] - self.roi[1])
        return not ((cue.center_x is not None and read.center_x is not None and abs(cue.center_x-read.center_x)/roi_w > .18)
                    or (cue.center_y is not None and read.center_y is not None and abs(cue.center_y-read.center_y)/roi_h > .18))

    def consensus(self, readings: list[tuple[str, float]]) -> tuple[str, float]:
        groups: list[list[tuple[str, float]]] = []
        for item in readings:
            matches = [g for g in groups if similarity(g[0][0], item[0], LANGUAGES[self.args.language][2]) >= self.profile["event"]]
            if matches:
                max(matches, key=lambda g: similarity(g[0][0], item[0], LANGUAGES[self.args.language][2])).append(item)
            else:
                groups.append([item])
        best = max(groups, key=lambda g: (len(g), sum(x[1] for x in g) / len(g)))
        representative = max(best, key=lambda x: (x[1], len(comparison_text(x[0], LANGUAGES[self.args.language][2]))))
        return representative[0], sum(x[1] for x in best) / len(best)

    def finalize(self, cue: Cue, end_low: float, end_high: float) -> None:
        cue.end_low = max(cue.start, end_low)
        cue.end_high = max(cue.end_low + .01, end_high)
        cue.end = max(cue.start + self.mode["min_duration"], min(cue.end_high, cue.end_low + self.interval))
        if clean_text(cue.text) and cue.end > cue.start:
            self.entries.append(cue)

    def extract(self) -> list[Cue]:
        start = max(0.0, self.args.start)
        end = min(self.duration, self.args.end if self.args.end is not None else self.duration)
        if end <= start:
            raise ValueError("--end must be greater than --start and within the video duration")
        cap = cv2.VideoCapture(str(self.args.video))
        if not cap.isOpened():
            raise RuntimeError("OpenCV could not open this video. Check the path and its video codec.")
        sample_step = 1.0 / self.sample_fps
        next_at = start
        previous_sample = None
        previous_sig = None
        previous_read = OCRRead()
        last_ocr_at = -math.inf
        current: Optional[Cue] = None
        last_seen = None
        blank_at = None
        start_frame = max(0, int(math.floor(start * self.info_fps)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frame_index = start_frame - 1
        count = 0
        started = time.monotonic()
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame_index += 1
                t = frame_index / self.info_fps
                if t + .5 / self.info_fps < next_at:
                    continue
                if t >= end:
                    break
                while next_at <= t + .5 / self.info_fps:
                    next_at += sample_step
                signature_now = signature(crop(frame, self.roi))
                count += 1
                elapsed_since_ocr = t - last_ocr_at
                cached = (previous_sig is not None
                          and difference(previous_sig, signature_now) < self.mode["visual_skip"] * self.profile["visual_scale"]
                          and elapsed_since_ocr < (.75 if previous_read.text else .25))
                if cached:
                    read = previous_read
                else:
                    read = self.backend.read(upscale(crop(frame, self.roi)))
                    previous_read, previous_sig, last_ocr_at = read, signature_now, t
                text = clean_text(read.text)
                if text:
                    if current is not None and blank_at is not None and t - blank_at >= self.mode["blank_grace"]:
                        self.finalize(current, last_seen if last_seen is not None else current.end, blank_at)
                        current, last_seen, blank_at = None, None, None
                    blank_at = None
                    if current is None:
                        current = Cue(t, t + self.interval, text, read.confidence,
                                      max(0.0, previous_sample if previous_sample is not None else t-self.interval), t,
                                      center_x=read.center_x, center_y=read.center_y,
                                      readings=[(text, read.confidence)])
                        last_seen = t
                    elif (similarity(current.text, text, LANGUAGES[self.args.language][2]) >= self.profile["event"]
                          and self.spatial_match(current, read)):
                        last_seen = t
                        current.end = t + self.interval
                        if not cached:
                            current.readings.append((text, read.confidence))
                            current.text, current.confidence = self.consensus(current.readings)
                        if current.center_x is None:
                            current.center_x = read.center_x
                        if current.center_y is None:
                            current.center_y = read.center_y
                    else:
                        self.finalize(current, last_seen if last_seen is not None else t-self.interval, t)
                        current = Cue(t, t + self.interval, text, read.confidence,
                                      max(0.0, previous_sample if previous_sample is not None else t-self.interval), t,
                                      center_x=read.center_x, center_y=read.center_y,
                                      readings=[(text, read.confidence)])
                        last_seen = t
                elif current is not None:
                    if blank_at is None:
                        blank_at = t
                    if last_seen is not None and t - last_seen >= self.mode["blank_grace"]:
                        self.finalize(current, last_seen, blank_at)
                        current, last_seen, blank_at = None, None, None
                previous_sample = t
                if count % 30 == 0:
                    print(f"Scanned {min(t, end):.1f}/{end:.1f}s; {len(self.entries)} cues found")
            if current is not None:
                last = last_seen if last_seen is not None else current.end
                self.finalize(current, last, min(end, max(last + .01, last + self.interval)))
        finally:
            cap.release()
        self.entries = self._merge_adjacent(self.entries)
        if self.mode["refine"]:
            print(f"Refining cue boundaries ({len(self.entries)} cues)...")
            self._refine(start, end)
        print(f"Scanned {count} frames at {self.sample_fps:g} sample FPS in {time.monotonic()-started:.1f}s; {len(self.entries)} cues found")
        return self.entries

    def _merge_adjacent(self, entries: list[Cue]) -> list[Cue]:
        if not entries:
            return []
        merged = [entries[0]]
        for cue in entries[1:]:
            prev = merged[-1]
            same_spot = (prev.center_x is None or cue.center_x is None or abs(prev.center_x-cue.center_x) <= max(18, (self.roi[2]-self.roi[0])*.12))
            same_spot &= (prev.center_y is None or cue.center_y is None or abs(prev.center_y-cue.center_y) <= max(12, (self.roi[3]-self.roi[1])*.12))
            gap = cue.start - prev.end
            if (similarity(prev.text, cue.text, LANGUAGES[self.args.language][2]) >= self.profile["event"]
                    and same_spot and gap <= min(.20, self.interval*.5)):
                prev.end = max(prev.end, cue.end)
                prev.end_low, prev.end_high = cue.end_low, cue.end_high
                prev.readings.extend(cue.readings)
                if prev.readings:
                    prev.text, prev.confidence = self.consensus(prev.readings)
            else:
                if cue.start < prev.end:
                    prev.end = max(prev.start+.05, cue.start-.01)
                merged.append(cue)
        return merged

    def _matches(self, cap: cv2.VideoCapture, seconds: float, text: str) -> bool:
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0, seconds)*1000)
        ok, frame = cap.read()
        if not ok:
            return False
        read = self.backend.read(upscale(crop(frame, self.roi)))
        return bool(read.text) and similarity(read.text, text, LANGUAGES[self.args.language][2]) >= self.profile["boundary"]

    def _refine(self, start: float, end: float) -> None:
        cap = cv2.VideoCapture(str(self.args.video))
        if not cap.isOpened():
            print("Could not reopen the video; keeping sampled cue boundaries.", file=sys.stderr)
            return
        try:
            for cue in self.entries:
                if cue.start_low is not None and cue.start_high is not None and cue.start_high > cue.start_low:
                    low, high = max(start, cue.start_low), min(end, cue.start_high)
                    for _ in range(self.mode["refine"]):
                        mid = (low+high)/2
                        if self._matches(cap, mid, cue.text):
                            high = mid
                        else:
                            low = mid
                    cue.start = high
                if cue.end_low is not None and cue.end_high is not None and cue.end_high > cue.end_low:
                    low, high = max(start, cue.end_low), min(end, cue.end_high)
                    for _ in range(self.mode["refine"]):
                        mid = (low+high)/2
                        if self._matches(cap, mid, cue.text):
                            low = mid
                        else:
                            high = mid
                    cue.end = max(cue.start+.05, high)
        finally:
            cap.release()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read burned-in subtitles from a video and write an SRT draft.")
    parser.add_argument("--video", type=Path, required=True, help="Input video path")
    parser.add_argument("--language", choices=sorted(LANGUAGES), required=True, help="Subtitle language")
    parser.add_argument("--mode", choices=sorted(MODE), default="balanced", help="fast samples 1 FPS; balanced samples 3 FPS and refines cue boundaries")
    parser.add_argument("--device", choices=("cpu", "gpu"), default="cpu", help="Inference device; GPU requires a compatible NVIDIA CUDA setup")
    parser.add_argument("--region", default="0,0.65,1,1", metavar="X1,Y1,X2,Y2", help="Normalized crop coordinates from 0 to 1; default is the bottom 35%%")
    parser.add_argument("--confidence", type=float, default=0.80, help="Minimum OCR confidence, from 0 to 1 (default: 0.80)")
    parser.add_argument("--color", choices=COLORS, default="white", help="Subtitle text color filter (default: white)")
    parser.add_argument("--centered", action=argparse.BooleanOptionalAction, default=True, help="Keep text near the horizontal center (default: on)")
    parser.add_argument("--start", type=float, default=0.0, help="Start scan time in seconds")
    parser.add_argument("--end", type=float, help="Optional end scan time in seconds")
    parser.add_argument("--output", type=Path, help="Output SRT path (default: alongside the video)")
    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    args.video = args.video.expanduser().resolve()
    if not args.video.is_file():
        parser.error(f"video does not exist: {args.video}")
    if not 0.0 <= args.confidence <= 1.0:
        parser.error("--confidence must be between 0 and 1")
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        parser.error("OpenCV could not open the input video or its codec")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 25.0)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    duration = frames / max(.001, fps)
    try:
        roi = parse_region(args.region, width, height)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    print(f"Video: {width}x{height}, {fps:.3f} source FPS, {duration:.2f}s")
    print(f"OCR: {args.language} / {LANGUAGES[args.language][1]} / {args.device}; mode: {args.mode} ({MODE[args.mode]['fps']:g} sample FPS)")
    print(f"Region pixels: x={roi[0]}..{roi[2]}, y={roi[1]}..{roi[3]}; confidence={args.confidence:.0%}; color={args.color}")
    try:
        backend = PaddleBackend(args.language, args.device, args.confidence, args.color, args.centered)
        cues = Extractor(args, backend, roi, fps, duration).extract()
        output = (args.output or args.video.with_suffix(".srt")).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for i, cue in enumerate(sorted(cues, key=lambda x: (x.start, x.end)), 1):
            text = clean_text(cue.text)
            if not text:
                continue
            lines.extend([str(i), f"{time_srt(cue.start)} --> {time_srt(max(cue.end, cue.start+.05))}", text, ""])
        output.write_text("\n".join(lines), encoding="utf-8-sig")
        print(f"Wrote {len(cues)} cues to {output}")
        return 0
    except Exception as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
