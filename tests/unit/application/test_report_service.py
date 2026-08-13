"""Unit tests for the ReportService."""

from datetime import datetime
from pathlib import Path

import pytest

from kenya_wealth_agent.application.financial_services import ReportService


class FakeRenderer:
    def render(
        self,
        messages: list[dict[str, str]],
        session_start: datetime | None = None,
    ) -> str:
        return f"<html>{len(messages)} messages</html>"


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path / "reports"


async def test_export_writes_file(tmp_output: Path):
    service = ReportService(renderer=FakeRenderer(), output_dir=tmp_output)
    path = await service.export([{"role": "user", "content": "Hi"}])
    assert Path(path).exists()
    assert Path(path).read_text() == "<html>1 messages</html>"


async def test_export_uses_custom_path(tmp_output: Path):
    service = ReportService(renderer=FakeRenderer(), output_dir=tmp_output)
    custom = tmp_output / "custom.html"
    path = await service.export([], custom_path=custom)
    assert Path(path) == custom
    assert custom.exists()
