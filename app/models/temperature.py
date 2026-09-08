"""
Pydantic v2 models for body temperature ingestion payloads.

Covers single-record ingestion of body temperature readings.
All validation rules are enforced at the Pydantic layer before reaching
the router or validator service.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TemperatureUnit(str, Enum):
    """Unit of a body temperature value as submitted by the device."""

    CELSIUS = "CELSIUS"
    FAHRENHEIT = "FAHRENHEIT"


class MeasurementMethod(str, Enum):
    """Optional method used to obtain the temperature reading."""

    ORAL = "oral"
    AXILLARY = "axillary"
    TYMPANIC = "tympanic"
    RECTAL = "rectal"
    FOREHEAD = "forehead"


class BodyTemperaturePayload(BaseModel):
    """
    Payload for a single body temperature observation.

    `value` is the raw numeric reading in the supplied `unit`.
    `measurement_method` is optional metadata about how the reading was taken.
    Validation against the physiological range is performed by
    TemperatureValidationService after Pydantic parsing.
    """

    value: float = Field(..., description="Numeric temperature value in the supplied unit")
    unit: TemperatureUnit = Field(
        ..., description="Unit of the supplied value: CELSIUS or FAHRENHEIT"
    )
    measurement_method: Optional[MeasurementMethod] = Field(
        None,
        description="Optional measurement method (oral, axillary, tympanic, rectal, forehead)",
    )

# Made with Bob
