import csv
import io
from io import StringIO
from fastapi import HTTPException
import pandas as pd

async def inspect_csv(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
        df = pd.read_csv(io.BytesIO(contents))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file is not valid UTF-8 text",
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file is empty",
        )
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="The CSV file could not be parsed",
        )

    buffer = StringIO(text)
    total_missing = int(df.isnull().sum().sum())
    reader = csv.DictReader(buffer)
    rows = [row for row in reader]
    columns = reader.fieldnames
    duplicate_mask = df.duplicated(keep=False)
    duplicate_df = df[duplicate_mask]
    buffer.close()

    return {
        "filename": file.filename, 
        "content_type": file.content_type, 
        "size_bytes": file.size, 
        "rows": len(rows), 
        "columns": len(columns), 
        "column_names": columns, 
        "missing_values": total_missing, 
        "duplicate_rows": len(duplicate_df)
    }