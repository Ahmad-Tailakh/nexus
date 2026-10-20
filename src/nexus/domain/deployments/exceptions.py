class InvalidDeploymentServiceIdError(ValueError):
    """Raised when a Deployment is created with an invalid Service ID."""

    def __init__(self) -> None:
        super().__init__(
            "Deployment service ID must be a valid UUID."
        )


class InvalidDeploymentTransitionError(ValueError):
    """Raised when an invalid Deployment state transition is requested."""

    def __init__(self) -> None:
        super().__init__(
            "Invalid deployment state transition."
        )