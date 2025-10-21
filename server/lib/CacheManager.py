


class CacheManager:
    """
    The unified library for managing caches for intermediate results of nodes.
    Can be used by nodes or fastapi for returning intermediate results to visualization.
    Can be called in multiple containers.
    """

    def __init__(self, user_id: int, project_id: int) -> None:
        self.user_id = user_id
        self.project_id = project_id

    # TODO: Implement cache management methods
