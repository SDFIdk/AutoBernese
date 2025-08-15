"""
Transfer files over SFTP

Built-in command-line too sftp is assumed to exist.

"""

from typing import Final
from collections.abc import Iterable
from dataclasses import (
    dataclass,
    asdict,
)
import itertools as it
from pathlib import Path
import subprocess as sub  # type: ignore
import logging

from ab.paths import (
    resolve_wildcards,
    _parents,
)
from ab.data import TransferStatus


log = logging.getLogger(__name__)

type LocalRemoteType = dict[str, Path | str]
"Type for local file and remote directory as dict"

MKDIR: Final = "-mkdir {remote_dir}"
"SFTP-command structure for making a directory with a prefixed hyphen to suppress errors."

PUT: Final = "put {fname} {remote_dir}"
"SFTP-command structure for transfering a file to a remote directory"


@dataclass
class LocalRemote:
    fname: str | Path | None = None
    remote_dir: str | Path | None = None

    @property
    def valid(self) -> bool:
        if self.fname is None:
            return False

        if self.remote_dir is None:
            return False

        return True

    def resolve_local(self) -> list["LocalRemote"]:
        if not self.valid:
            return []

        # NOTE: type comment avoids MyPy complaining about type of `self.fname`
        # which `self.valid` has already made sure is note the case.
        return [
            LocalRemote(resolved, self.remote_dir)
            for resolved in resolve_wildcards(self.fname)  # type: ignore
        ]


def _mkdir_commands(paths: Iterable[str]) -> list[str]:
    """
    Return list of commands to create each full path, part by part.

    """
    return [
        MKDIR.format(remote_dir=part)
        for unique in sorted(set(paths))
        for part in _parents(unique)
    ]


def update_status(
    status: TransferStatus, result: sub.CompletedProcess
) -> TransferStatus:
    """
    Assuming that each line is a successful transfer message, when the return
    code is zero.

    NOTE: This is not accounting for any failures.

    """
    if result.returncode == 0:
        status.success += len(result.stdout.splitlines())
    return status


def _batch(host: str, commands: str) -> sub.CompletedProcess:
    return sub.run(
        ["sftp", "-b", "-", host],
        input=commands,
        text=True,
        check=True,
        capture_output=True,
    )


def upload(host: str, pairs: list[LocalRemoteType]) -> TransferStatus:
    """
    Using settings provided, upload pairs of local file/remote destination
    directory.

    Provided host string must be a `Host` in running user's SSH config file.

    Host settings must provide needed host details and credentials for the
    connection.

    If '*' wildcards are used for the local file, these are expanded.

    No wildcards can be used for the destination directory. This would be
    ambiguous for files with wildcards, and, presumably, redundant, if concrete
    files are to be put into more than one destination directory.

    """
    log.info(f"Uploading files to {host} using SFTP ...")

    status = TransferStatus()

    log.info("Build LocalRemote instances from input ...")
    candidates = [LocalRemote(**pair) for pair in pairs]

    log.info("Get usable input (valid dict structure) ...")
    extracted = [candidate for candidate in candidates if candidate.valid]
    status.failed += len(candidates) - len(extracted)

    log.info("Get all local filenames ...")
    resolvable = [
        resolved
        for candidate in extracted
        if len(resolved := candidate.resolve_local())
    ]
    status.failed += len(resolvable) - len(extracted)
    resolved = list(it.chain(*resolvable))

    log.info(f"Prepare commands to build remote directory tree ...")
    remote_dirs = [str(lr.remote_dir) for lr in resolved]
    cmd_mkdir = "\n".join(_mkdir_commands(remote_dirs))

    log.info("Prepare commands to transfer local files to remote directories ...")
    cmd_put = "\n".join(PUT.format(**asdict(lr)) for lr in resolved)

    try:
        log.info(f"Batch-create directories on {host} ...")
        result = _batch(host, cmd_mkdir)
        status = update_status(status, result)

        log.info(f"Batch-transfer local files to {host} ...")
        result = _batch(host, cmd_put)
        status = update_status(status, result)

    except sub.CalledProcessError as e:
        log.warn(f"Subprocess failed with error {e}")
        status.exceptions.append(e)

    log.info(status)
    return status
