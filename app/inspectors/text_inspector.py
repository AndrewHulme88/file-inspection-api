from fastapi import HTTPException

async def inspect_text(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
        encoding = "UTF-8"
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The file is not valid UTF-8 text",
        )

    lines = text.splitlines()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "text",
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(lines),
        "empty_lines": sum(not line.strip() for line in lines),
        "encoding": encoding
    }