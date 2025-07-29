import hashlib
from pathlib import Path

from tqdm import tqdm

from cnrgh_dl.logger import Logger
from cnrgh_dl.models import (
    LocalFiles,
    Result,
    Results,
    Status,
)

logger = Logger.get_instance()
"""Module logger instance."""


class Integrity:
    """Class containing methods used to check the integrity of downloaded files."""

    @staticmethod
    def _parse_hash_file(filepath: Path) -> dict[str, str]:
        """Parses an MD5 hash file.

        Each line of the file must contain hash and filename pairs, separated by two spaces as follows:
        ``<MD5 hash>  <filename>``.

        :param filepath: The path of the MD5 file to parse.
        :raises ValueError: If the file is empty or incorrectly formatted.
        :raises OSError: If an error occurred when trying to open the MD5 hash file.
        :return: A dict containing as keys the filenames (for convenience), and as values the corresponding hashes.
        """
        file_content = {}

        with Path.open(filepath) as f:
            lines = f.readlines()

        if len(lines) == 0:
            msg = "Empty file."
            raise ValueError(msg)

        counter = 1
        try:
            for line in lines:
                file_hash, file_name = line.split()
                file_content[file_name] = file_hash
                counter += 1
        except ValueError:
            msg = f"Hash or filename is missing at line {counter}."
            raise ValueError(msg) from None

        return file_content

    @staticmethod
    def _compute_checksum(filepath: Path) -> str:
        """Computes the MD5 checksum of a file.

        :param filepath: The path of the file to compute the checksum for.
        :return: The computed checksum.
        """
        chunk_num_blocks = 128
        h = hashlib.md5()
        file_size = filepath.stat().st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            miniters=1,
            desc=f"{filepath.name} MD5 compute",
            leave=False,
        ) as t:
            with Path.open(filepath, "rb") as f:
                while chunk := f.read(chunk_num_blocks * h.block_size):
                    h.update(chunk)
                    t.update(len(chunk))

            t.update(abs(file_size - t.n))
            t.close()

        return h.hexdigest()

    @staticmethod
    def check(
        file_queue: LocalFiles,
        checksum_queue: LocalFiles,
        dl_results: Results,
    ) -> Results:
        """Check the integrity of downloaded files against their downloaded checksums.

        :param file_queue: Queue of files to download.
        :param checksum_queue: Queue of checksums to download.
        :param dl_results: Dict containing download results.
        :returns: A dict containing as keys file URLs and as values the message returned by the integrity check.
            This dict is only returned for testing purposes.
        """
        res = {}

        for url in sorted(file_queue.keys()):
            checksum_url = f"{url}.md5"
            local_file = file_queue[url]
            local_file_dl_results = dl_results[url]

            # If the file download was skipped or failed, we skip the check.
            if local_file_dl_results.status is not Status.SUCCESS:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.SKIPPED,
                    "Download of the file was skipped / failed.",
                )
                res[url] = ic_res
                logger.warning(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )
                continue

            # If no checksum corresponding to the file was downloaded, we skip the check.
            if checksum_url not in checksum_queue:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.SKIPPED,
                    "No MD5 checksum file available to download.",
                )
                res[url] = ic_res
                logger.warning(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )
                continue

            checksum_dl_results = dl_results[checksum_url]

            # If the checksum download was skipped or failed, we skip the check.
            if checksum_dl_results.status is not Status.SUCCESS:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.SKIPPED,
                    "Download of its MD5 checksum file was skipped / failed.",
                )
                res[url] = ic_res
                logger.warning(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )
                continue

            # Here, we are sure that the file was successfully downloaded along its checksum.
            try:
                # Will raise an OSError if the hash file can't be opened and
                # a ValueError if its badly formatted.
                md5_content = Integrity._parse_hash_file(
                    checksum_queue[checksum_url].path,
                )

                # Will raise a KeyError if the hash file does not contain the current filename.
                is_valid = md5_content[
                    local_file.filename
                ] == Integrity._compute_checksum(local_file.path)

                if is_valid:
                    ic_res = Result(
                        local_file.filename,
                        local_file.file_type,
                        Status.SUCCESS,
                        "The file matches its checksum.",
                    )
                    res[url] = ic_res
                    logger.info(
                        "[%s] %s => %s",
                        ic_res.status.name,
                        ic_res.filename,
                        ic_res.message,
                    )
                else:
                    ic_res = Result(
                        local_file.filename,
                        local_file.file_type,
                        Status.ERROR,
                        "The file does not match its checksum.",
                    )
                    res[url] = ic_res
                    logger.error(
                        "[%s] %s => %s",
                        ic_res.status.name,
                        ic_res.filename,
                        ic_res.message,
                    )

            except OSError as e:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.ERROR,
                    f"Its MD5 checksum file can't be opened: {e}.",
                )
                res[url] = ic_res
                logger.error(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )
            except ValueError as e:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.ERROR,
                    "Its MD5 checksum file is incorrectly formatted: "
                    f"{e} Please report this error to your contact at the CNRGH.",
                )
                res[url] = ic_res
                logger.error(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )
            except KeyError:
                ic_res = Result(
                    local_file.filename,
                    local_file.file_type,
                    Status.ERROR,
                    "Its filename does not appear in the downloaded MD5 checksum file. "
                    "Please report this error to your contact at the CNRGH.",
                )
                res[url] = ic_res
                logger.error(
                    "[%s] %s => %s",
                    ic_res.status.name,
                    ic_res.filename,
                    ic_res.message,
                )

        return res
