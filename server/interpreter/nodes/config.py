from pydantic import BaseModel, model_validator
from typing_extensions import Self

from server.lib.FileManager import FileManager
from server.lib.FinancialDataManager import FinancialDataManager


class GlobalConfig(BaseModel):
    """
    Global config shared by all nodes for same requests.
    Manage context like FileManager etc.
    """
    
    file_manager: FileManager      # manager for file operations
    financial_data_manager: FinancialDataManager  # manager for financial data operations
    user_id: int                   # current user id
    project_id: int                # current project id

    model_config = {
        "arbitrary_types_allowed": True
    }
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        return self

