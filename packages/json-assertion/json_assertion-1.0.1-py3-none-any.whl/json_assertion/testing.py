import json
from collections.abc import Callable, Iterable
from functools import cache
from typing import Any

import jmespath
import jmespath.exceptions
from jmespath.functions import Functions, signature

__all__ = [
    "Predicate",
    "json_assert_that",
    "json_assert_that_with_predicate",
]

Predicate = Callable[[Any], bool]


class _ExtendedFunctions(Functions):
    @signature({"types": ["array"]})
    def _func_any(self, array: list[Any]) -> bool:
        return any(array)

    @signature({"types": ["array"]})
    def _func_all(self, array: list[Any]) -> bool:
        return all(array)


def json_assert_that(
    json_data_document: Any,
    expression: str | list[str],
) -> bool:
    """Asserts that the provided JSON document matches the expected structure.

    Args:
        json_data_document (Any): The JSON document to be evaluated.
        expression (str | list[str]): The JMESPath expression(s) used.
                                      In this function this expects the JMESPath to return a boolean value.

    Raises:
        TypeError: when the extracted data is not a boolean.

    Returns:
        bool: the result of the JMESPath expression evaluation.
    """
    if not isinstance(expression, list):
        expression = [expression]

    extracted_data = [
        _search_expression(_coerce_json(data=json_data_document), expr)
        for expr in expression
    ]

    if any(not isinstance(data, bool) for data in extracted_data):
        raise TypeError(
            f"Extracted data from expression '{expression}' is not a boolean: {extracted_data}.",
        )
    return all(extracted_data)


def json_assert_that_with_predicate(
    json_data_document: Any,
    extract_expression: str,
    predicate: Predicate | list[Predicate],
) -> bool:
    """Asserts that the synthesized output matches the expected structure using a predicate.

    If the extracted data is a list, the predicate will be applied to each item in the list,
    and return True if any item satisfies the predicate.
    If a list of predicates is provided, all predicates must return True for the assertion to pass.

    Args:
        json_data_document (Any): The JSON document to be evaluated.
        extract_expression (str): The JMESPath expression used to extract data.
        predicate (Predicate | list[Predicate]): A function or list of functions that return a boolean.

    Returns:
        bool: The result of applying the predicate to the extracted data.
    """
    extracted_data = _search_expression(
        _coerce_json(data=json_data_document),
        extract_expression,
    )

    if isinstance(extracted_data, Iterable) and not isinstance(extracted_data, str):
        return any(_apply_predicate(item, predicate) for item in extracted_data)

    return _apply_predicate(extracted_data, predicate)


def _apply_predicate(
    data: Any,  # noqa: ANN401
    predicate: Predicate | list[Predicate],
) -> bool:
    if isinstance(predicate, list):
        return all(p(data) for p in predicate)
    return predicate(data)


@cache
def _json_decode(data: str) -> Any:
    try:
        return json.loads(data)
    except json.JSONDecodeError as ex:
        raise ValueError("The Provided JSON is not valid.") from ex


def _coerce_json(data: Any) -> Any:  # noqa: ANN401
    if isinstance(data, str):
        return _json_decode(data)
    return data


def _search_expression(
    obj: Any,
    expression: str,
) -> Any:  # noqa: ANN401
    try:
        return jmespath.search(
            expression,
            obj,
            options=jmespath.Options(custom_functions=_ExtendedFunctions()),
        )
    except jmespath.exceptions.LexerError as ex:
        raise ValueError(f"Invalid JMESPath expression syntax: {expression}") from ex
    except jmespath.exceptions.JMESPathTypeError as ex:
        raise ValueError(f"Invalid JMESPath expression: {expression}") from ex
    except jmespath.exceptions.JMESPathError as ex:
        raise ValueError(f"Error processing JMESPath expression: {expression}") from ex
