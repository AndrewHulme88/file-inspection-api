import os
import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import FastAPI, UploadFile, HTTPException, APIRouter, Depends, Header, status, Request
import app.inspectors.csv_inspector as csv_inspector
import app.inspectors.json_inspector as json_inspector
import app.inspectors.text_inspector as text_inspector
import app.inspectors.tsv_inspector as tsv_inspector
import app.inspectors.yaml_inspector as yaml_inspector
import app.inspectors.xml_inspector as xml_inspector
import app.inspectors.ndjson_inspector as ndjson_inspector
import app.inspectors.excel_inspector as excel_inspector

from app.models import InspectionResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="File Inspection API",
    description="Upload CSV, JSON, and text files to inspect their contents and structure.",
    version="1.0.0",
)

api_v1 = APIRouter(prefix="/api/v1")

MAX_FILE_SIZE = 10 * 1024 * 1024
API_KEY = os.getenv("FILE_INSPECTION_API_KEY", "dev-local-key")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

request_timestamps: dict[str, Deque[float]] = defaultdict(deque)

def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-KEY")):
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return x_api_key

def get_client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def rate_limit_dependency(request: Request):
    rate_limit(request)
    return None

def rate_limit(request):
    client_ip = get_client_ip(request)
    now = time.monotonic()
    timestamps = request_timestamps[client_ip]

    while timestamps and now - timestamps[0] > RATE_LIMIT_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )

    timestamps.append(now)

async def handle_upload(file: UploadFile):
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB."
        )

    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="Missing file name",
        )

    filename = file.filename.lower()
    
    if filename.endswith(".csv"):
        return await csv_inspector.inspect_csv(file)

    if filename.endswith(".json"):
        return await json_inspector.inspect_json(file)

    if filename.endswith((".txt", ".md")):
       return await text_inspector.inspect_text(file)

    if filename.endswith(".tsv"):
        return await tsv_inspector.inspect_tsv(file)

    if filename.endswith((".yaml", ".yml")):
        return await yaml_inspector.inspect_yaml(file)

    if filename.endswith(".xml"):
        return await xml_inspector.inspect_xml(file)

    if filename.endswith((".ndjson", ".jsonl")):
        return await ndjson_inspector.inspect_ndjson(file)

    if filename.endswith(".xlsx"):
        return await excel_inspector.inspect_excel(file)

    else:    
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}"
        )

    
@api_v1.get("/health")
def read_root():
    return {"status": "ok"}

@api_v1.post("/uploadfile/", response_model=InspectionResponse)
async def create_upload_file(
    file: UploadFile,
    _: str = Depends(require_api_key),
    __: None = Depends(rate_limit_dependency),
):
    # request dependency is just a placeholder; you can wire the limiter into a real dependency
    return await handle_upload(file)

app.include_router(api_v1)