from pydantic import BaseModel, model_validator
from typing_extensions import Self
from pathlib import Path

"""
global_config shared by all nodes for same requests
"""
class GlobalConfig(BaseModel):
    temp_dir: Path  # directory to store temporary files
    user_id: str    # user id for current request
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        if not self.temp_dir.is_dir():
            raise ValueError(f"temp_dir is not a directory: {self.temp_dir}")
        if self.user_id == "" or self.user_id.strip() == "":
            raise ValueError("user_id cannot be empty.")
        return self
