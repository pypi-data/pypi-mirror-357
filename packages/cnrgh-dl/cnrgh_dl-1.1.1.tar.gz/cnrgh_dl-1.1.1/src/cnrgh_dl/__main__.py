from __future__ import annotations

import atexit
import dataclasses
from collections import defaultdict
from enum import Enum

import requests

from cnrgh_dl.args import check_args, get_args
from cnrgh_dl.auth.refresh_token import RefreshTokenThread
from cnrgh_dl.config import LOG_SAVE_FILE
from cnrgh_dl.daemon import daemonize
from cnrgh_dl.download.downloader import Downloader
from cnrgh_dl.download.integrity import Integrity
from cnrgh_dl.download.queue import find_partial_downloads, init_queue
from cnrgh_dl.download.url import DownloadURL
from cnrgh_dl.exceptions import SingleAppInstanceError
from cnrgh_dl.instance import SingleAppInstance
from cnrgh_dl.logger import Logger
from cnrgh_dl.models import (
    LocalFiles,
    Result,
    Results,
    Status,
)
from cnrgh_dl.utils import (
    check_for_update,
    log_config,
    log_system_info,
    write_json_report,
)

logger = Logger.get_instance()
"""Module logger instance."""


def start_download(
    downloader: Downloader,
    file_queue: LocalFiles,
    checksum_queue: LocalFiles,
    *,
    force_download: bool,
) -> Results:
    """Start the download of files and then checksums.

    :param downloader: A download instance.
    :param file_queue: Queue of files to download.
    :param checksum_queue: Queue of checksums to download.
    :param force_download: Flag to force the download of files.
    :return: A dict containing download results.
    """
    dl_results = {}

    if len(file_queue) > 0:
        logger.info("==============")
        logger.info("FILES DOWNLOAD")
        logger.info("==============")
        dl_results.update(
            downloader.download_queue(
                file_queue,
                force_download=force_download,
            ),
        )

    if len(checksum_queue) > 0:
        logger.info("===========================")
        logger.info("MD5 CHECKSUM FILES DOWNLOAD")
        logger.info("============================")
        dl_results.update(
            downloader.download_queue(
                checksum_queue,
                force_download=force_download,
            ),
        )

    return dl_results


def start_integrity_check(
    file_queue: LocalFiles,
    checksum_queue: LocalFiles,
    dl_results: Results,
) -> Results | None:
    """Start the integrity check of downloaded files by computing their checksums and
    comparing them with the downloaded ones if they exist.

    :param file_queue: Queue of files to download.
    :param checksum_queue: Queue of checksums to download.
    :param dl_results: Dict containing download results.
    """
    logger.info("===============")
    logger.info("INTEGRITY CHECK")
    logger.info("===============")

    if len(file_queue) == 0:
        logger.warning(
            "Skipped the integrity check: there is no files to check.",
        )
        return None

    if len(checksum_queue) == 0:
        logger.warning(
            "Skipped the integrity check: there is no checksums to validate files against.",
        )
        return None

    return Integrity.check(file_queue, checksum_queue, dl_results)


def start_additional_checksum_download(
    downloader: Downloader,
    file_queue: LocalFiles,
    checksum_queue: LocalFiles,
    *,
    force_download: bool,
) -> tuple[Results, LocalFiles]:
    """Retrieve and download additional MD5 checksum files from the server.

    For each project represented in the file queue, this function checks if
    there are any additional MD5 checksum files on the server that are not
    already present in the checksum queue. If found, these checksum
    files are downloaded to help verify the integrity of the corresponding
    files.

    :param downloader: An instance responsible for downloading files.
    :param file_queue: Queue of files scheduled for download.
    :param checksum_queue: Queue of MD5 checksum files scheduled for download.
    :param force_download: Whether to force re-download of files even if they
        exist locally.
    :return: A tuple where the first element is a dictionary mapping file URLs
        to error messages encountered during download, and the second element
        is a queue of the additional MD5 checksum files that were found and
        downloaded.
    """
    logger.info("======================================")
    logger.info("ADDITIONAL MD5 CHECKSUM FILES DOWNLOAD")
    logger.info("======================================")

    dl_results = {}
    additional_checksum_queue = {}

    urls_by_project = defaultdict(set)
    for url in file_queue:
        project_name = DownloadURL.get_project_name(url)
        urls_by_project[project_name].add(url)

    for project_name, file_urls in urls_by_project.items():
        logger.info(
            "Project %s: "
            "looking for additional MD5 checksum files to download...",
            project_name,
        )
        try:
            project_additional_checksums = (
                downloader.fetch_additional_checksums(
                    project_name, file_urls, set(checksum_queue.keys())
                )
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                "Project %s: failed to retrieve its file list from "
                "the server, preventing the identification of additional MD5 "
                "checksum files to download: %s",
                project_name,
                e,
            )
            continue

        if len(project_additional_checksums) > 0:
            logger.info(
                "Project %s: found %s additional MD5 checksum file(s) to download.",
                project_name,
                len(project_additional_checksums),
            )
            dl_results.update(
                downloader.download_queue(
                    project_additional_checksums,
                    force_download=force_download,
                ),
            )
            additional_checksum_queue.update(project_additional_checksums)
        else:
            logger.info(
                "Project %s: found no additional MD5 checksum files to download.",
                project_name,
            )

    return dl_results, additional_checksum_queue


def print_download_recap(
    file_queue: LocalFiles,
    checksum_queue: LocalFiles,
    dl_results: Results,
) -> None:
    """Print a recap after all the files have been downloaded.

    :param file_queue: Queue of files to download.
    :param checksum_queue: Queue of checksums to download.
    :param dl_results: Dict containing download results.
    """
    checksum_filenames = set(checksum_queue.keys())
    filenames = set(file_queue.keys())
    checksum_count = 0
    file_count = 0
    error_count = 0

    for url, result in dl_results.items():
        if result.status == Status.ERROR:
            error_count += 1
            continue

        if result.status == Status.SUCCESS:
            if url in checksum_filenames:
                checksum_count += 1
            if url in filenames:
                file_count += 1

    logger.info(
        "Downloaded %d of %d file(s), "
        "%d of %d checksum(s) and encountered %d error(s).",
        file_count,
        len(file_queue),
        checksum_count,
        len(checksum_queue),
        error_count,
    )


def print_download_summary(dl_results: Results) -> None:
    """Print the download summary.

    :param dl_results: Dict containing download results.
    """
    logger.info("================")
    logger.info("DOWNLOAD SUMMARY")

    format_string = ""
    full_tab_width = 0
    columns_margin = 3
    table_lines: list[list[str]] = []
    fields = [field.name for field in dataclasses.fields(Result)]

    # Create a list containing the lines of the table to print.
    for index, dl_result in enumerate(dl_results.values()):
        table_lines.append([])
        for field in fields:
            field_value = dl_result.__dict__[field]
            if isinstance(field_value, Enum):
                table_lines[index].append(field_value.value)
            else:
                table_lines[index].append(field_value)

    # Transform fields into table headers.
    headers = [field.replace("_", " ") for field in fields]

    # For each table column, we compute its maximum value length (including its header).
    for index in range(len(headers)):
        # Compute the length of all the column values and its header.
        values_length = [len(line[index]) for line in table_lines]
        values_length.append(len(headers[index]))
        # Get the maximum value length.
        width = max(values_length) + columns_margin
        # Create a format string for this column.
        format_string += "{:<" + str(width) + "}"
        full_tab_width += width

    logger.info("=" * full_tab_width)
    logger.info(format_string.format(*headers))
    logger.info("-" * full_tab_width)

    # Print the table lines with the corresponding level.
    for index, dl_result in enumerate(dl_results.values()):
        if dl_result.status is Status.ERROR:
            logger.error(format_string.format(*table_lines[index]))
        elif dl_result.status is Status.SKIPPED:
            logger.warning(format_string.format(*table_lines[index]))
        else:
            logger.info(format_string.format(*table_lines[index]))

    logger.info("=" * full_tab_width)


def run() -> int:
    """Main function of ``cnrgh-dl``.
    Depending on the presence and the value of the parsed
    command line arguments, it runs the corresponding functions.

    :raises SingleAppInstanceError: An instance of 'cnrgh-dl' is already running.
    """
    log_system_info()
    log_config()

    # Parse arguments.
    args = get_args()
    logger.debug("CLI args: %s", args)

    check_for_update()
    logger.info("Logs are saved to %s", LOG_SAVE_FILE)

    # Use the SingleAppInstance class to create a lockfile, ensuring that only one instance
    # of 'cnrgh-dl' runs at a time. The lockfile is created after argument parsing, allowing
    # commands like '--help' or '--version' (which exit immediately) to run even if another
    # instance is already active.
    instance = SingleAppInstance()
    # Lock the current instance, and register a handler to release it at exit.
    instance.lock()
    atexit.register(instance.release)

    # At this point, the lockfile is in effect, ensuring that only one instance is running.
    # We now validate the arguments and, if in interactive mode, prompt the user to enter URLs to download.
    args = check_args(args)
    logger.debug("URLs list: %s", args.urls)

    # Then, start the device flow, print the 'user code' provided by Keycloak and
    # wait for the user to authenticate.
    refresh_token_thread = RefreshTokenThread()

    # We are now ready to start processing the downloads.
    # As there will be no more user interaction needed,
    # we can now run in background mode if asked.
    if args.background:
        daemonize(instance)

    # If we are running in background mode,
    # then from this point on the code is executed by the child process.

    # Start a thread that will periodically refresh the access and refresh tokens,
    # and finally and start processing the download queue.
    refresh_token_thread.start()
    downloader = Downloader(refresh_token_thread, args.outdir)

    partially_downloaded_files = find_partial_downloads(args.urls, args.outdir)
    if not args.force_download and len(partially_downloaded_files) > 0:
        logger.warning(
            "Some files in the download queue are already present in the output folder but are incomplete. "
            "Their download will be continued.",
        )

        for file in partially_downloaded_files:
            logger.warning("'%s': incomplete download.", file)

    file_queue, checksum_queue = init_queue(
        args.urls,
        args.outdir,
        partially_downloaded_files,
    )

    dl_results = start_download(
        downloader,
        file_queue,
        checksum_queue,
        force_download=args.force_download,
    )

    if not args.no_additional_checksums:
        results, additional_checksums = start_additional_checksum_download(
            downloader,
            file_queue,
            checksum_queue,
            force_download=args.force_download,
        )
        # Update global results and checksum queue.
        dl_results.update(results)
        checksum_queue.update(additional_checksums)

    # All downloads are finished, stop the refresh thread.
    refresh_token_thread.terminate()

    print_download_summary(dl_results)
    print_download_recap(file_queue, checksum_queue, dl_results)

    integrity_check_results = None
    if not args.no_integrity_check:
        integrity_check_results = start_integrity_check(
            file_queue, checksum_queue, dl_results
        )

    if args.json_report:
        write_json_report(args.outdir, dl_results, integrity_check_results)

    # Return True (=1) if any download failed - used as error status code.
    # Return False (=0) if all downloads succeeded or were skipped.
    return any(
        dl_result.status == Status.ERROR for dl_result in dl_results.values()
    )


def main() -> int:
    try:
        return run()
    except SingleAppInstanceError as e:
        logger.error(e)
        raise SystemExit(e) from None


if __name__ == "__main__":
    raise SystemExit(main())
