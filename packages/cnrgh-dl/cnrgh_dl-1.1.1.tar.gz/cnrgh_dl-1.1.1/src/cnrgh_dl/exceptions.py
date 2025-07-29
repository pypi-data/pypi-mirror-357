from typing_extensions import Self


class PrematureDownloadTerminationError(Exception):
    """Exception raised when a download finishes prematurely."""

    def __init__(self: Self) -> None:
        """Initialize a PrematureDownloadTerminationError exception."""
        super().__init__(
            "Download prematurely terminated. "
            "The server may not have sent all the data or there was a network issue.",
        )


class MissingScopesError(Exception):
    """Exception raised when the server did not grant all the requested scopes."""

    def __init__(self: Self, missing_scopes: set[str]) -> None:
        """Initialize a MissingScopesError exception."""
        self.missing_scopes = missing_scopes
        super().__init__(
            f"Some scopes were not granted by the authorization server "
            f"and are missing: {','.join(missing_scopes)}."
        )


class SingleAppInstanceError(Exception):
    """Exception raised when an instance of 'cnrgh-dl' is already running."""

    def __init__(self: Self, pid: int) -> None:
        """Initialize a SingleAppInstanceError exception."""
        super().__init__(
            f"An instance of 'cnrgh-dl' with PID {pid} is already running."
        )


class OfflineSessionMaxReachedError(Exception):
    """Exception raised when the offline session maximum duration is nearly reached,
    indicating that the next downloads will not be processed.
    """

    def __init__(self: Self, expires_in: int) -> None:
        """Initialize an OfflineSessionMaxReachedError exception."""
        super().__init__(
            f"The maximum duration for an offline session is nearly reached "
            f"({expires_in} seconds remaining). cnrgh-dl will stop refreshing the access token. "
            f"The current download will complete successfully, "
            f"but any subsequent downloads will be skipped."
        )
