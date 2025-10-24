"""
This file defines custom exceptions.
"""

class ModelValidationError(Exception):
    """
    Exception raised for errors in the model validation.
    """
    pass

class NodeParameterError(Exception):
    """parameter error"""

    node_id: str
    err_param_key: str
    err_msg: str

    def __init__(self, node_id: str, err_param_key: str, err_msg: str):
        self.node_id = node_id
        self.err_param_key = err_param_key
        self.err_msg = err_msg
        super().__init__(
            f"NodeParameterError in node '{node_id}': {err_param_key} - {err_msg}"
        )


class NodeValidationError(Exception):
    """static validation error"""

    node_id: str
    err_input: list[str]
    err_msg: str

    def __init__(self, node_id: str, err_input: list[str], err_msg: str):
        self.node_id = node_id
        self.err_input = err_input
        self.err_msg = err_msg
        super().__init__(
            f"NodeValidationError in node '{node_id}': {err_input} - {err_msg}"
        )


class NodeExecutionError(Exception):
    """runtime execution error"""

    node_id: str
    err_msg: str

    def __init__(self, node_id: str, err_msg: str):
        self.node_id = node_id
        self.err_msg = err_msg
        super().__init__(f"NodeExecutionError in node '{node_id}': {err_msg}")

class InsufficientStorageError(Exception):
    """user storage limit exceeded"""
    pass

class ProjectLockError(Exception):
    """project is locked for editing"""
    pass

class ProjLockIdentityError(Exception):
    """
    project lock identity error: your identity does not match the appointed identity, the appointed identity may timeout or be cleared
    """
    pass