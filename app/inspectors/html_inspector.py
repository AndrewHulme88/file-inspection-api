from bs4 import BeautifulSoup
from fastapi import HTTPException

async def inspect_html(file):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "The HTML file is not valid UTF-8 text")

    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else None

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file.size,
        "file_type": "html",
        "title": title,
        "heading_count": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
        "link_count": len(soup.find_all("a", href=True)),
        "text_characters": len(soup.get_text()),
        "valid": True,
    }