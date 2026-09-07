from typing import Any, Literal
from pydantic import BaseModel, Field

class FileInspectionBase(BaseModel):
    filename: str
    content_type: str | None = None
    size_bytes: int | None = None

class CsvInspection(FileInspectionBase):
    file_type: Literal["csv"] = "csv"
    rows: int
    columns: int
    column_names: list[str]
    missing_values: int
    duplicate_rows: int

class JsonInspection(FileInspectionBase):
    file_type: Literal["json"] = "json"
    json_type: str
    valid: bool
    keys: list[str] | None = None
    key_count: int | None = None
    rows: int | None = None
    columns: int | None = None
    column_names: list[str] | None = None
    missing_values: int | None = None
    duplicate_rows: int | None = None
    value: Any = None

class TextInspection(FileInspectionBase):
    file_type: Literal["text"] = "text"
    characters: int
    words: int
    lines: int
    empty_lines: int
    encoding: str

InspectionResponse = CsvInspection | JsonInspection | TextInspection