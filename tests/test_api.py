import pytest
from fastapi.testclient import TestClient
from app.main import app
import app.main as main
import io
import pandas as pd

client = TestClient(app)
API_HEADERS = {"X-API-Key": "your-dev-key"}

@pytest.fixture(autouse=True)
def reset_rate_limit():
    main.request_timestamps.clear()
    original_limit = main.RATE_LIMIT_REQUESTS
    main.RATE_LIMIT_REQUESTS = 1000

    try:
        yield
    finally:
        main.request_timestamps.clear()
        main.RATE_LIMIT_REQUESTS = original_limit

def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_missing_api_key():
    response = client.post(
        "/api/v1/uploadfile/",
        files={
            "file": (
                "test.json",
                b'{"name": "Alice", "age", 30}',
                "application/json",
            )
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"

def test_invalid_api_key():
    response = client.post(
        "/api/v1/uploadfile/",
        headers={"X-API-Key": "wrong-key"},
        files={
            "file": (
                "test.json",
                b'{"name": "Alice", "age": 30}',
                "application/json",
            )
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"

def test_valid_json_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "test.json",
                b'{"name": "Alice", "age": 30}',
                "application/json",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["json_type"] == "dict"
    assert response.json()["key_count"] == 2

def test_invalid_json_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "invalid.json",
                b'{"name": "Alice",}',
                "application/json",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The uploaded file is not valid UTF-8 JSON"}

def test_unsupported_file_type():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "program.exe",
                b"not supported",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported file type: program.exe"}

def test_valid_csv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "sample.csv",
                b"name,age,email\nAlice,30,alice@example.com\nBob,,bob@example.com\nAlice,30,alice@example.com\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["rows"] == 3
    assert response.json()["columns"] == 3
    assert response.json()["missing_values"] == 1
    assert response.json()["duplicate_rows"] == 2

def test_valid_text_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "sample.txt",
                b"Hello world\n\nThis is a text file.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "text"
    assert response.json()["words"] == 7
    assert response.json()["lines"] == 3
    assert response.json()["empty_lines"] == 1

def test_empty_csv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The CSV file is empty"}

def test_missing_file():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
    )
    
    assert response.status_code == 422

def test_file_too_large():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "large.txt",
                b"x" * (10 * 1024 * 1024 + 1),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "File is too large. Maximum size is 10 MB."}

def test_malformed_csv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "malformed.csv",
                b'name,email\n"Alice,alice@example.com\n',
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The CSV file could not be parsed"}

def test_invalid_utf8_csv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "invalid.csv",
                b"\xff\xfe\xfd",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The CSV file is not valid UTF-8 text"}

def test_invalid_utf8_json_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "invalid.json",
                b"\xff\xfe\xfd",
                "application/json",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The uploaded file is not valid UTF-8 JSON"}

def test_invalid_utf8_text_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfd",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The file is not valid UTF-8 text"}

def test_valid_tsv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "sample.tsv",
                b"name\tage\nAlice\t30\nBob\t\nAlice\t30\n",
                "text/tab-separated-values",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "tsv"
    assert response.json()["rows"] == 3
    assert response.json()["columns"] == 2
    assert response.json()["missing_values"] == 1
    assert response.json()["duplicate_rows"] == 2

@pytest.mark.parametrize("filename", ["sample.yaml", "sample.yml"])
def test_valid_yaml_upload(filename):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                filename,
                b"name: Alice\nage: 30\n",
                "application/yaml",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "yaml"
    assert response.json()["yaml_type"] == "dict"
    assert response.json()["key_count"] == 2

def test_valid_xml_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "sample.xml",
                b"<catalog><book><title>Example</title></book></catalog>",
                "application/xml",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "xml"
    assert response.json()["root_tag"] == "catalog"
    assert response.json()["element_count"] == 3
    assert response.json()["max_depth"] == 3
    assert response.json()["valid"] is True

def test_malformed_tsv_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "malformed.tsv",
                b'name\tage\n"Alice\t30\n',
                "text/tab-separated-values",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The TSV file could not be parsed"}

def test_malformed_yaml_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": ("malformed.yaml", b"name: [Alice\n", "application/yaml")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The YAML file could not be parsed"}

def test_malformed_xml_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": ("malformed.xml", b"<catalog><book></catalog>", "application/xml")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "The XML file could not be parsed"}

@pytest.mark.parametrize(
    ("filename", "content_type", "detail"),
    [
        ("invalid.yaml", "application/yaml", "The uploaded file is not valid UTF-8 YAML"),
        ("invalid.xml", "application/xml", "The XML file is not valid UTF-8 text"),
    ],
)
def test_invalid_utf8_yaml_and_xml_upload(filename, content_type, detail):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": (filename, b"\xff\xfe\xfd", content_type)},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": detail}

@pytest.mark.parametrize("filename", ["program.exe", "archive.zip"])
def test_unsupported_file_extensions_return_400(filename):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": (filename, b"not supported", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": f"Unsupported file type: {filename}"}

@pytest.mark.parametrize("filename", ["events.ndjson", "events.jsonl"])
def test_valid_ndjson_upload(filename):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                filename,
                b'{"event":"login","user":"alice"}\n{"event":"login","user":"bob"}\n',
                "application/x-ndjson",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "ndjson"
    assert response.json()["rows"] == 2
    assert response.json()["column_names"] == ["event", "user"]

def test_valid_excel_upload():
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(
            {"name": ["Alice", "Bob"], "age": [30, None]}
        ).to_excel(writer, sheet_name="People", index=False)

        pd.DataFrame(
            {"event": ["login"]}
        ).to_excel(writer, sheet_name="Events", index=False)

    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "report.xlsx",
                output.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "xlsx"
    assert body["sheet_count"] == 2
    assert body["sheets"][0]["name"] == "People"
    assert body["sheets"][0]["rows"] == 2

def test_valid_parquet_upload():
    dataframe = pd.DataFrame(
        {"name": ["Alice", "Bob"], "age": [30, None]}
    )
    output = io.BytesIO()
    dataframe.to_parquet(output, engine="pyarrow", index=False)

    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "people.parquet",
                output.getvalue(),
                "application/vnd.apache.parquet",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "parquet"
    assert body["rows"] == 2
    assert body["column_types"]["name"] in {"object", "str"}


def test_valid_toml_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "settings.toml",
                b'title = "File Inspector"\n[database]\nhost = "localhost"\n',
                "application/toml",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "toml"
    assert response.json()["keys"] == ["title", "database"]
    assert response.json()["key_count"] == 2


def test_valid_ini_upload():
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={
            "file": (
                "settings.ini",
                b"[database]\nhost = localhost\nport = 5432\n[logging]\nlevel = INFO\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "settings.ini"
    assert body["file_type"] == "ini"
    assert body["sections"] == ["database", "logging"]
    assert body["setting_count"] == 3


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        (
            "page.html",
            b"<html><head><title>Example</title></head><body><h1>Hello</h1><a href='/about'>About</a></body></html>",
        ),
        ("fragment.htm", b"<main><h2>Untitled</h2></main>"),
    ],
)
def test_valid_html_upload(filename, contents):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": (filename, contents, "text/html")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["file_type"] == "html"
    assert body["heading_count"] == 1
    if filename == "page.html":
        assert body["title"] == "Example"
        assert body["link_count"] == 1
    else:
        assert body["title"] is None


@pytest.mark.parametrize("filename", ["notes.log", "notes.md"])
def test_text_file_extension_aliases(filename):
    response = client.post(
        "/api/v1/uploadfile/",
        headers=API_HEADERS,
        files={"file": (filename, b"A short note.", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["file_type"] == "text"
