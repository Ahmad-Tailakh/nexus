


class DeploymentNotFoundError(ValueError):
    """Raised when a Deployment cannot be found."""

    def __init__(self) -> None:
        super().__init__("Deployment not found.")