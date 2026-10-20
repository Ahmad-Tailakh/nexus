class ProjectNameAlreadyExistsError(ValueError):
    """Raised when a project with the given name already exists."""

    def __init__(self) -> None:
        super().__init__("Project name already exists.")

class ProjectNotFoundError(ValueError):
    """Raised when the requested Project does not exist."""

    def __init__(self) -> None:
        super().__init__("Project not found.")


class ProjectHasEnvironmentsError(ValueError):
    """Raised when a project cannot be deleted because it has environments."""

    def __init__(self) -> None:
        super().__init__("Project has environments and cannot be deleted.")
