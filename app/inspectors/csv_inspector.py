import csv
import io
from io import StringIO
import pandas as pd

async def inspect_csv(file):
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

    return {
        "filename": file.filename, 
        "content_type": file.content_type, 
        "size_bytes": file.size, "rows": len(rows), 
        "columns": len(columns), "column_names": columns, 
        "missing_values": total_missing, 
        "duplicate_rows": len(duplicate_df)
    }