from defusedxml import ElementTree
from fastapi import HTTPException

def get_depth(element):
    if not list(element):
        return 1
    return 1 + max(get_depth(child) for child in element)

def count_elements(element):
    return 1 + sum(count_elements(child) for child in element)

async def inspect_xml(file):
    contents = await file.read()

    try:
        root = ElementTree.fromstring(contents)
    except ElementTree.ParseError:
        raise HTTPException(
            status_code=400,
            detail="The XML file could not be parsed",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "xml",
        "root_tag": root.tag,
        "element_count": count_elements(root),
        "max_depth": get_depth(root),
        "valid": True,
    }