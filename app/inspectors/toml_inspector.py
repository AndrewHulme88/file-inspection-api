import tomllib
from fastapi import HTTPException

async def inspect_toml(file):
    contents = await file.read()

    try:
        data = tomllib.loads(contents.decode("utf-8"))
    except UnicodeDecodeError:
        raise HTTPException(400, "The TOML file is not valid UTF-8 text")
    except tomllib.TOMLDecodeError:
        raise HTTPException(400, "The TOML file could not be parsed")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "toml",
        "key_count": len(data),
        "keys": list(data.keys()),
        "valid": True,
    }