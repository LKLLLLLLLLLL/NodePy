from pydantic import BaseModel

"""
This file contains data models for project list representation, used in explore page.
"""


class ExploreListItem(BaseModel):
    project_id: int
    project_name: str
    owner: int
    created_at: int  # unix timestamp in milliseconds
    updated_at: int  # unix timestamp in milliseconds
    thumb: str | None = None  # base64 encoded thumbnail image


class ExploreList(BaseModel):
    projects: list[ExploreListItem]
