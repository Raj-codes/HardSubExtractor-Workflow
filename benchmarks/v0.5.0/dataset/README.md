# v0.5.0 benchmark dataset and curation

This is the metadata and curation record for the synthetic subtitle dataset used in the v0.5.0 pipeline benchmark. The original video and rendered MP4 clips are not included; the manifest preserves labels, timings, intended settings, file sizes, and SHA-256 hashes for auditing the reported cases.

## Dataset summary

- 50 clips for each of the app's 23 OCR options: 1,150 cases.
- Six labelled subtitle cues per clip: 6,900 reference cues. Across 2,500 successful OCR runs, this is 15,000 run-level cue instances.
- One 320×240 source at 15 FPS, about 18.93 seconds; subtitles appear in the bottom 35%. The source video and generated variations were not modified or included in this repository.
- Most cues last 1.4–2.6 seconds; occasional stress cues last about 0.53 or 0.8 seconds. Seven hand-authored phrase patterns are varied with punctuation, numbers and styling, yielding 117 exact label strings per language.
- 782 white clips, 184 yellow and 184 cyan; text sizes 12–23 pixels, regular/bold weights, 0–2 pixel black outlines, and language-appropriate font families.
- OCR settings: 80% minimum confidence, subtitle-specific and centered filters on, GPU inference configured, bottom 35% region. White cases use the White color filter; colored cases use Any color.

## Files

- `manifest.jsonl`: one complete case record per line, including cue text/times, styling, settings, relative clip/ground-truth names and SHA-256 hashes.
- `index.csv`: Excel-readable case index with settings, audit status, file sizes and hashes.
- `source.json`: source clip geometry, frame rate, duration, SHA-256 and original filename; the local path is intentionally removed.
- `coverage.json`, `curation_summary.json`, and `glyph_coverage.json`: dataset and font-character-map audits.
- `style_preview.png`: representative font, weight, outline and color samples.

## Curation checks

All generated clips were opened and all 284 frames decoded. Audits checked dimensions, frame rate, cue timing, JSON/SRT/SQLite agreement, intended OCR settings, and the rendered text overlay at each cue midpoint. All 6,900 midpoint checks showed a positive overlay signal. The primary Windows font faces were checked for requested-character coverage; this does not verify translation quality, shaping, fallback behavior, or subjective legibility.

## Limitations

This is a controlled, single-background, low-resolution stress set, not a representative sample of natural footage. It does not cover varied codecs/scenes, vertical subtitles, karaoke, complex two-line captions, or varied subtitle rendering. The source video and generation scripts are not included in this archive.
