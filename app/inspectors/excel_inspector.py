import io
import pandas as pd
from fastapi import HTTPException
from pathlib import Path


async def inspect_excel(file):
    contents = await file.read()

    try:
        workbook = pd.ExcelFile(io.BytesIO(contents))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The Excel file could not be read",
        )

    sheets = []
    file_type = Path(file.filename).suffix.lower().lstrip(".")

    try:
        for sheet_name in workbook.sheet_names:
            df = pd.read_excel(workbook, sheet_name=sheet_name)

            sheets.append({
                "name": sheet_name,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": [str(column) for column in df.columns],
                "missing_values": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated(keep=False).sum()),
            })
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The Excel file contains an unreadable worksheet",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": file_type,
        "sheet_count": len(sheets),
        "sheets": sheets,
    }