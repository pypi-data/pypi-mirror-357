from __future__ import annotations

import atexit
import os
import signal
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from cnrgh_dl.logger import Logger

if TYPE_CHECKING:
    from types import FrameType

    from cnrgh_dl.instance import SingleAppInstance


logger = Logger.get_instance()
"""Module logger instance."""


def child_handler(
    instance: SingleAppInstance,
    signum: int,
    frame: FrameType | None,  # noqa: ARG001
) -> None:
    """Exit the parent process based on the signals sent by the child process.

    :raises SystemExit: the parent process exited.
    """
    if signum == signal.SIGALRM:
        msg = f"Parent process received signal {signal.Signals(signum).name} as child did not respond in time."
        logger.error(msg)
        raise SystemExit(msg)
    if signum == signal.SIGCHLD:
        msg = f"Parent process received signal {signal.Signals(signum).name} as child died prematurely."
        logger.error(msg)
        raise SystemExit(msg)
    if signum == signal.SIGUSR1:
        logger.debug(
            "Parent process has received signal %s as child started successfully. "
            "Lockfile will not be deleted; it will be / has been overwritten by child process.",
            signal.Signals(signum).name,
        )
        # Do not delete the lockfile, the child process will refresh it with its own PID.
        atexit.unregister(instance.release)

        logger.info("Successfully daemonized, exiting...")
        raise SystemExit(0)


def daemonize(instance: SingleAppInstance) -> None:
    """cnrgh-dl will detach itself from the controlling terminal and run in the background as a daemon.

    Resources used for implementation:
        - `How to Daemonize in Linux <https://web.archive.org/web/20180223192524/http://www.itp.uzh.ch/~dpotter/howto/daemonize>`__,
        - `Advanced Programming in the UNIX Environment, Third Edition - Chapter 13: Daemon process <https://en.wikipedia.org/wiki/Advanced_Programming_in_the_Unix_Environment>`__,
        - `UNIX daemonization and the double fork <https://0xjet.github.io/3OHA/2022/04/11/post.html>`__.

    :raises SystemExit: an error occurred while trying to daemonize the process.
    """
    logger.info("Attempting to daemonize...")

    try:
        if os.getppid() == 1:
            logger.debug(
                "cnrgh-dl is already a daemon (parent is init process)."
            )
            return

        # Trap signals that we expect to receive.
        signal.signal(signal.SIGCHLD, partial(child_handler, instance))
        signal.signal(signal.SIGUSR1, partial(child_handler, instance))
        signal.signal(signal.SIGALRM, partial(child_handler, instance))

        # Fork to create a child process and exit the parent process.
        if os.fork() > 0:
            logger.debug("Parent process is waiting for child to start.")

            # Parent waits for a SIGUSR1 from the child or SIGALRM after 5 seconds.
            signal.alarm(5)  # Trigger SIGALRM if child doesn't respond in time.
            signal.pause()  # Wait indefinitely for signals

            # This exit will never be reached, as signal.pause() should never return.
            msg = "The 'signal.pause()' function returned when it never should have."
            logger.error(msg)
            raise SystemExit(msg)

        # Executing in the child process now.
        parent_pid = os.getppid()  # Get parent PID (needed to notify parent).
        logger.debug(
            "Child process with PID %s was created from parent with PID %s.",
            os.getpid(),
            parent_pid,
        )

        # Reset signals behavior.
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

        # Ignore signals.
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
        signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        signal.signal(signal.SIGTTIN, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        # Set the file mode creation mask to a known value.
        os.umask(0)

        # Create a new session ID, detaching the child from the terminal and parent.
        os.setsid()

        # Change the working directory to avoid locking the current directory
        # (all paths used in the daemon should be absolute).
        os.chdir("/")

        # Redirect standard input/output/error streams to /dev/null.
        with Path("/dev/null").open(mode="r+") as devnull:
            for stream_fd in range(3):
                os.dup2(devnull.fileno(), stream_fd)

        # Notify the parent process that the child is ready (SIGUSR1).
        logger.debug(
            "Child process is ready. Notifying parent with SIGUSR1 signal."
        )
        os.kill(parent_pid, signal.SIGUSR1)

        # Here, parent process has exited with success without handling the lockfile deletion.
        # The child should overwrite it with its own PID (the FQDN is unchanged).
        logger.debug(
            "Child process is overwriting parent lockfile with its own PID..."
        )
        instance.write_lockfile()

        logger.debug(
            "Child is starting to process the download queue in background..."
        )

    except OSError as e:
        msg = f"An error occurred while trying to daemonize the process: {e}"
        logger.error(msg)
        raise SystemExit(msg) from None
