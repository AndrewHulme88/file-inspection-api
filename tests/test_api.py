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