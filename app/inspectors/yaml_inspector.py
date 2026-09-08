from fastapi import HTTPException
import yaml

async def inspect_yaml(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
        documents = list(yaml.safe_load_all(text))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not valid UTF-8 YAML",
        )
    except yaml.YAMLError:
        raise HTTPException(
            status_code=400,
            detail="The YAML file could not be parsed",
        )

    first_document = documents[0] if documents else None
    response = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "yaml",
        "yaml_type": type(first_document).__name__,
        "valid": True,
        "documents": len(documents),
    }

    if isinstance(first_document, dict):
        response["keys"] = list(first_document.keys())
        response["key_count"] = len(first_document)

    return response