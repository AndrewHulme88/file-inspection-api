# File Inspection API

A FastAPI service for uploading and inspecting data, configuration, spreadsheet, markup, and UTF-8 text files. It returns useful structural information such as tabular row and column counts, document shape, or text statistics.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or another Python environment manager

## Run locally

Install the project dependencies and start the development server:

```bash
uv sync --dev
uv run fastapi dev app/main.py
```

The API is then available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Endpoints

### `GET /api/v1/health`

Returns the service health status:

```json
{"status": "ok"}
```

### `POST /api/v1/uploadfile/`

Accepts a multipart form upload with a required `file` field. Supported filename extensions are `.csv`, `.tsv`, `.json`, `.ndjson`, `.jsonl`, `.yaml`, `.yml`, `.xml`, `.toml`, `.ini`, `.html`, `.htm`, `.xlsx`, `.xls`, `.ods`, `.parquet`, `.txt`, `.md`, and `.log`.

Uploads require an `X-API-Key` header. Its value is the configured `FILE_INSPECTION_API_KEY` (or `dev-local-key` when it is not configured).

```bash
curl -X POST http://127.0.0.1:8000/api/v1/uploadfile/ \
  -H "X-API-Key: dev-local-key" \
  -F "file=@sample.csv"
```

Files must be 10 MB or smaller and use UTF-8 encoding where applicable.

## Inspection results

Every successful result includes the uploaded filename, content type, and size in bytes.

| File type | Additional information returned |
| --- | --- |
| CSV | Row count, column count and names, missing-value total, duplicate-row total |
| TSV | Row count, column count and names, missing-value total, duplicate-row total |
| JSON object | JSON type, validity, top-level keys, and key count |
| JSON array of objects | JSON type, validity, row/column counts and names, missing-value and duplicate-row totals |
| Other valid JSON values | JSON type, validity, and the parsed value |
| NDJSON / JSONL | Row count, column count and names, missing-value total, duplicate-row total |
| YAML / YML | YAML type, validity, document count, and top-level keys for mapping documents |
| XML | Root tag, element count, maximum nesting depth, and validity |
| TOML | Validity, top-level keys, and key count |
| INI | Validity, section names and count, and setting count |
| HTML / HTM | Page title (when present), heading and link counts, text-character count, and validity |
| XLSX / XLS / ODS | Workbook sheet count plus per-sheet row/column counts and names, missing-value total, and duplicate-row total |
| Parquet | Row/column counts and names, column data types, missing-value total, and duplicate-row total |
| Text / Markdown / Log | Character, word, line, and empty-line counts; UTF-8 encoding |

For example, a CSV upload can return:

```json
{
  "filename": "sample.csv",
  "content_type": "text/csv",
  "size_bytes": 91,
  "rows": 3,
  "columns": 3,
  "column_names": ["name", "age", "email"],
  "missing_values": 1,
  "duplicate_rows": 2
}
```

## Errors

| Status | When it occurs |
| --- | --- |
| 400 | Unsupported extension, invalid UTF-8, malformed JSON/YAML/XML, or empty/unparseable CSV/TSV |
| 413 | Uploaded file exceeds 10 MB |
| 422 | The required `file` field is missing |

## Tests

Run the test suite with:

```bash
uv run pytest
```

The tests cover successful uploads plus invalid encodings, malformed content, unsupported files, missing uploads, and the upload-size limit.
