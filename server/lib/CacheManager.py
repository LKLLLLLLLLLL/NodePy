
class CacheManager:
    """
    The unified library for managing caches for intermediate results of nodes.
    Can be used by nodes or fastapi for returning intermediate results to visualization.
    Can be called in multiple containers.
    """
    
    user_id: str
    project_id: str
    
    def __init__(self, user_id: str, project_id: str) -> None:
        if not isinstance(user_id, str) or user_id.strip() == "":
            raise ValueError("user_id cannot be empty.")
        if not isinstance(project_id, str) or project_id.strip() == "":
            raise ValueError("project_id cannot be empty.")
        self.user_id = user_id
        self.project_id = project_id

    # TODO: Implement cache management methods
