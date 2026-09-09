import io
import pandas as pd
from fastapi import HTTPException

async def inspect_parquet(file):
    contents = await file.read()

    try:
        df = pd.read_parquet(io.BytesIO(contents), engine="pyarrow")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The Parquet file could not be read",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "parquet",
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": [str(column) for column in df.columns],
        "column_types": {str(column): str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated(keep=False).sum()),
    }