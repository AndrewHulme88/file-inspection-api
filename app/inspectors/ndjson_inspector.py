import json
import pandas as pd
from fastapi import HTTPException

async def inspect_ndjson(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The NDJSON file is not valid UTF-8 text",
        )

    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        try:
            value =  json.loads(line)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"The NDJSON file must contain JSON objects; line {line_number}",
            )

        if not isinstance(value, dict):
            raise HTTPException(
                status_code=400,
                detail=f"The NDJSON file must contain JSON objects; line {line_number} does not",
            )

        rows.append(value)

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="The NDJSON file is empty",
        )

    df = pd.DataFrame(rows)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "ndjson",
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated(keep=False).sum()),
    }