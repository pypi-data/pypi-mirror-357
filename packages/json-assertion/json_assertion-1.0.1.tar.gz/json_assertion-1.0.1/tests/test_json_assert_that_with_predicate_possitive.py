from dataclasses import dataclass
from typing import Final

import pytest
from json_assertion import Predicate, json_assert_that_with_predicate


@dataclass
class Case:
    name: str
    expression: str
    predicate: Predicate | list[Predicate]
    expected_result: bool = True


cases: Final[list[Case]] = [
    Case(
        name="contains_substring_single",
        expression="long_string",
        predicate=lambda s: "very long" in s,
    ),
    Case(
        name="contains_substring_multiple",
        expression="long_string",
        predicate=[
            lambda s: "very long" in s,
            lambda s: "This" in s,
        ],
    ),
    Case(
        name="mismatch",
        expression="long_string",
        predicate=lambda s: "not in there" in s,
        expected_result=False,
    ),
    Case(
        name="list_expression_predicate",
        expression="any_field[0]",
        predicate=lambda v: v,
    ),
    Case(
        name="list_expression_predicate_false",
        expression="any_field[1]",
        predicate=lambda v: v,
        expected_result=False,
    ),
    Case(
        name="list_expression_predicate_empty",
        expression="any_field[2]",
        predicate=lambda v: v,
        expected_result=False,
    ),
    Case(
        name="double_list_expression_predicate",
        expression="all_field[0]",
        predicate=[
            lambda v: v,
            lambda v: v,
        ],
    ),
    Case(
        name="double_list_expression_predicate_false",
        expression="all_field[0]",
        predicate=[
            lambda v: v,
            lambda v: not v,
        ],
        expected_result=False,
    ),
]


@pytest.mark.parametrize(
    "case",
    cases,
    ids=[case.name for case in cases],
)
def test_json_assert_that_with_predicate(json_content: str, case: Case) -> None:
    assert (
        json_assert_that_with_predicate(
            json_content,
            case.expression,
            case.predicate,
        )
        == case.expected_result
    )
