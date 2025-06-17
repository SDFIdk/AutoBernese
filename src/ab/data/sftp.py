"""
Transfer files over SFTP

Built-in command-line too sftp is assumed to exist.

"""

from typing import (
    Any,
    Final,
)
import itertools as it
from pathlib import Path
import subprocess as sub
import logging

from ab.paths import resolve_wildcards
from ab.data import TransferStatus


log = logging.getLogger(__name__)

type LocalRemotePairType = dict[str, Path | str]

PUT: Final = "put {fname} {remote_dir}"


def update_status(
    status: TransferStatus, result: sub.CompletedProcess
) -> TransferStatus:

    if result.returncode == 0:
        status.downloaded += len(result.stdout.splitlines())

    # c = lambda s: s.replace("sftp> ", "")
    # print("stdout:")
    # print(c(result.stdout))

    # print()
    # print("stderr:")
    # print(c(result.stderr))

    # print()
    # print("return code:")
    # print(result.returncode)
    # print("TODO: Check that the files exists on the server ...")
    return status


def upload(host: str, pairs: list[LocalRemotePairType]) -> TransferStatus:
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

    expanded = []
    for raw in pairs:
        filename = raw.get("filename")
        remote_dir = raw.get("remote_dir")

        if filename is None:
            status.failed += 1
            log.warn(f"Local filename is `None` ({remote_dir=}). Skiping entry ...")
            continue

        if remote_dir is None:
            status.failed += 1
            log.warn(f"Remote directory is `None` ({filename=}). Skiping entry ...")
            continue

        resolved = list(resolve_wildcards(filename))
        # No wildcard used and returned file was the same as input which we have to check
        if len(resolved) == 1 and not Path(resolved[0]).is_file():
            status.failed += 1
            continue

        for fname in resolved:
            # Any file paths here exists, since they were resolved by `pathlib`
            expanded.append(dict(fname=fname, remote_dir=remote_dir))
            log.info(f"Added {fname} to SFTP batch upload ({remote_dir=})")

    commands = "\n".join(PUT.format(**pair) for pair in expanded)

    try:
        result = sub.run(
            ["sftp", "-b", "-", host],
            input=commands,
            text=True,
            check=True,
            capture_output=True,
        )
        status = update_status(status, result)

    except sub.CalledProcessError as e:
        status.exceptions.append(e)

    print(status)

    return status
