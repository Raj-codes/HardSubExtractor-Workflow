# Raw benchmark artifacts

- `predicted-srt.zip` contains the OCR-generated SRT for every completed clip and mode. Paths inside the archive begin with the language slug.
- `run-logs.zip` contains the generation, audit, model and report logs. Workstation paths and the local user-profile path were redacted.
- `../results.sqlite3` is the sanitized structured database with case labels, curation audit records and all 2,500 extraction runs.

The original benchmark MP4s are not included. Ground-truth text and timing are retained in the dataset manifest and structured database.
