


class ServiceNotFoundError(ValueError):
    """Raised when an Environment cannot be found."""

    def __init__(self) -> None:
        super().__init__("Environment not found.")


class ServiceNameAlreadyExistsError(ValueError):
    """Raised when an Environment name already exists within a Project."""

    def __init__(self) -> None:
        super().__init__(
            "Environment name already exists in this Project."
        )

