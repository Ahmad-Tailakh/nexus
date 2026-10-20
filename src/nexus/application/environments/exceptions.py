class EnvironmentNotFoundError(ValueError):
    """Raised when an Environment cannot be found."""

    def __init__(self) -> None:
        super().__init__("Environment not found.")


class EnvironmentNameAlreadyExistsError(ValueError):
    """Raised when an Environment name already exists within a Project."""

    def __init__(self) -> None:
        super().__init__(
            "Environment name already exists in this Project."
        )

class EnvironmentHasServicesError(ValueError):
    """Raised when an Environment cannot be deleted because Services exist."""

    def __init__(self) -> None:
        super().__init__(
            "Environment cannot be deleted while Services exist."
        )