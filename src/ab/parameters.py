"""
Resolve parameterised strings

"""

from typing import Any
from collections.abc import Iterable
import itertools as it


type ArgumentsType = dict[str, Any]
type ParametersType = dict[str, Iterable[Any]]
type PermutationType = dict[str, Any]


def permutations(parameters: ParametersType) -> list[PermutationType]:
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
    inverted: dict[tuple[Any], str] = {
        tuple(values): key for (key, values) in parameters.items()
    }
    return [
        {key: value for (key, value) in zip(parameters.keys(), values)}
        for values in it.product(*inverted.keys())
    ]


def resolvable(parameters: ParametersType, string_to_format: str) -> ParametersType:
    """
    Remove keys in parameters that are not present in string to format.

    A user may provide more parameters than are used in the string to format.

    Since the mechanism expanding the parameters and possible values
    to a list of dicts with each possible permutation of parameter value will
    provide duplicate file listings when the name is resolved for each parameter
    permutation where the difference in parameter value is only in the not-used
    parameter (which is ignored by the .format() method).

    """
    return {
        parameter: values
        for (parameter, values) in parameters.items()
        # Case: 'String with {parameter} whatever comes after'
        if f"{{{parameter}}}" in string_to_format
        # Case: 'String with {parameter.property} whatever comes after'
        or f"{{{parameter}." in string_to_format
    }


def resolve(
    arguments: ArgumentsType, parameters: ParametersType
) -> list[ArgumentsType]:
    """
    Returns a list of dictionaries with the argument names as keys and the
    corresponding values all possible permutation of the given parameters.

    """
    if not parameters:
        return [arguments]

    return [
        {key: format_strings(value, permutation) for (key, value) in arguments.items()}
        for permutation in permutations(parameters)
    ]


def format_strings(structure: Any, permutation: PermutationType) -> Any:

    if isinstance(structure, dict):
        return {
            key: format_strings(value, permutation)
            for (key, value) in structure.items()
        }

    if isinstance(structure, list):
        return [format_strings(value, permutation) for value in structure]

    if isinstance(structure, str):
        return structure.format_map(permutation)

    return structure
