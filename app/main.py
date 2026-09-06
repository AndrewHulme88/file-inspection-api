from fastapi import FastAPI, UploadFile, HTTPException
import app.inspectors.csv_inspector as csv_inspector
import app.inspectors.json_inspector as json_inspector
import app.inspectors.text_inspector as text_inspector

app = FastAPI(
    title="File Inspection API",
    description="Upload CSV, JSON, and text files to inspect their contents and structure.",
    version="1.0.0",
)

MAX_FILE_SIZE = 10 * 1024 * 1024

@app.get("/health")
def read_root():
    return {"Hello": "World"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
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