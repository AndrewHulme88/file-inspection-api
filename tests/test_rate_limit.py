from fastapi.testclient import TestClient
from app.main import app
import app.main as main

client = TestClient(app)
API_HEADERS = {"X-API-Key": "your-dev-key"}

def test_rate_limit_upload():
    main.request_timestamps.clear()
    original_limit = main.RATE_LIMIT_REQUESTS
    main.RATE_LIMIT_REQUESTS = 1

    try:
        first = client.post(
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
        second = client.post(
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

        assert first.status_code == 200
        assert second.status_code == 429
        assert second.json()["detail"] == "Rate limit exceeded. Try again later."
    finally:
        main.request_timestamps.clear()
        main.RATE_LIMIT_REQUESTS = original_limit