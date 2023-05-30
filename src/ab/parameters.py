"""
Module for handling parameters.

"""

from typing import (
    Any,
    Iterable,
)
import itertools as it


def resolved(parameters: dict[str, tuple[Any]]) -> dict[str, Any]:
    """
    Parameter expansion for a mapping with at least one key and a sequence of at
    least one value.

    Example:
    --------
    Given

        {
            'year': [2021, 2022], 'hour': ['01']
        }

    this function returns

        [
            {'year': 2021, 'hour': '01'}, {'year': 2022, 'hour': '01'},
        ]

    Limitations:
    ------------
    The values must be given in a sequence that can be converted to a tuple,
    since Python's dict type only takes immutable keys.

    """
    inverted = {tuple(values): key for (key, values) in parameters.items()}
    return [
        {key: value for (key, value) in zip(parameters.keys(), values)}
        for values in it.product(*inverted.keys())
    ]


def resolvable(
    parameters: dict[str, Iterable[Any]], string_to_format: str
) -> dict[str, Iterable[Any]]:
    """
    Return dict with parameters that are actually employed in formatabale.

    This function exists, because the user may provide more parameters than are
    usable, and the mechanism that expands the dict of parameters and possible
    values to a list of dicts with each possible combination of parameter value
    will provide duplicate file listings when the name is resolved for each
    parameter combination where the difference in parameter value is only in the
    not-used parameter (which is ignored by the .format() method).

    """
    return {
        parameter: values
        for (parameter, values) in parameters.items()
        # Case: 'Whatever comes before {parameter} whatever comes after'
        if f"{{{parameter}}}" in string_to_format
        # Case: 'Whatever comes before {parameter.property} whatever comes after'
        or f"{{{parameter}." in string_to_format
    }
