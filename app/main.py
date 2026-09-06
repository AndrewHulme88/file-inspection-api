from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
import inspectors.csv_inspector as csv_inspector
import inspectors.json_inspector as json_inspector
import inspectors.text_inspector as text_inspector

app = FastAPI()

@app.get("/health")
def read_root():
    return {"Hello": "World"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
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