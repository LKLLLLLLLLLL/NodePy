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

    def __init__(self, node_id: str, 
                 err_param_keys: list[str] | None = None, err_msgs: list[str] | None = None,
                 err_param_key: str | None = None, err_msg: str | None = None):
        self.node_id: str = node_id
        if err_param_key is not None and err_msg is not None:
            assert err_param_keys is None and err_msgs is None, "Provide either single or multiple error details, not both."
            self.err_param_keys = [err_param_key]
            self.err_msgs = [err_msg]
        elif err_param_keys is not None and err_msgs is not None:
            assert err_param_key is None and err_msg is None, "Provide either single or multiple error details, not both."
            assert len(err_param_keys) == len(err_msgs), "err_param_keys and err_msgs must have the same length."
            self.err_param_keys = err_param_keys
            self.err_msgs = err_msgs
        else:
            raise ValueError("Either err_param_keys and err_msgs or err_param_key and err_msg must be provided.")
        super().__init__(
            f"NodeParameterError in node '{node_id}': {self.err_param_keys} - {self.err_msgs}"
        )


class NodeValidationError(Exception):
    """static validation error"""

    def __init__(self, node_id: str, 
                 err_inputs: list[str] | None = None, err_msgs: list[str] | None = None,
                 err_input: str | None = None, err_msg: str | None = None):
        self.node_id: str = node_id
        if err_input is not None and err_msg is not None:
            assert err_inputs is None and err_msgs is None, "Provide either single or multiple error details, not both."
            self.err_inputs = [err_input]
            self.err_msgs = [err_msg]
        elif err_inputs is not None and err_msgs is not None:
            assert err_input is None and err_msg is None, "Provide either single or multiple error details, not both."
            assert len(err_inputs) == len(err_msgs), "err_inputs and err_msgs must have the same length."
            self.err_inputs = err_inputs
            self.err_msgs = err_msgs
        else:
            raise ValueError("Either err_inputs and err_msgs or err_input and err_msg must be provided.")
        super().__init__(
            f"NodeValidationError in node '{node_id}': {self.err_inputs} - {self.err_msgs}"
        )


class NodeExecutionError(Exception):
    """runtime execution error"""

    def __init__(self, node_id: str, err_msg: str):
        self.node_id: str = node_id
        self.err_msg: str = err_msg
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
