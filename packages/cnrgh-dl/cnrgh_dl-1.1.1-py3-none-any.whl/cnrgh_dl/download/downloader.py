import shutil
from pathlib import Path
from time import sleep

import requests
import urllib3.exceptions
from tqdm import tqdm
from typing_extensions import Self

from cnrgh_dl import config
from cnrgh_dl.auth.refresh_token import (
    RefreshTokenThread,
    RefreshTokenThreadExitStatus,
)
from cnrgh_dl.download.url import URL, DownloadURL
from cnrgh_dl.exceptions import PrematureDownloadTerminationError
from cnrgh_dl.logger import Logger
from cnrgh_dl.models import (
    FileType,
    LocalFile,
    LocalFiles,
    RemoteFile,
    Result,
    Results,
    Status,
)
from cnrgh_dl.utils import hash_access_token, safe_parse_obj_as

logger = Logger.get_instance()
"""Module logger instance."""


class Downloader:
    """Handle the downloads."""

    _refresh_token_thread: RefreshTokenThread
    """A RefreshTokenThread instance to obtain a valid access token to
    include in each request made to the datawebnode server."""
    _output_dir: Path
    """Output directory where downloaded files are stored."""

    def __init__(
        self: Self,
        refresh_token_thread: RefreshTokenThread,
        output_dir: Path,
    ) -> None:
        """Initialize a downloader with a refresh token thread and
        an output directory to store files.
        """
        self._refresh_token_thread = refresh_token_thread
        self._output_dir = output_dir

    def _get_project_files(self: Self, project_name: str) -> list[RemoteFile]:
        """Retrieves the list of files for a given project using the project API endpoint.

        This method sends a GET request to the server with the specified project name.
        The server responds with a JSON array of file metadata, which is parsed into a list
        of `RemoteFile` objects.

        :param project_name: Name of the project whose files are to be retrieved.
        :raises RequestException: If the request to the server fails or returns an error status.
        :return: A list of `RemoteFile` instances representing the project's files.
        """
        response = requests.get(
            config.DATAWEBNODE_PROJECT_FILES_ENDPOINT + project_name,
            headers={
                "Authorization": f"Bearer {self._refresh_token_thread.token_response.access_token}",
            },
            timeout=config.REQUESTS_TIMEOUT,
        )
        response.raise_for_status()
        return safe_parse_obj_as(list[RemoteFile], response.json())

    def fetch_additional_checksums(
        self: Self,
        project_name: str,
        file_urls: set[str],
        checksum_urls: set[str],
    ) -> LocalFiles:
        """Identifies MD5 checksum files to add to the additional
        checksum queue.

        This method retrieves the full list of files in a project
        from the server. Then, for each file already queued for download,
        if its corresponding MD5 checksum file exists on the server and
        is not yet in the checksum queue, it is added to the additional
        checksum queue.

        :param project_name: Name of the project from which to fetch
            additional checksums.
        :param file_urls: Set of URLs of the files already in the file queue.
        :param checksum_urls: Set of URLs of the MD5 checksum files already in
            the checksum queue.
        :raises RequestException: If retrieving the project file list from the
            server fails.
        :return: A queue of additional MD5 checksum files to download,
            with URLs as keys and corresponding `LocalFile` instances as values.
        """
        additional_checksums: LocalFiles = {}

        project_files = self._get_project_files(project_name)
        project_checksum_urls = [
            DownloadURL.get_full_url(remote_file.display_path)
            for remote_file in project_files
            if URL.get_path_extension(remote_file.display_path) == ".md5"
        ]

        for file_url in file_urls:
            expected_checksum_url = f"{file_url}.md5"
            # Check that the expected MD5 checksum file exists on the server,
            # and is not already present in the checksum download queue.
            if (
                expected_checksum_url in project_checksum_urls
                and expected_checksum_url not in checksum_urls
            ):
                filename = URL.get_path_filename(expected_checksum_url)
                additional_checksums[expected_checksum_url] = LocalFile(
                    filename=filename,
                    file_type=FileType.CHECKSUM,
                    path=Path(self._output_dir / filename),
                    is_partially_downloaded=False,
                )

        return additional_checksums

    def _download(
        self: Self,
        url: str,
        local_file: LocalFile,
        *,
        force_download: bool,
    ) -> None:
        """Download a file from the datawebnode server.
        This function can also continue a partial download by sending a Range header to the server
        if ``local_file.is_partially_downloaded`` is ``True``.

        :param url: The URL of the file to download,
            hosted on the datawebnode server.
        :param local_file: A LocalFile instance containing metadata about the file that will be downloaded.
        :param force_download: Flag to force the download of files.
        :raises requests.exceptions.RequestException:
            An error occurred while requesting the file.
        :raises requests.RequestException:
            An error occurred while handling the download request.
        :raises urllib3.exceptions.ReadTimeoutError:
            The network connection was lost while receiving a file.
        :raises PrematureDownloadTerminationError:
            The download could not fully finish because the server went down.
        :raises FileNotFoundError:
            The file was moved or deleted during the download.
        :raises Exception:
            An exception other than those listed above has been raised.
        """
        logger.debug(
            "Download is using access token '%s'.",
            hash_access_token(
                self._refresh_token_thread.token_response.access_token
            ),
        )
        partial_save_path = local_file.path.with_suffix(
            local_file.path.suffix + config.PARTIAL_DOWNLOAD_SUFFIX,
        )

        headers = {
            "Authorization": f"Bearer {self._refresh_token_thread.token_response.access_token}",
        }
        open_mode = "wb"

        if local_file.is_partially_downloaded:
            if force_download:
                partial_save_path.unlink(missing_ok=True)
            else:
                downloaded_size = partial_save_path.stat().st_size
                headers["Range"] = f"bytes={downloaded_size}-"
                open_mode = "ab"

        response = requests.get(
            url,
            stream=True,
            headers=headers,
            timeout=config.REQUESTS_TIMEOUT,
        )
        response.raise_for_status()

        file_size = int(response.headers.get("Content-Length", 0))

        desc = (
            f"{local_file.filename} (unknown total file size)"
            if file_size == 0
            else f"{local_file.filename}"
        )

        with (
            tqdm.wrapattr(
                response.raw,
                "read",
                total=file_size,
                unit="B",
                unit_scale=True,
                miniters=1,
                desc=desc,
                leave=False,
            ) as r_raw,
            Path.open(partial_save_path, open_mode) as f,
        ):
            shutil.copyfileobj(r_raw, f, length=16 * 1024 * 1024)

        # If the server goes down during a download,
        # raise an exception because the file has not been fully downloaded.
        if partial_save_path.stat().st_size < file_size:
            raise PrematureDownloadTerminationError

        partial_save_path.rename(local_file.path)

    def _pre_download_checks(
        self, url: str, local_file: LocalFile, *, force_download: bool
    ) -> Results:
        """Succession of checks to run before starting a download:
            - do not start the download if the file already exist in the output directory,
                and we are not forcing downloads.
            - do not start the download if the token refresh thread has encountered an error
                (offline session max duration was reached, or the token could not be refreshed).

        :param url: URL of the file to download.
        :param local_file: Metadata about the file that will be downloaded.
        :param force_download: Flag to force the download of files.
        :return: An empty dict if all the checks were successful,
          or a dict with the file URL as key and a Result
          instance as value containing details of the failed check error.
        """
        is_file_download_complete = (
            local_file.path.is_file() and not local_file.is_partially_downloaded
        )

        if not force_download and is_file_download_complete:
            logger.warning(
                "Skipping download of file %s as it already exists in the output directory.",
                str(local_file.filename),
            )
            return {
                url: Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.SKIPPED,
                    "File already exists in the output directory.",
                ),
            }

        if (
            not self._refresh_token_thread.is_alive()
            and self._refresh_token_thread.exit_status
            == RefreshTokenThreadExitStatus.OFFLINE_SESSION_MAX_REACHED_ERROR
        ):
            logger.warning(
                "Skipping download of file %s as "
                "the maximum duration for an offline session was reached.",
                str(local_file.filename),
            )
            return {
                url: Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.SKIPPED,
                    "Maximum duration for an offline session reached.",
                ),
            }

        if (
            not self._refresh_token_thread.is_alive()
            and self._refresh_token_thread.exit_status
            == RefreshTokenThreadExitStatus.REFRESH_TOKEN_ERROR
        ):
            logger.error(
                "File %s could not be downloaded as there was an error trying to obtain a new access token.",
                str(local_file.filename),
            )
            return {
                url: Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.ERROR,
                    "Could not obtain a new access token to download the file.",
                ),
            }

        return {}

    def download_queue(
        self: Self,
        queue: dict[str, LocalFile],
        *,
        force_download: bool,
    ) -> Results:
        """Download a queue of URLs.

        :param queue: A dict containing as keys URLs of files to download and
            as values LocalFile instances containing metadata about the file that will be downloaded.
        :param force_download: Flag to force the download of files.
        :return: A dict containing as keys files URLs and as values error messages.
        """
        dl_results = {}

        for url in sorted(queue.keys()):
            local_file = queue[url]
            log_prefix = (
                f"{local_file.file_type.capitalize()} {local_file.filename} =>"
            )

            check_result = self._pre_download_checks(
                url, local_file, force_download=force_download
            )
            if check_result:
                dl_results.update(check_result)
                continue

            try:
                logger.info(
                    "%s starting download.",
                    log_prefix,
                )
                self._download(url, local_file, force_download=force_download)
                logger.info(
                    "%s successfully downloaded.",
                    log_prefix,
                )
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.SUCCESS,
                            "File successfully downloaded.",
                        ),
                    },
                )
                # Sleep to simulate a large download.
                if config.DOWNLOAD_WAIT_AFTER_COMPLETE > 0:
                    logger.debug(
                        "Download completed, will sleep %s seconds before moving to the next one.",
                        config.DOWNLOAD_WAIT_AFTER_COMPLETE,
                    )
                    sleep(config.DOWNLOAD_WAIT_AFTER_COMPLETE)

            except requests.RequestException as err:
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.ERROR,
                            "An error occurred while handling the download request.",
                        ),
                    },
                )
                logger.error("%s %s", log_prefix, err)
            except urllib3.exceptions.ReadTimeoutError as err:
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.ERROR,
                            "Read timed out.",
                        ),
                    },
                )
                logger.error("%s %s", log_prefix, err)
            except PrematureDownloadTerminationError as err:
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.ERROR,
                            "Download could not fully finish.",
                        ),
                    },
                )
                logger.error("%s %s", log_prefix, err)
            except FileNotFoundError as err:
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.ERROR,
                            "File was moved or deleted during the download.",
                        ),
                    },
                )
                logger.error("%s %s", log_prefix, err)
            except Exception as err:  # noqa: BLE001
                dl_results.update(
                    {
                        url: Result(
                            local_file.filename,
                            local_file.file_type,
                            Status.ERROR,
                            "An error occurred.",
                        ),
                    },
                )
                logger.error("%s %s", log_prefix, err)

        return dl_results
