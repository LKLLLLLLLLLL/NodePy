from pydantic import BaseModel

class ProjectListItem(BaseModel):
    project_id: int
    project_name: str
    owner: int
    created_at: int # unix timestamp in milliseconds
    updated_at: int # unix timestamp in milliseconds
    thumb: str | None = None  # base64 encoded thumbnail image

class ProjectList(BaseModel):
    userid: int
    projects: list[ProjectListItem]