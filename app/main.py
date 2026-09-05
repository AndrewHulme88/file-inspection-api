from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import inspectors.csv_inspector as csv_inspector
import inspectors.json_inspector as json_inspector
import inspectors.text_inspector as text_inspector

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

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
        return {"filename": file.filename, "content_type": file.content_type, "size_bytes": file.size}