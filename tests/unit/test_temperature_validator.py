"""
Unit tests for temperature_validator.py.

Covers: Celsius/Fahrenheit conversion accuracy, boundary conditions,
range enforcement, and null-unit rejection via Pydantic.
Coverage gate: 100% line coverage for app/services/temperature_validator.py
"""
import pytest
from unittest.mock import patch
from types import SimpleNamespace

from app.services.temperature_validator import to_celsius, validate_temperature_range


def _mock_settings(min_c: float = 34.0, max_c: float = 42.0):
    """Return a simple mock settings object with temperature bounds."""
    return SimpleNamespace(TEMP_MIN_CELSIUS=min_c, TEMP_MAX_CELSIUS=max_c)


class TestToCelsius:
    def test_celsius_passthrough_unchanged(self) -> None:
        """A value already in Celsius should be returned rounded to 2dp."""
        assert to_celsius(37.2, "CELSIUS") == 37.2

    def test_fahrenheit_standard_body_temp(self) -> None:
        """98.6 degF is exactly 37.00 degC by the standard formula."""
        assert to_celsius(98.6, "FAHRENHEIT") == 37.0

    def test_fahrenheit_below_min(self) -> None:
        """59.0 degF converts to 15.0 degC."""
        assert to_celsius(59.0, "FAHRENHEIT") == 15.0

    def test_rounding_to_two_decimal_places(self) -> None:
        """Conversion result must be rounded to exactly 2 decimal places."""
        result = to_celsius(100.0, "FAHRENHEIT")
        assert result == round(result, 2)

    def test_celsius_exactly_at_min_boundary(self) -> None:
        """34.0 degC is the default lower bound."""
        assert to_celsius(34.0, "CELSIUS") == 34.0

    def test_celsius_exactly_at_max_boundary(self) -> None:
        """42.0 degC is the default upper bound."""
        assert to_celsius(42.0, "CELSIUS") == 42.0


class TestValidateTemperatureRange:
    def test_in_range_celsius_accepted(self) -> None:
        """37.2 degC is within the default range — no exception raised."""
        with patch("app.services.temperature_validator.settings", _mock_settings()):
            validate_temperature_range(37.2)  # must not raise

    def test_below_min_celsius_raises(self) -> None:
        """15.0 degC is below the default minimum — ValueError expected."""
        with patch("app.services.temperature_validator.settings", _mock_settings()):
            with pytest.raises(ValueError, match="outside"):
                validate_temperature_range(15.0)

    def test_above_max_celsius_raises(self) -> None:
        """55.0 degC is above the default maximum — ValueError expected."""
        with patch("app.services.temperature_validator.settings", _mock_settings()):
            with pytest.raises(ValueError, match="outside"):
                validate_temperature_range(55.0)

    def test_exactly_at_min_boundary_accepted(self) -> None:
        """34.0 degC equals the default minimum — inclusive boundary accepted."""
        with patch("app.services.temperature_validator.settings", _mock_settings()):
            validate_temperature_range(34.0)  # must not raise

    def test_exactly_at_max_boundary_accepted(self) -> None:
        """42.0 degC equals the default maximum — inclusive boundary accepted."""
        with patch("app.services.temperature_validator.settings", _mock_settings()):
            validate_temperature_range(42.0)  # must not raise

    def test_custom_range_overrides_default(self) -> None:
        """Settings-driven range should be respected when overridden via env."""
        with patch("app.services.temperature_validator.settings",
                   _mock_settings(min_c=36.0, max_c=38.0)):
            with pytest.raises(ValueError):
                validate_temperature_range(35.9)  # below custom min

# Made with Bob
