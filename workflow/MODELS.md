# OCR models and language mapping

The script configures PaddleOCR with ONNX Runtime. PaddleOCR/PaddleX downloads the needed model files on the first run and caches them locally. In normal use, you do not download model archives by hand.

| Workflow language | PaddleOCR code | Model family | Pipeline group |
| --- | --- | --- | --- |
| English | `en` | PP-OCRv6 | Latin |
| German | `de` | PP-OCRv6 | Latin |
| French | `fr` | PP-OCRv6 | Latin |
| Spanish | `es` | PP-OCRv6 | Latin |
| Italian | `it` | PP-OCRv6 | Latin |
| Portuguese | `pt` | PP-OCRv6 | Latin |
| Dutch | `nl` | PP-OCRv6 | Latin |
| Indonesian | `id` | PP-OCRv6 | Latin |
| Malay | `ms` | PP-OCRv6 | Latin |
| Filipino / Tagalog | `tl` | PP-OCRv6 | Latin |
| Polish | `pl` | PP-OCRv6 | Latin |
| Swedish | `sv` | PP-OCRv6 | Latin |
| Chinese, Simplified | `ch` | PP-OCRv6 | CJK |
| Chinese, Traditional | `chinese_cht` | PP-OCRv6 | CJK |
| Japanese | `japan` | PP-OCRv6 | CJK |
| Korean | `korean` | PP-OCRv5 | Hangul |
| Russian | `ru` | PP-OCRv5 | Cyrillic |
| Ukrainian | `uk` | PP-OCRv5 | Cyrillic |

The script selects PP-OCRv6 for the 15 language codes listed above and PP-OCRv5 for Korean, Russian, and Ukrainian. It uses PP-OCRv6 medium detection and recognition for the first group. The PP-OCRv5 language-specific setups use the server detector with the Korean recognizer or East Slavic recognizer. PaddleOCR initializes and downloads the detector and recognizer for the selected language.

## Model files

These are the inference archives used by the configured model families. The command-line workflow normally downloads them through PaddleOCR/PaddleX and you do not need to unpack these links yourself.

| Model | Use | Download |
| --- | --- | --- |
| `PP-OCRv6_medium_det` | Text detection for PP-OCRv6 languages | [inference archive](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv6_medium_det_infer.tar) |
| `PP-OCRv6_medium_rec` | Text recognition for PP-OCRv6 languages | [inference archive](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv6_medium_rec_infer.tar) |
| `PP-OCRv5_server_det` | Text detection for PP-OCRv5 languages | [inference archive](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_server_det_infer.tar) |
| `korean_PP-OCRv5_mobile_rec` | Korean recognition | [inference archive](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/korean_PP-OCRv5_mobile_rec_infer.tar) |
| `eslav_PP-OCRv5_mobile_rec` | Russian and Ukrainian recognition | [inference archive](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/eslav_PP-OCRv5_mobile_rec_infer.tar) |

## Official references

- [PaddleOCR 3.x model list](https://www.paddleocr.ai/main/en/version3.x/model_list.html) — inference model links for detection and recognition.
- [PP-OCRv6 recognition model details](https://www.paddleocr.ai/main/en/version3.x/module_usage/text_recognition.html) — the v6 medium/small/tiny model information and supported languages.
- [PP-OCRv5 multilingual recognition](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.html) — language codes and model families, including Korean and East Slavic.
- [PaddleOCR source and license](https://github.com/PaddlePaddle/PaddleOCR) — software source and license file.
- [ONNX Runtime CUDA provider](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html) — supported NVIDIA runtime combinations.

The model list can change upstream. Check the official model page for current downloads and each artifact's terms before redistributing model files. This repository does not include model weights.
