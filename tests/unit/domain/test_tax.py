"""Unit tests for PAYE and statutory deduction calculations."""

import pytest

from kenya_wealth_agent.config.constants import PERSONAL_RELIEF
from kenya_wealth_agent.domain.tax import calculate_tax


class TestPayeBoundaryAndProgressiveMath:
    """Verify progressive bracket math against KRA FY 2024/25 expectations."""

    def test_negative_salary_rejected(self):
        with pytest.raises(ValueError, match="gross_salary cannot be negative"):
            calculate_tax(-1)

    def test_zero_salary(self):
        result = calculate_tax(0)
        assert result.paye == 0
        assert result.nhif_shif == 300  # SHIF minimum
        assert result.nssf == 0
        assert result.housing_levy == 0
        assert result.net_salary == -300  # deductions exceed income

    def test_first_bracket_top_end(self):
        """At KES 24,000 the full first bracket is taxed at 10% and wiped by relief."""
        result = calculate_tax(24_000)
        gross_tax = 24_000 * 0.10
        assert gross_tax == 2_400
        assert result.paye == max(0.0, gross_tax - PERSONAL_RELIEF)
        assert result.paye == 0
        # Deductions are positive even when PAYE is zero
        assert result.nhif_shif == pytest.approx(min(max(24_000 * 0.0275, 300), 1_700))
        assert result.nssf == pytest.approx(min(24_000 * 0.06, 2_160))
        assert result.housing_levy == pytest.approx(24_000 * 0.015)

    def test_one_kes_into_second_bracket(self):
        """KES 24,001 should pay 25 st. cents more than KES 24,000."""
        low = calculate_tax(24_000)
        high = calculate_tax(24_001)
        assert high.paye == pytest.approx(low.paye + 0.25, rel=1e-9)

    def test_second_bracket_top_end(self):
        """At KES 32,333 the second bracket width is exactly 8,333 KES."""
        result = calculate_tax(32_333)
        # First bracket: 24,000 @ 10% = 2,400
        # Second bracket: 8,333 @ 25% = 2,083.25
        gross_tax = 2_400 + 2_083.25
        assert result.paye == pytest.approx(max(0.0, gross_tax - PERSONAL_RELIEF))

    def test_one_kes_into_third_bracket(self):
        """KES 32,334 should pay 30% on the extra KES over KES 32,333."""
        low = calculate_tax(32_333)
        high = calculate_tax(32_334)
        assert high.paye == pytest.approx(low.paye + 0.30, rel=1e-9)

    def test_high_earner(self):
        """Smoke test for a salary deep in the top bracket."""
        result = calculate_tax(1_000_000)
        assert result.paye > 0
        assert result.nhif_shif == 1_700  # SHIF cap
        assert result.nssf == 2_160  # NSSF cap
        assert result.housing_levy == 15_000
        assert result.net_salary < result.gross_salary

    def test_known_kra_example(self):
        """A sanity-check example: gross 50,000 should yield sensible PAYE."""
        result = calculate_tax(50_000)
        # First 24,000 @ 10% = 2,400
        # Next 8,333 @ 25% = 2,083.25
        # Remaining 17,667 @ 30% = 5,300.10
        gross_tax = 2_400 + 2_083.25 + 5_300.10
        expected_paye = gross_tax - PERSONAL_RELIEF
        assert result.paye == pytest.approx(expected_paye, rel=1e-9)
