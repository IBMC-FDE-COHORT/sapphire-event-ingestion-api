"""
Physiological range validation and unit conversion for body temperature readings.

All conversion and validation logic is isolated here so it can be unit-tested
independently of the FastAPI routing layer. Consumed by ValidationService
and the body temperature ingestion endpoint.
"""
from app.config import settings

# Conversion constants — never use raw literals in conversion logic.
_FAHRENHEIT_OFFSET: float = 32.0
_FAHRENHEIT_TO_CELSIUS_FACTOR: float = 5.0 / 9.0
_CELSIUS_DECIMAL_PLACES: int = 2


def to_celsius(value: float, unit: str) -> float:
    """
    Convert a temperature value to Celsius, rounded to two decimal places.

    If the unit is already CELSIUS the value is returned unchanged (rounded).
    For FAHRENHEIT the standard formula C = (F - 32) * 5/9 is applied.
    """
    if unit == "CELSIUS":
        return round(value, _CELSIUS_DECIMAL_PLACES)
    return round(
        (value - _FAHRENHEIT_OFFSET) * _FAHRENHEIT_TO_CELSIUS_FACTOR,
        _CELSIUS_DECIMAL_PLACES,
    )


def validate_temperature_range(value_celsius: float) -> None:
    """
    Raise ValueError if value_celsius falls outside the configured physiological range.

    The range is read from application settings (env vars TEMP_MIN_CELSIUS /
    TEMP_MAX_CELSIUS) so it can be overridden per deployment without code changes.
    """
    if value_celsius < settings.TEMP_MIN_CELSIUS or value_celsius > settings.TEMP_MAX_CELSIUS:
        raise ValueError(
            f"Body temperature {value_celsius}\u00b0C is outside the acceptable "
            f"physiological range [{settings.TEMP_MIN_CELSIUS}, "
            f"{settings.TEMP_MAX_CELSIUS}]\u00b0C"
        )

# Made with Bob
