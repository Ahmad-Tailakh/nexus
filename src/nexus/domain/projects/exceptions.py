class ProjectNameRequiredError(ValueError):
    """Raised when a project is created without a name."""

    def __init__(self) -> None:
        super().__init__("Project name is required.")