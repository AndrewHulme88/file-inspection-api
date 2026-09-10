import configparser
import io
from fastapi import HTTPException

async def inspect_ini(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
        parser = configparser.ConfigParser()
        parser.read_file(io.StringIO(text))
    except UnicodeDecodeError:
        raise HTTPException(400, "The INI file is not valid UTF-8 text")
    except configparser.Error:
        raise HTTPException(400, "The INI file could not be parsed")

    sections = parser.sections()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "ini",
        "section_count": len(sections),
        "sections": sections,
        "setting_count": sum(len(parser[section]) for section in sections),
        "valid": True,
    }