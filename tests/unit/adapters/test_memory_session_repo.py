"""Tests for the in-memory session repository."""

import pytest

from kenya_wealth_agent.adapters.persistence.memory_session_repo import (
    InMemorySessionRepository,
)


@pytest.fixture
def repo():
    return InMemorySessionRepository()


async def test_save_and_get(repo):
    await repo.save("s1", [{"role": "user", "content": "Hi"}])
    result = await repo.get("s1")
    assert len(result) == 1
    assert result[0]["content"] == "Hi"


async def test_session_isolation(repo):
    await repo.save("s1", [{"role": "user", "content": "A"}])
    await repo.save("s2", [{"role": "user", "content": "B"}])
    assert await repo.get("s1") == [{"role": "user", "content": "A"}]
    assert await repo.get("s2") == [{"role": "user", "content": "B"}]


async def test_get_missing_returns_empty(repo):
    assert await repo.get("missing") == []


async def test_clear(repo):
    await repo.save("s1", [{"role": "user", "content": "Hi"}])
    await repo.clear("s1")
    assert await repo.get("s1") == []


async def test_copy_is_returned(repo):
    original = [{"role": "user", "content": "Hi"}]
    await repo.save("s1", original)
    result = await repo.get("s1")
    result[0]["content"] = "Modified"
    assert (await repo.get("s1"))[0]["content"] == "Hi"
