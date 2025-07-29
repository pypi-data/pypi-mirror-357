from __future__ import annotations

import threading
from enum import Enum

import requests

from cnrgh_dl.auth.token_manager import TokenManager
from cnrgh_dl.config import REQUESTED_ACCESS_SCOPE
from cnrgh_dl.exceptions import (
    MissingScopesError,
    OfflineSessionMaxReachedError,
)
from cnrgh_dl.logger import Logger
from cnrgh_dl.models import TokenErrorResponse, TokenResponse
from cnrgh_dl.utils import safe_parse_obj_as, verify_scopes

logger = Logger.get_instance()
"""Module logger instance."""


class RefreshTokenThreadExitStatus(Enum):
    """Enum representing the exit status of the token refresh thread."""

    NONE = -1
    """No exit status is available: the refresh thread has not been started yet or is currently running."""
    SUCCESS = 0
    """The refresh thread stopped successfully."""
    OFFLINE_SESSION_MAX_REACHED_ERROR = 1
    """The refresh thread stopped because the offline session has reached its maximum allowed duration."""
    REFRESH_TOKEN_ERROR = 2
    """The refresh thread stopped because it encountered an error while attempting to refresh the token
    (e.g., network error, invalid token, or missing scopes)."""


class RefreshTokenThread(threading.Thread):
    """Daemon thread used to periodically refresh an access token
    to ensure that it is always valid.
    """

    _stop_event: threading.Event
    """Event to stop the refresh thread."""
    _exit_status: RefreshTokenThreadExitStatus
    """Refresh thread exit status."""
    _lock: threading.Lock
    """Lock instance to share variables between the main thread and the refresh thread."""
    _token_manager: TokenManager
    """Token manager used to obtain an initial access token from Keycloak, and then refresh it."""

    def __init__(self) -> None:
        """Initialise the RefreshTokenThread class."""
        self._stop_event = threading.Event()
        self._exit_status = RefreshTokenThreadExitStatus.NONE
        self._lock = threading.Lock()
        self._token_manager = TokenManager()
        # Run as a daemon so the thread will automatically terminate when
        # the main thread exits.
        super().__init__(daemon=True)

    @property
    def exit_status(self) -> RefreshTokenThreadExitStatus:
        """Get the current thread status."""
        with self._lock:
            return self._exit_status

    def _set_exit_status(
        self, exit_status: RefreshTokenThreadExitStatus
    ) -> None:
        logger.debug(
            "Thread exit status set to '%s', was previously '%s'.",
            exit_status,
            self.exit_status,
        )
        with self._lock:
            self._exit_status = exit_status

    @property
    def token_response(self) -> TokenResponse:
        """Get the latest token response, containing a valid access token."""
        return self._token_manager.token_response

    def run(self) -> None:
        """Start periodically refreshing the access token in a daemon thread.
        If the thread encounters any error, it will stop.
        """
        logger.debug("[Refresh token thread] Starting background refresh...")
        # Obtain a refresh wait time based on the lifespan of the access token obtained during
        # the initialization of the TokenManager class.
        # The loop will start by waiting to avoid directly refreshing the first obtained token.
        wait_time = self._token_manager.get_token_refresh_wait_time()
        refresh_threshold = self._token_manager.token_response.expires_in // 2
        try:
            while not self._stop_event.is_set():
                logger.debug(
                    "[Refresh token thread] Access token will expire in %s seconds. "
                    "Sleeping %s seconds before trying to refresh it. Using a %s seconds threshold.",
                    self._token_manager.token_response.expires_in,
                    wait_time,
                    refresh_threshold,
                )

                if self._stop_event.wait(wait_time):
                    logger.debug(
                        "[Refresh token thread] Received a 'STOP' event while sleeping, waking up."
                    )
                    break

                self._token_manager.refresh_token()
                # Ensure that the server granted all the required scopes.
                verify_scopes(
                    REQUESTED_ACCESS_SCOPE,
                    self._token_manager.token_response.scope,
                )

                logger.debug(
                    "[Refresh token thread] New access token lifespan is %s seconds.",
                    self._token_manager.token_response.expires_in,
                )
                self._token_manager.check_threshold(refresh_threshold)

                # Update the refresh wait time and threshold from the newly received access token.
                wait_time = self._token_manager.get_token_refresh_wait_time()
                refresh_threshold = (
                    self._token_manager.token_response.expires_in // 2
                )

        except OfflineSessionMaxReachedError as e:
            # Treat this exception as a warning.
            logger.warning(e)
            self._set_exit_status(
                RefreshTokenThreadExitStatus.OFFLINE_SESSION_MAX_REACHED_ERROR
            )
            return

        except (
            requests.exceptions.RequestException,
            MissingScopesError,
        ) as err:
            # If the token endpoint has returned an HTTP error,
            # log its response type and description.
            if isinstance(err, requests.exceptions.HTTPError):
                response_error: TokenErrorResponse = safe_parse_obj_as(
                    TokenErrorResponse,
                    err.response.json(),
                )
                logger.error(
                    "Refresh token error '%s': %s",
                    response_error.error,
                    response_error.error_description,
                )
            else:
                logger.error(err)

            self._set_exit_status(
                RefreshTokenThreadExitStatus.REFRESH_TOKEN_ERROR
            )
            return

        logger.debug(
            "[Refresh token thread] The thread has successfully stopped."
        )
        self._set_exit_status(RefreshTokenThreadExitStatus.SUCCESS)

    def terminate(self) -> None:
        """Terminate the thread."""
        logger.debug("Stopping the refresh thread...")

        if not self.is_alive():
            logger.debug("Thread is already stopped.")
            return

        self._stop_event.set()
