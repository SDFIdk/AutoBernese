"""
Path constructors

"""

from pathlib import Path

import yaml

from ab.paths import resolve_wildcards


def path_constructor(loader: yaml.Loader, node: yaml.Node) -> Path | list[Path]:
    """
    The path constructor resolves filenames and returns either a single Path
    instance or a list, depending on the number of results.

    The constructor can read input either as 1) a string path or 2) a sequence
    of parts that combine to a path. The reason for the second input option is
    the need for building paths relative to the active installation environment.

    1) Fully specified path strings like the following:

    *   scheme://uniform/ressource/identifier
    *   /some/path/to/somewhere
    *   /some/path/to/some.file

    These values will be parsed as YAML ScalarNode instances, and the
    constructor simply returns a Python Path instance of the entire string
    value.

    Examples of the scalar syntax are:

    ```yaml

    key1: !Path /mnt/server/subdirectory/file.txt

    key2: !Path /mnt/server/subdirectory/*.log

    ```

    ---

    2) A sequence of path components, which is useful when one or more
       components are YAML aliases referring to a string somewhere else in the
       YAML document.

    More complex paths can thus be constructed by supplying the YAML tag with a
    sequence of path elements.

    Here, each sequence item can be either a YAML alias for a value elsewhere in
    the document, or simply a string.

    Examples of the sequence syntax are:

    ```yaml

    key1: !Path [*alias_to_a_base_path, subdirectory, file.txt]

    ```

    Return types
    ------------

    Any element in the path or sequence of path components, may use the common
    wildcard `*` to specify any matching files.

    In this case, the constructor will return not one single Path instance, but
    a list of all matches found, except when only one result is found. In that
    case that single Path instance is returned.

    However, if the wildcard is used as the first character of the first
    element, it must be explicitly written as a string to prevent the YAML
    parser from interpreting it as an alias to a YAML anchor.

    """
    if not isinstance(node, (yaml.ScalarNode, yaml.SequenceNode)):
        raise KeyError(
            f"Must be single string or list of strings or `Path` instances. Got {node.value!r} ..."
        )

    if isinstance(node, yaml.ScalarNode):
        raw = loader.construct_scalar(node)
        if not isinstance(raw, str):
            raise RuntimeError(f"Expected {raw!r} to be a string.")
        path: Path = Path(raw)
    else:
        # We use loader.construct_object, since there may be YAML aliases inside.
        multiple: list[str | Path] = [loader.construct_object(v) for v in node.value]
        path = Path(*multiple)

    # Avoid relative paths `dir/../dir2`
    path = path.absolute()

    resolved = list(resolve_wildcards(path))

    if not resolved:
        EnvironmentError(f"Path {path!r} could not be resolved.")

    if len(resolved) > 1:
        return resolved

    return resolved[0]


def path_as_str_constructor(loader: yaml.Loader, node: yaml.Node) -> str | list[str]:
    paths = path_constructor(loader, node)
    if isinstance(paths, list):
        return [str(path) for path in paths]
    return str(paths)


def parent_constructor(loader: yaml.Loader, node: yaml.Node) -> Path | list[Path]:
    """
    Returns the parent directory of the path given.

    Expected input is the same as for path_contructor.

    """
    paths = path_constructor(loader, node)
    # There is no usecase for returning multiple parent directories, since, at
    # worst, this will be ambiguous or have duplicates.
    # if isinstance(paths, list):
    #     return [path.parent for path in paths]
    if not isinstance(paths, Path):
        raise ValueError(
            f"Expected single path to return parent directory for. Got {paths!r} ..."
        )
    return paths.parent
