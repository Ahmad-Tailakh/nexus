class ServiceNameRequiredError(ValueError):
    """Raised when an environments is created without a name."""

    def __init__(self) -> None:
        super().__init__("Environment name is required.")


class InvalidServiceEnvironmentIdError(ValueError):
    """Raised when an environment is created with an invalid project ID."""

    def __init__(self) -> None:
        super().__init__("Environment project ID must be a valid UUID.")

