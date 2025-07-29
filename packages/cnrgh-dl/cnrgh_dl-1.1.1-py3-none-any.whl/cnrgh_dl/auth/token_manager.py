from __future__ import annotations

import math
import threading
from typing import cast

import requests
from requests import Response
from typing_extensions import Self

from cnrgh_dl import config
from cnrgh_dl.auth.device_flow import DeviceFlow
from cnrgh_dl.exceptions import OfflineSessionMaxReachedError
from cnrgh_dl.logger import Logger
from cnrgh_dl.models import TokenResponse
from cnrgh_dl.utils import hash_access_token, safe_parse_obj_as

logger = Logger.get_instance()
"""Module logger instance."""


class TokenManager:
    """Manages the lifecycle of an access token.
    When initialised, the class starts an OAuth 2.0 Device Authorization Grant process (Device Flow) to obtain one.
    Then, the access token can be refreshed by calling the `refresh_token()` method.
    """

    _lock: threading.Lock
    """Lock instance to share variables between the main thread and the refresh thread."""
    _token_response: TokenResponse
    """Dataclass that contains the access token and the refresh token returned by Keycloak."""
    _userinfo: dict[str, str]
    """User info dict returned by the Keycloak userinfo endpoint."""

    def __init__(self: Self) -> None:
        """Initialize the token manager by starting a device flow to obtain an access token and
        retrieve user info.
        """
        logger.debug("Initializing the token manager...")

        # Start the device flow to obtain an access and a refresh token.
        self._lock = threading.Lock()
        self._token_response = DeviceFlow.start()
        self._userinfo = self._get_userinfo()

        try:
            username = self._userinfo["name"]
        except KeyError:
            username = self._userinfo["preferred_username"]

        logger.info("Logged as: %s.", username)
        logger.debug(
            "Access token hash = %s.",
            hash_access_token(self._token_response.access_token),
        )

    def _get_userinfo(self: Self) -> dict[str, str]:
        """Get user information by calling the Keycloak userinfo endpoint.

        :raises requests.exceptions.RequestException:
            An error occurred with the request.
        :return: A dict of strings containing user information.
        """
        response: Response = requests.get(
            config.KEYCLOAK_USER_INFO_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self.token_response.access_token}",
            },
            timeout=config.REQUESTS_TIMEOUT,
        )
        response.raise_for_status()
        return cast("dict[str, str]", response.json())

    def get_token_refresh_wait_time(self: Self) -> int:
        """Get the time (in seconds) to wait before trying to refresh the access token.
        The wait time is equal to 90% of the access token lifespan,
        leaving a 10% time margin to refresh the access token before it expires.
        """
        expires_in = self.token_response.expires_in
        return expires_in - math.ceil(expires_in / 10)

    def refresh_token(self: Self) -> None:
        """Refresh the current access token by calling the Keycloak token endpoint
        with its refresh token and save its new value.

        :raises requests.exceptions.RequestException:
            An error occurred with the request.
        """
        params: dict[str, str] = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "scope": config.REQUESTED_ACCESS_SCOPE,
            "grant_type": "refresh_token",
            "refresh_token": self.token_response.refresh_token,
        }

        response = requests.post(
            config.KEYCLOAK_TOKEN_ENDPOINT,
            data=params,
            timeout=config.REQUESTS_TIMEOUT,
        )
        response.raise_for_status()

        self._set_token_response(
            safe_parse_obj_as(
                TokenResponse,
                response.json(),
            )
        )

    def check_threshold(self, refresh_threshold: int) -> None:
        """Check if the new access token's expiry time has significantly decreased,
        which indicate that the session is nearing its end.

        :param refresh_threshold: refresh threshold in seconds.
        :raises OfflineSessionMaxReachedError: The offline session is nearing its end.
        """
        if self.token_response.expires_in <= refresh_threshold:
            raise OfflineSessionMaxReachedError(self.token_response.expires_in)

    @property
    def token_response(self: Self) -> TokenResponse:
        """Get the latest token response, containing a valid access token."""
        with self._lock:
            return self._token_response

    def _set_token_response(self, token_response: TokenResponse) -> None:
        logger.debug(
            "New access token hash is '%s', was previously '%s'.",
            hash_access_token(token_response.access_token),
            hash_access_token(self.token_response.access_token),
        )
        with self._lock:
            self._token_response = token_response

    @property
    def userinfo(self: Self) -> dict[str, str]:
        """Get the current user info."""
        with self._lock:
            return self._userinfo
