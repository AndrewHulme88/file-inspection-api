import csv
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from io import StringIO

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
    if file.filename.endswith(".csv"):
        # Read file contents asynchronously
        contents = await file.read()
        buffer = StringIO(contents.decode("utf-8"))
        # Load bytes into Pandas DataFrame
        df = pd.read_csv(io.BytesIO(contents))
        # Find missing/null values per column
        missing_counts = df.isnull().sum().to_dict()
        total_missing = int(df.isnull().sum().sum())
        # Use DictReader to parse and extract headers
        reader = csv.DictReader(buffer)
        rows = [row for row in reader]
        columns = reader.fieldnames
        # Identify duplicate rows
        duplicate_mask = df.duplicated(keep=False)
        duplicate_df = df[duplicate_mask]
        # Optional clean up
        buffer.close()

        return {"filename": file.filename, "content_type": file.content_type, "size_bytes": file.size, "rows": len(rows), "columns": len(columns), "column_names": columns, "missing_values": total_missing, "duplicate_rows": len(duplicate_df)}
    else:    
        return {"filename": file.filename, "content_type": file.content_type, "size_bytes": file.size}