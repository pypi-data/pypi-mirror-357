from collections.abc import Callable
import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def fixture_loader() -> Callable[[str], str]:
    def _load(name: str) -> str:
        path = Path(__file__).parent / "__fixtures__" / name
        return path.read_text()

    return _load


@pytest.fixture
def json_content(fixture_loader: Callable[[str], str]) -> str:
    return fixture_loader("test.json")


@pytest.fixture
def json_data(json_content: str) -> Any:
    return json.loads(json_content)
