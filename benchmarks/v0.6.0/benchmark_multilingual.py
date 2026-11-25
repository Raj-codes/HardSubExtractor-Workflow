"""Manual OCR evaluation against generated fixtures or annotated real videos.

Run from the project root: python tests/benchmark_multilingual.py --synthetic --report diagnostics/multilingual.json
Real manifest: [{"language": "English", "video": "clip.mp4", "roi": [0, 234, 640, 360],
                 "cues": [{"start": 0.5, "end": 1.2, "text": "Hello"}]}]
Video paths are relative to the manifest. Generated text uses Windows GDI for
proper Arabic/Indic shaping; no screenshot or user desktop access is involved.
"""
from __future__ import annotations

import argparse
import ctypes as ct
import gc
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version as package_version

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hard_sub_extractor import APP_VERSION, EXPERIMENTAL_OCR_LANGUAGES, LANGUAGES, MODE_CONFIGS, V6_LANGUAGE_CODES, PaddleOCRBackend, SubtitleExtractor, comparison_text


SAMPLES = {
    "English": ("We will leave tomorrow", "We will leave tonight", "Wait for me", "Arial"),
    "German": ("Wir fahren morgen nach Hause", "Wir fahren heute nach Hause", "Warte auf mich", "Arial"),
    "French": ("Nous partons demain matin", "Nous partons demain soir", "Attends moi ici", "Arial"),
    "Spanish": ("Nos vamos mañana temprano", "Nos vamos mañana tarde", "Espera un momento", "Arial"),
    "Italian": ("Partiamo domani mattina", "Partiamo domani sera", "Aspettami qui", "Arial"),
    "Portuguese": ("Vamos sair amanhã cedo", "Vamos sair amanhã à noite", "Espere por mim", "Arial"),
    "Dutch": ("We vertrekken morgen vroeg", "We vertrekken morgen laat", "Wacht op mij", "Arial"),
    "Japanese": ("明日の朝に出発します", "明日の夜に出発します", "少し待ってください", "Yu Gothic"),
    "Korean": ("우리는 내일 아침에 떠나요", "우리는 내일 저녁에 떠나요", "잠시만 기다려 주세요", "Malgun Gothic"),
    "Chinese (Simplified)": ("我们明天早上出发", "我们明天晚上出发", "请等我一下", "Microsoft YaHei"),
    "Chinese (Traditional)": ("我們明天早上出發", "我們明天晚上出發", "請等我一下", "Microsoft JhengHei"),
    "Russian": ("Мы уезжаем завтра утром", "Мы уезжаем завтра вечером", "Подожди меня здесь", "Arial"),
    "Ukrainian": ("Ми їдемо завтра вранці", "Ми їдемо завтра ввечері", "Зачекай на мене", "Arial"),
    "Indonesian": ("Kita berangkat besok pagi", "Kita berangkat besok malam", "Tunggu sebentar", "Arial"),
    "Malay": ("Kita bertolak esok pagi", "Kita bertolak esok malam", "Tunggu saya di sini", "Arial"),
    "Filipino": ("Aalis tayo bukas ng umaga", "Aalis tayo bukas ng gabi", "Hintayin mo ako", "Arial"),
    "Polish": ("Wyjeżdżamy jutro rano", "Wyjeżdżamy jutro wieczorem", "Poczekaj na mnie", "Arial"),
    "Swedish": ("Vi åker i morgon bitti", "Vi åker i morgon kväll", "Vänta på mig", "Arial"),
}


def render_text(text, font_name, rtl=False):
    if os.name != "nt":
        raise RuntimeError("Synthetic text rendering requires Windows; use --manifest on other platforms.")
    class Header(ct.Structure):
        _fields_ = [("size", ct.c_uint32), ("width", ct.c_int32), ("height", ct.c_int32),
                    ("planes", ct.c_uint16), ("bits", ct.c_uint16), ("compression", ct.c_uint32),
                    ("image_size", ct.c_uint32), ("xppm", ct.c_int32), ("yppm", ct.c_int32),
                    ("used", ct.c_uint32), ("important", ct.c_uint32)]
    class Info(ct.Structure):
        _fields_ = [("header", Header), ("colors", ct.c_uint32 * 3)]
    class Rect(ct.Structure):
        _fields_ = [(name, ct.c_int32) for name in ("left", "top", "right", "bottom")]
    gdi, user = ct.WinDLL("gdi32"), ct.WinDLL("user32")
    gdi.CreateCompatibleDC.argtypes = [ct.c_void_p]; gdi.CreateCompatibleDC.restype = ct.c_void_p
    gdi.CreateDIBSection.argtypes = [ct.c_void_p, ct.POINTER(Info), ct.c_uint, ct.POINTER(ct.c_void_p), ct.c_void_p, ct.c_uint]
    gdi.CreateDIBSection.restype = ct.c_void_p
    gdi.SelectObject.argtypes = [ct.c_void_p, ct.c_void_p]; gdi.SelectObject.restype = ct.c_void_p
    gdi.CreateFontW.argtypes = [ct.c_int] * 5 + [ct.c_uint] * 8 + [ct.c_wchar_p]
    gdi.CreateFontW.restype = ct.c_void_p
    gdi.SetTextColor.argtypes = [ct.c_void_p, ct.c_uint32]
    gdi.SetBkMode.argtypes = [ct.c_void_p, ct.c_int]
    gdi.DeleteObject.argtypes = [ct.c_void_p]; gdi.DeleteDC.argtypes = [ct.c_void_p]
    user.DrawTextW.argtypes = [ct.c_void_p, ct.c_wchar_p, ct.c_int, ct.POINTER(Rect), ct.c_uint]
    dc = gdi.CreateCompatibleDC(None)
    info = Info(Header(40, 960, -540, 1, 32, 0, 0, 0, 0, 0, 0))
    bits = ct.c_void_p()
    bitmap = gdi.CreateDIBSection(dc, ct.byref(info), 0, ct.byref(bits), None, 0)
    if not bitmap or not bits.value:
        raise RuntimeError("Could not allocate fixture bitmap")
    old_bitmap = gdi.SelectObject(dc, bitmap)
    pixels = np.ctypeslib.as_array((ct.c_uint8 * (960 * 540 * 4)).from_address(bits.value)).reshape(540, 960, 4)
    pixels[:, :, :] = 26
    font = gdi.CreateFontW(-36, 0, 0, 0, 500, 0, 0, 0, 1, 0, 0, 4, 0, font_name)
    old_font = gdi.SelectObject(dc, font)
    try:
        gdi.SetBkMode(dc, 1); gdi.SetTextColor(dc, 0xFFFFFF)
        rect = Rect(10, 426, 950, 510)
        user.DrawTextW(dc, text, -1, ct.byref(rect), 0x1 | 0x4 | 0x20 | 0x800 | (0x20000 if rtl else 0))
        return pixels[:, :, :3].copy()
    finally:
        gdi.SelectObject(dc, old_font); gdi.SelectObject(dc, old_bitmap)
        gdi.DeleteObject(font); gdi.DeleteObject(bitmap); gdi.DeleteDC(dc)


def synthetic_jobs(directory, languages, stress=False):
    for name in languages:
        a, b, repeat, font = SAMPLES[name]
        cues = [dict(start=.23, end=.53, text=a), dict(start=.60, end=1.20, text=b),
                dict(start=1.53, end=2.10, text=repeat), dict(start=2.50, end=3.10, text=repeat)]
        images = {text: render_text(text, font, LANGUAGES[name] == "ar") for text in (a, b, repeat)}
        for case in (("clear", "moving_compressed") if stress else ("clear",)):
            video = str(directory / (LANGUAGES[name] + case + ".avi"))
            writer = cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*"MJPG"), 30, (960, 540))
            if not writer.isOpened():
                raise RuntimeError("Could not open fixture video writer")
            x = np.arange(960, dtype=np.float32)[None, :]
            y = np.arange(540, dtype=np.float32)[:, None]
            for i in range(108):
                cue = next((c for c in cues if c["start"] <= i / 30 < c["end"]), None)
                frame = images[cue["text"]] if cue else np.full((540, 960, 3), 26, np.uint8)
                if case != "clear":
                    background = (38 + 15 * np.sin((x+i*4)/28) + 9*np.cos((y-i*2)/17))[:, :, None]
                    alpha = np.maximum(0, frame.astype(np.float32) - 26) / 229
                    fade = min(1.0, (i/30-cue["start"] + .033)/.10) if cue else 0
                    frame = np.clip(background*(1-alpha*fade) + 210*alpha*fade, 0, 255).astype(np.uint8)
                    frame = cv2.resize(cv2.resize(frame, (640, 360), interpolation=cv2.INTER_AREA), (960, 540))
                writer.write(frame)
            writer.release()
            yield dict(language=name, case=case, video=video, roi=[0, 350, 960, 540], cues=cues)


def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        nxt = [i]
        for j, cb in enumerate(b, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j-1] + (ca != cb)))
        row = nxt
    return row[-1]


def evaluate(cues, entries):
    pairs = []
    for i, cue in enumerate(cues):
        for j, entry in enumerate(entries):
            overlap = max(0, min(cue["end"], entry.end) - max(cue["start"], entry.start))
            if overlap / max(.01, cue["end"] - cue["start"]) >= .30:
                a, b = comparison_text(cue["text"]), comparison_text(entry.text)
                similarity = max(0, 1 - edit_distance(a, b) / max(1, len(a), len(b)))
                pairs.append((similarity, overlap, i, j))
    matched, used, correct, exact = set(), set(), 0, 0
    start_errors, end_errors = [], []
    for similarity, overlap, i, j in sorted(pairs, reverse=True):
        if i in matched or j in used:
            continue
        matched.add(i); used.add(j)
        correct += similarity >= .95
        exact += similarity == 1.0
        start_errors.append(abs(cues[i]["start"] - entries[j].start))
        end_errors.append(abs(cues[i]["end"] - entries[j].end))
    return dict(expected_cues=len(cues), detected_cues=len(matched),
                text_correct_cues=correct, exact_text_cues=exact, extra_cues=len(entries) - len(used),
                mean_start_error_seconds=(sum(start_errors) / len(start_errors) if start_errors else None),
                mean_end_error_seconds=(sum(end_errors) / len(end_errors) if end_errors else None),
                median_start_error_seconds=(float(np.median(start_errors)) if start_errors else None),
                median_end_error_seconds=(float(np.median(end_errors)) if end_errors else None),
                boundaries_within_0_5_seconds=(sum(a <= .5 and b <= .5 for a, b in zip(start_errors, end_errors)) if start_errors else 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--synthetic", action="store_true")
    source.add_argument("--manifest", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--device", choices=("cpu", "gpu"), default="gpu")
    parser.add_argument("--mode", choices=("Fast", "Balanced"), default="Fast")
    parser.add_argument("--stress", action="store_true", help="Add moving-background, faded, downscaled subtitle fixtures")
    parser.add_argument("--include-experimental", action="store_true", help="Include experimental options in generated tests and in the quality gate")
    parser.add_argument("--languages", nargs="*", choices=list(LANGUAGES))
    args = parser.parse_args()
    report = dict(app_version=APP_VERSION,
                  scope=("synthetic clear plus moving/compressed/fading horizontal subtitles" if args.stress else "synthetic clear, white, horizontal subtitles") if args.synthetic else "annotated video corpus",
                  mode=args.mode, target_sample_fps=MODE_CONFIGS[args.mode].sample_fps, device=args.device,
                  settings={"confidence_threshold": 0.80, "subtitle_filter": True, "center_filter": True,
                            "text_color": "White", "roi": "fixture bottom region"}, results=[])
    report["confidence_threshold"] = .80
    report["excluded_experimental_languages"] = sorted(EXPERIMENTAL_OCR_LANGUAGES) if args.synthetic and not args.include_experimental and not args.languages else []
    report["source_sha256"] = hashlib.sha256((Path(__file__).resolve().parents[1] / "hard_sub_extractor.py").read_bytes()).hexdigest()
    report["dependencies"] = {name: package_version(name) for name in ("paddleocr", "paddlex")}
    for name in ("onnxruntime-gpu", "onnxruntime"):
        try:
            report["dependencies"][name] = package_version(name)
        except PackageNotFoundError:
            pass
    from paddleocr import PaddleOCR
    resolver = object.__new__(PaddleOCR)
    backend, active_models = None, None
    with tempfile.TemporaryDirectory() as td:
        languages = args.languages or [name for name in LANGUAGES if args.include_experimental or name not in EXPERIMENTAL_OCR_LANGUAGES]
        jobs = synthetic_jobs(Path(td), languages, args.stress) if args.synthetic else json.loads(args.manifest.read_text(encoding="utf-8"))
        for job in jobs:
            name = job["language"]
            if args.languages and name not in args.languages:
                continue
            code = LANGUAGES[name]
            version = "PP-OCRv6" if code in V6_LANGUAGE_CODES else "PP-OCRv5"
            models = resolver._get_ocr_model_names(code, version)
            result = dict(language=name, case=job.get("case", "real"), models=models, expected=job["cues"])
            total_started = time.monotonic()
            model_init_seconds = 0.0
            try:
                if active_models != models:
                    backend = None; gc.collect()
                    model_started = time.monotonic()
                    backend = PaddleOCRBackend(language=code, device=args.device)
                    model_init_seconds = time.monotonic() - model_started
                    active_models = models
                backend.language = code
                pipeline = backend._ocr.paddlex_pipeline
                result["providers"] = {key: getattr(pipeline, key).runner.session.get_providers() for key in ("text_det_model", "text_rec_model")}
                video = Path(job["video"])
                if not args.synthetic and not video.is_absolute():
                    video = args.manifest.resolve().parent / video
                extractor = SubtitleExtractor(str(video), tuple(job["roi"]), backend, mode=args.mode)
                extraction_started = time.monotonic()
                entries = extractor.extract()
                result["elapsed_seconds"] = round(time.monotonic() - extraction_started, 3)
                result.update(evaluate(job["cues"], entries))
                result["entries"] = [dict(start=e.start, end=e.end, text=e.text, confidence=e.confidence) for e in entries]
                result["scan"] = extractor.stats
            except Exception as exc:
                result.update(error=str(exc), expected_cues=len(job["cues"]), detected_cues=0, text_correct_cues=0, exact_text_cues=0, extra_cues=0)
                backend, active_models = None, None
            result["model_initialization_seconds"] = round(model_init_seconds, 3)
            result["total_seconds_including_model_initialization"] = round(time.monotonic() - total_started, 3)
            result.setdefault("elapsed_seconds", 0.0)
            report["results"].append(result)
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{name}: {result['detected_cues']}/{result['expected_cues']} cues; {result['text_correct_cues']} text correct; {result.get('error', '')}", flush=True)
    total = {key: sum(r[key] for r in report["results"]) for key in ("expected_cues", "detected_cues", "text_correct_cues", "exact_text_cues", "extra_cues")}
    total["cue_recall"] = total["detected_cues"] / max(1, total["expected_cues"])
    total["text_correct_rate"] = total["text_correct_cues"] / max(1, total["expected_cues"])
    total["exact_text_rate"] = total["exact_text_cues"] / max(1, total["expected_cues"])
    total["cue_precision"] = total["detected_cues"] / max(1, total["detected_cues"] + total["extra_cues"])
    report["totals"] = total
    report["meets_95_percent_cue_target_on_this_corpus"] = total["cue_recall"] >= .95 and all(r["detected_cues"] / max(1, r["expected_cues"]) >= .95 for r in report["results"])
    report["meets_95_percent_text_target_on_this_corpus"] = total["text_correct_rate"] >= .95 and all(r["text_correct_cues"] / max(1, r["expected_cues"]) >= .95 for r in report["results"])
    report["meets_95_percent_precision_target_on_this_corpus"] = total["cue_precision"] >= .95 and all(r["detected_cues"] / max(1, r["detected_cues"] + r["extra_cues"]) >= .95 for r in report["results"])
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(total), flush=True)
    return 0 if all(report[key] for key in report if key.startswith("meets_95_percent_")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
