import argparse
import os
from importlib.metadata import version
from pathlib import Path

from cnrgh_dl.logger import Logger
from cnrgh_dl.utils import (
    read_urls_from_file,
    read_urls_from_stdin,
)

logger = Logger.get_instance()
"""Module logger instance."""


def get_args() -> argparse.Namespace:
    """Parses the arguments needed by the program.

    :return: A Namespace object holding parsed arguments and their values.
    """
    parser = argparse.ArgumentParser(
        prog="cnrgh-dl",
        description="Python client for downloading CNRGH project data.",
    )
    parser.add_argument(
        "outdir",
        type=Path,
        help="Output directory where downloaded files are stored.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {version(__package__)}",
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=Path,
        help="Path to a file containing a list of URLs to download (one per line). "
        "Without this argument, cnrgh-dl will run in 'interactive' mode and "
        "ask for a list of files to download via the standard input.",
    )
    parser.add_argument(
        "--no-integrity-check",
        action="store_true",
        help="By default, cnrgh-dl will check the integrity of each downloaded file if "
        "its checksum file is present in the download queue. Using this option will disable this behavior: "
        "the integrity of downloaded files will not be checked.",
    )
    parser.add_argument(
        "--no-additional-checksums",
        action="store_true",
        help="By default, cnrgh-dl will try to download additional checksums for "
        "files in the download queue. "
        "If a file is listed in the queue without its checksum, "
        "cnrgh-dl will automatically download its checksum "
        "if it exists on the datawebnode server. "
        "If the checksum of a file is not available on the server, "
        "the verification will fail with the following message: "
        "'No corresponding MD5 file found.'. Using this option will disable this behavior: "
        "only the files explicitly listed in the download queue will be downloaded.",
    )
    parser.add_argument(
        "-f",
        "--force-download",
        action="store_true",
        help="By default, cnrgh-dl will skip the download of a file "
        "if it is already present in the output directory. "
        "If a file is partially downloaded (e.i. its filename is prefixed by '.part'), its download will continue. "
        "Using this option will re-download all files already present in the output directory, "
        "whether their download is complete or partial.",
    )
    parser.add_argument(
        "-j",
        "--json-report",
        action="store_true",
        help="Generates a JSON-formatted report containing the status of the downloaded files, "
        "as well as the status of their integrity check. The report is saved in the output directory 'outdir'.",
    )
    parser.add_argument(
        "-b",
        "--background",
        action="store_true",
        help="Processes the download queue in the background. "
        "Once the arguments have been validated, the user authenticated, "
        "and (in interactive mode) the list of URLs entered, cnrgh-dl exits after launching a "
        "background process (daemon) responsible for handling the download queue independently. "
        "This process is detached from the terminal, allowing downloads to continue even if the terminal "
        "is closed or the user is disconnected (e.g. due to SSH logout or network issues). "
        "It is recommended to use this option in conjunction with '-j' / '--json-report' so that "
        "the background process generates a download report upon completion. "
        "This option is not supported on Windows.",
    )
    return parser.parse_args()


def check_args(args: argparse.Namespace) -> argparse.Namespace:
    # All paths provided as options are resolved to absolute paths.
    # This is because in background mode, the child process current working directory is set to '/'
    # and relative directories won't point to the correct entries anymore.

    if args.background and os.name == "nt":
        msg = "Background mode is not supported on a Windows system."
        logger.error(msg)
        raise SystemExit(msg)

    # Check the validity of the output directory: ensure that the path exist and
    # that it points to a directory.
    try:
        outdir = args.outdir.expanduser().resolve(strict=True)
    except FileNotFoundError:
        msg = f"Output path '{args.outdir}' does not exists."
        logger.error(msg)
        raise SystemExit(msg) from None

    if not outdir.is_dir():
        msg = f"Output path '{args.outdir}' does not point to a directory."
        logger.error(msg)
        raise SystemExit(msg)

    args.outdir = outdir  # Override variable with new value.

    # Check the validity of the input file path: if provided,
    # ensure that it points to a file that contains at least one URL.
    # Otherwise, ask for files URLs from stdin.
    if args.input_file:
        try:
            input_file = args.input_file.expanduser().resolve(strict=True)
        except FileNotFoundError:
            msg = f"Input path '{args.input_file}' does not exists."
            logger.error(msg)
            raise SystemExit(msg) from None

        if not input_file.is_file():
            msg = f"Input path '{args.input_file}' does not point to a file."
            logger.error(msg)
            raise SystemExit(msg)

        args.input_file = input_file  # Override variable with new value.
        args.urls = read_urls_from_file(args.input_file)
    else:
        args.urls = read_urls_from_stdin()

    if len(args.urls) == 0:
        msg = "Empty list of files to download."
        logger.error(msg)
        raise SystemExit(msg)

    return args
