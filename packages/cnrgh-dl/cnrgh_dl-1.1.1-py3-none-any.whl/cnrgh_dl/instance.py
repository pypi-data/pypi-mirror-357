from __future__ import annotations

import os
import socket
from pathlib import Path

import psutil
from platformdirs import user_runtime_path

from cnrgh_dl.config import APP_AUTHOR, APP_NAME, APP_VERSION
from cnrgh_dl.exceptions import SingleAppInstanceError
from cnrgh_dl.logger import Logger

logger = Logger.get_instance()


class SingleAppInstance:
    """Context manager ensuring that only one instance of the application runs at a time on a machine.

    When a new instance starts, it checks for the existence of a lockfile.
    The lockfile must contain a fully qualified domain name (FQDN) and a process ID (PID), separated by a space.

    An instance will refuse to start if all the following conditions are met:
        - A valid lockfile is found,
        - The FQDN read from the lockfile matches the current one,
        - The PID read from the lockfile corresponds to a running process,
        - The executable of this process contains 'python',
        - The command line of this process contains 'cnrgh-dl' or 'cnrgh_dl'.

    If at least one of these conditions is not met,
    the instance will start normally and create/overwrite the lockfile with its own FQDN and PID.
    """

    _lockfile_path: Path

    def __init__(self, lockfile_path: Path | None = None) -> None:
        """Initialization of the context manager.

        :param lockfile_path: Path of the lockfile.
            By default, the lockfile is named 'instance.lock' and located in the user runtime directory.
        """
        self._lockfile_path = (
            lockfile_path
            if lockfile_path
            else (
                user_runtime_path(
                    APP_NAME, APP_AUTHOR, APP_VERSION, ensure_exists=True
                )
                / "instance.lock"
            )
        )
        logger.debug("Lockfile path: '%s'.", self._lockfile_path)

    def lock(self) -> None:
        """Ensure that no instance of 'cnrgh-dl' is already running.

        :raises SingleAppInstanceError: An instance is already running.
        """
        if self._lockfile_path.exists():
            try:
                with self._lockfile_path.open(encoding="utf-8") as lf:
                    lf_fqdn, lf_pid = lf.read().strip().split()

                logger.debug("Lockfile FQDN: '%s', PID: '%s'.", lf_fqdn, lf_pid)

                if self._instance_already_running(lf_fqdn, int(lf_pid)):
                    raise SingleAppInstanceError(int(lf_pid))

            except (ValueError, OSError) as e:
                logger.debug(
                    "Error reading lockfile '%s': %s",
                    self._lockfile_path,
                    e,
                )
        else:
            logger.debug("No lockfile found.")

        logger.debug("Creating / overwriting lockfile and starting...")
        self.write_lockfile()

    def release(self) -> None:
        """Ensure that the lockfile is deleted."""
        logger.debug("Deleting lockfile '%s'.", self._lockfile_path)
        self._lockfile_path.unlink(missing_ok=True)

    def write_lockfile(self) -> None:
        """Refresh FQDN and PID in the lockfile.
        Create the lockfile if it does not exist,
        and do not raise a SingleAppInstanceError.
        """
        self._lockfile_path.write_text(
            f"{socket.getfqdn()} {os.getpid()}", encoding="utf-8"
        )

    @staticmethod
    def _instance_already_running(lf_fqdn: str, lf_pid: int) -> bool:
        """Determine if the PID and FQDN found in the lockfile means
        that a 'cnrgh-dl' instance is already running.

        :param lf_fqdn: FQDN read from the lockfile.
        :param lf_pid: PID read from the lockfile.
        :return: True if an instance is already running, False otherwise.
        """
        search_terms = ["cnrgh-dl", "cnrgh_dl"]

        current_fqdn = socket.getfqdn()
        if current_fqdn != lf_fqdn:
            # The lockfile FQDN does not match the current machine FQDN.
            logger.debug(
                "Lockfile FQDN '%s' is different from the current FQDN '%s'.",
                lf_fqdn,
                current_fqdn,
            )
            return False

        try:
            process = psutil.Process(lf_pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(
                "Could not gather data about process with PID '%s': %s",
                lf_pid,
                e,
            )
            # The lockfile PID belongs to a process that do not exist anymore,
            # or to a new process requiring stricter permissions (which is not 'cnrgh-dl').
            return False
        else:
            exe_stem = Path(process.exe()).stem if process.exe() else ""
            if not (exe_stem == "py" or "python" in exe_stem):
                # If the executable path stem is not equal to 'py' nor contains 'python',
                # then the running process is not using a Python interpreter.
                logger.debug(
                    "Process with PID '%s' is not using a Python interpreter.",
                    lf_pid,
                )
                return False

            # Check if the command line of the process contains any occurrence of the searched terms.
            return any(
                term in " ".join(process.cmdline()) for term in search_terms
            )
