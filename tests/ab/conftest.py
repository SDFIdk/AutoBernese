import os
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session", autouse=True)
def environment(tmp_path_factory):

    # Physical environment
    __ab__ = tmp_path_factory.mktemp("__ab__")
    ifname_env = Path(__file__).parent / "test_env.yaml"
    schema = yaml.safe_load(ifname_env.read_text())

    # Create and return the argument to enable single-line assignment and creation
    mkdir = lambda path: path.mkdir(exist_ok=True, parents=True) or path
    touch = lambda fname: fname.touch() or fname

    # Record keeping
    keys_to_remove = []

    # Set environment variables and create directories and files
    for env_var in schema:

        if isinstance(env_var, str):
            path = mkdir(__ab__ / env_var)
            os.environ[env_var] = str(path)
            keys_to_remove.append(env_var)
            continue

        if isinstance(env_var, dict):
            key, value = list(env_var.items())[0]

            if isinstance(value, str):
                os.environ[key] = value
                keys_to_remove.append(key)

            elif isinstance(value, list):
                path = mkdir(__ab__ / key)
                os.environ[key] = str(path)
                keys_to_remove.append(key)
                for fname in value:
                    touch(path / fname)
            continue

        raise RuntimeError("Schema not correctly structured ...")

    # Go test ...
    yield

    # Remove keys to remove
    for key in keys_to_remove:
        del os.environ[key]
