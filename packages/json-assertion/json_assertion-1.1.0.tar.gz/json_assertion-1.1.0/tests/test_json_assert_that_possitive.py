from dataclasses import dataclass
from typing import Any, Final

import pytest
from json_assertion import json_assert_that


@dataclass
class Case:
    name: str
    expression: str | list[str]
    expected_result: bool = True


cases: Final[list[Case]] = [
    Case(
        name="contains_substring_single",
        expression="contains(long_string, 'very long')",
    ),
    Case(
        name="contains_substring_multiple",
        expression=[
            "contains(long_string, 'very long')",
            "contains(long_string, 'This')",
        ],
    ),
    Case(
        name="contains_substring_not_found",
        expression="contains(long_string, 'not found')",
        expected_result=False,
    ),
    Case(name="extended_functions_any", expression="any(any_field[0])"),
    Case(
        name="extended_functions_any_false",
        expression="any(any_field[1])",
        expected_result=False,
    ),
    Case(
        name="extended_functions_any_empty",
        expression="any(any_field[2])",
        expected_result=False,
    ),
    Case(name="extended_functions_all", expression="all(all_field[0])"),
    Case(
        name="extended_functions_all_false",
        expression="all(all_field[1])",
        expected_result=False,
    ),
    Case(
        name="extended_functions_all_empty",
        expression="all(all_field[2])",
        expected_result=True,
    ),
]


@pytest.mark.parametrize(
    "case",
    cases,
    ids=[case.name for case in cases],
)
def test_json_assert_that(json_content: str, case: Case) -> None:
    assert (
        json_assert_that(
            json_content,
            case.expression,
        )
        == case.expected_result
    )


@pytest.mark.parametrize(
    "case",
    cases,
    ids=[case.name for case in cases],
)
def test_json_assert_that_data(json_data: Any, case: Case) -> None:
    assert (
        json_assert_that(
            json_data,
            case.expression,
        )
        == case.expected_result
    )
