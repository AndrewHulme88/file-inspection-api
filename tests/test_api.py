from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_valid_json_upload():
    response = client.post(
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
    response = client.post("/uploadfile/")

    assert response.status_code == 422

def test_file_too_large():
    response = client.post(
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
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
        "/uploadfile/",
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfd",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["error"] == "The file is not valid UTF-8 text"