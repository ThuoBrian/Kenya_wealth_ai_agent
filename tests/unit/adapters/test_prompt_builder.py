"""Tests for the system prompt builder."""

from kenya_wealth_agent.adapters.prompts.system_prompt import KenyaSystemPromptBuilder
from kenya_wealth_agent.domain.models import UserProfile


def test_build_without_profile():
    builder = KenyaSystemPromptBuilder()
    prompt = builder.build()
    assert "Kenyan market" in prompt
    assert "Known User Profile" not in prompt


def test_build_with_profile():
    builder = KenyaSystemPromptBuilder()
    profile = UserProfile(name="Brian", monthly_income=100_000)
    prompt = builder.build(profile)
    assert "Known User Profile" in prompt
    assert "Brian" in prompt
    assert "KES 100,000" in prompt
