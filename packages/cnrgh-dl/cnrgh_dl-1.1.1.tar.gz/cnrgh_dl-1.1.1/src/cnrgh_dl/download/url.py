from pathlib import PurePosixPath
from urllib.parse import urlparse

from cnrgh_dl import config
from cnrgh_dl.logger import Logger

logger = Logger.get_instance()
"""Module logger instance."""


class URL:
    """URL manipulation utilities."""

    @staticmethod
    def get_path_filename(url: str) -> str:
        """Gets the filename of a file present in the path of the URL.
        If the path of the URL is a directory (e.g. the path does not contain any extension),
        an empty string is returned.

        :param url: URL
        :return: The filename if a file is present in the path, otherwise an empty string.
        """
        if URL.is_path_a_dir(url):
            return ""
        return PurePosixPath(urlparse(url).path).name

    @staticmethod
    def get_path_extension(url: str) -> str:
        """Gets the extension of the path contained in the URL.

        :param url: URL
        :return: The extension (including the leading period) or
            an empty string if there is no extension.
        """
        return PurePosixPath(urlparse(url).path).suffix.lower()

    @staticmethod
    def is_path_a_dir(url: str) -> bool:
        """Checks if the path of the URL ends with a trailing slash.

        :param url: URL
        :return: True if the path points to a directory, False otherwise.
        """
        return urlparse(url).path[-1] == "/"

    @staticmethod
    def get_parent_directory(url: str) -> str:
        """Gets a new URL whose path is the parent directory of the given URL.

        :param url: URL
        :return: A new URL whose path is the parent directory of the given URL.
        """
        parsed_url = urlparse(url)
        download_path = PurePosixPath(parsed_url.path)

        try:
            parent = str(download_path.parents[0])
        except IndexError:
            parent = ""

        return parsed_url._replace(path=parent).geturl()

    @staticmethod
    def validate(url: str) -> tuple[bool, str]:
        """Validates a download URL.

        To be validated, a download URL must start with the download endpoint
        of the datawebnode server (see ``DATAWEBNODE_DOWNLOAD_ENDPOINT``
        in the config module) and contains a path to a file
        (and not a directory).

        :param url: The URL to validate.
        :return: True if the URL fulfills all the conditions listed above,
            False otherwise.
        """
        if not url:
            logger.debug("Skipping empty URL.")
            return False, "empty_url"

        if not url.startswith(config.DATAWEBNODE_DOWNLOAD_ENDPOINT):
            logger.error(
                "Error: URL %s is not valid: "
                "it does not points to the server "
                "download API endpoint: %s.",
                url,
                config.DATAWEBNODE_DOWNLOAD_ENDPOINT,
            )
            return False, "invalid_prefix"

        if url in {
            config.DATAWEBNODE_DOWNLOAD_ENDPOINT,
            config.DATAWEBNODE_DOWNLOAD_ENDPOINT + "/",
        }:
            logger.error(
                "Error: URL %s is not valid: "
                "it points to the server download API endpoint "
                "but does not provide a file path.",
                url,
            )
            return False, "empty_filepath"

        if URL.is_path_a_dir(url):
            logger.error(
                "Error: URL %s is not valid: "
                "it points to a directory instead of a file.",
                url,
            )
            return False, "invalid_filepath"

        return True, "valid_url"


class DownloadURL:
    """Utility class for handling download URLs."""

    @staticmethod
    def _assert_valid_prefix(url: str) -> None:
        """Validates that the given URL starts with the download API endpoint.

        :param url: The URL to validate.
        :raises ValueError: If the URL does not start with the download
            endpoint.
        """
        if not url.startswith(config.DATAWEBNODE_DOWNLOAD_ENDPOINT):
            msg = "Download URL must start with the download API endpoint."
            raise ValueError(msg)

    @staticmethod
    def get_relative_path(url: str) -> str:
        """Returns the relative path by removing the download API endpoint
        from the URL.

        :param url: The full URL.
        :raises ValueError: If the URL does not start with the download
            endpoint.
        :return: The relative path.
        """
        DownloadURL._assert_valid_prefix(url)
        return url[len(config.DATAWEBNODE_DOWNLOAD_ENDPOINT) :]

    @staticmethod
    def get_full_url(relative_path: str) -> str:
        """Builds a full download URL from a relative path.

        :param relative_path: The relative path to append to the endpoint.
        :return: The full URL.
        """
        return config.DATAWEBNODE_DOWNLOAD_ENDPOINT + relative_path.lstrip("/")

    @staticmethod
    def get_project_name(url: str) -> str:
        """Extracts the project name from the given URL.

        Assumes the project name is the first segment of the relative path.

        :param url: The full URL.
        :raises ValueError: If the URL does not start with the download
            endpoint.
        :return: The project name.
        """
        return DownloadURL.get_relative_path(url).split("/")[0]
