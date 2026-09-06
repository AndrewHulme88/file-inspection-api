import json
import pandas as pd
from fastapi import HTTPException

async def inspect_json(file):
    contents = await file.read()

    try:
        data = json.loads(contents.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not valid UTF-8 JSON",
        )

    response = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "json_type": type(data).__name__,
        "valid": True
    }

    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        df = pd.DataFrame(data)

        response.update({
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated(keep=False).sum())
        })
    elif isinstance(data, dict):
        response.update({
            "keys": list(data.keys()),
            "key_count": len(data)
        })
    else:
        response["value"] = data

    return response