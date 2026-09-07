from fastapi import FastAPI, UploadFile, HTTPException, APIRouter
import app.inspectors.csv_inspector as csv_inspector
import app.inspectors.json_inspector as json_inspector
import app.inspectors.text_inspector as text_inspector
from app.models import InspectionResponse

app = FastAPI(
    title="File Inspection API",
    description="Upload CSV, JSON, and text files to inspect their contents and structure.",
    version="1.0.0",
)

api_v1 = APIRouter(prefix="/api/v1")

MAX_FILE_SIZE = 10 * 1024 * 1024

async def handle_upload(file: UploadFile):
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB."
        )
    if file.filename.lower().endswith(".csv"):
        result = await csv_inspector.inspect_csv(file)

        return result

    elif file.filename.lower().endswith(".json"):
        result = await json_inspector.inspect_json(file)

        return result
    elif file.filename.lower().endswith((".txt", ".md")):
       result = await text_inspector.inspect_text(file)

       return result
    else:    
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}"
        )

    
@api_v1.get("/health")
def read_root():
    return {"status": "ok"}

@api_v1.post("/uploadfile/", response_model=InspectionResponse)
async def create_upload_file(file: UploadFile):
    return await handle_upload(file)

app.include_router(api_v1)