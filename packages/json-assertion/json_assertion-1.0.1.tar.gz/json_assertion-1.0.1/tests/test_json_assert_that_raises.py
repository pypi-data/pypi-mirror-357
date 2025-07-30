from dataclasses import dataclass
from typing import Final

import pytest
from json_assertion import json_assert_that


def test_json_assert_that_invalid_json() -> None:
    with pytest.raises(ValueError, match="The Provided JSON is not valid."):
        json_assert_that("invalid json", "contains(long_string, 'test')")


@dataclass
class Case:
    name: str
    expression: str | list[str]
    raised_type: type[Exception]
    content_match: str | None = None


cases: Final[list[Case]] = [
    Case(
        name="non_boolean",
        expression="long_string",
        raised_type=TypeError,
        content_match="is not a boolean",
    ),
    Case(
        name="non_boolean_multiple",
        expression=[
            "contains(long_string, 'very long')",
            "long_string",
        ],
        raised_type=TypeError,
        content_match="is not a boolean",
    ),
    Case(
        name="lexer_error",
        expression="contains(long_string, 'wheres the quote)",
        raised_type=ValueError,
        content_match="Invalid JMESPath expression syntax",
    ),
    Case(
        name="jmespath_type_error",
        expression="abs(long_string)",  # abs() expects a number not a string
        raised_type=ValueError,
        content_match="Invalid JMESPath expression",
    ),
    Case(
        name="jmespatherror",
        expression="",  # Empty expression Thows EmptyExpressionError (subtype of JMESPathError)
        raised_type=ValueError,
        content_match="Error processing JMESPath expression",
    ),
]


@pytest.mark.parametrize(
    "case",
    cases,
    ids=[case.name for case in cases],
)
def test_json_assert_that_invalid_expression(json_content: str, case: Case) -> None:
    with pytest.raises(case.raised_type, match=case.content_match):
        json_assert_that(json_content, case.expression)
