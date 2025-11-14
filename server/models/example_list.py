from pydantic import BaseModel

"""
This file contains data models for example list representation, used in example page.
"""


class ExampleListItem(BaseModel):
    project_id: int
    project_name: str
    owner: int
    created_at: int  # unix timestamp in milliseconds
    updated_at: int  # unix timestamp in milliseconds
    thumb: str | None = None  # base64 encoded thumbnail image


class ExampleList(BaseModel):
    userid: int
    projects: list[ExampleListItem]
