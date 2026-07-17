"""Printer state model for Creality Print Viewer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PrinterState:
    """Represent the current merged state of a Creality printer."""

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PrinterState":
        """Create a printer state from raw WebSocket data."""
        return cls(raw=dict(data))

    @property
    def nozzle_temperature(self) -> float | None:
        """Return the current nozzle temperature."""
        return self._as_float("nozzleTemp")

    @property
    def bed_temperature(self) -> float | None:
        """Return the current bed temperature."""
        return self._as_float("bedTemp0")

    @property
    def target_nozzle_temperature(self) -> float | None:
        """Return the target nozzle temperature."""
        return self._as_float("targetNozzleTemp")

    @property
    def target_bed_temperature(self) -> float | None:
        """Return the target bed temperature."""
        return self._as_float("targetBedTemp0")

    @property
    def print_progress(self) -> int | None:
        """Return print progress in percent."""
        return self._as_int("printProgress")

    @property
    def current_layer(self) -> int | None:
        """Return the current print layer."""
        return self._as_int("layer")

    @property
    def total_layers(self) -> int | None:
        """Return the total number of layers."""
        return self._as_int("TotalLayer")

    @property
    def print_job_time(self) -> str | None:
        """Return elapsed print time formatted as HH:MM:SS."""
        return self._format_duration(self._as_int("printJobTime"))

    @property
    def print_left_time(self) -> str | None:
        """Return remaining print time formatted as HH:MM:SS."""
        return self._format_duration(self._as_int("printLeftTime"))

    @property
    def print_file_name(self) -> str | None:
        """Return the current print file name without the storage prefix."""
    
        value = self._as_string("printFileName")
    
        if not value:
            return None
    
        return value.removeprefix(
            "/usr/data/printer_data/gcodes/"
        )

    @property
    def feedrate_percentage(self) -> int | None:
        """Return the configured speed percentage."""
        return self._as_int("curFeedratePct")

    @property
    def hostname(self) -> str | None:
        """Return the printer hostname."""
        return self._as_string("hostname")

    @property
    def model(self) -> str | None:
        """Return the printer model identifier."""
        return self._as_string("model")

    @property
    def is_connected(self) -> bool:
        """Return whether the printer reports itself as connected."""
        return self._as_int("connect") == 1

    def _as_float(self, key: str) -> float | None:
        """Return a raw value converted to float."""
        value = self.raw.get(key)

        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _as_int(self, key: str) -> int | None:
        """Return a raw value converted to integer."""
        value = self.raw.get(key)

        if value is None or value == "":
            return None

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None

    def _as_string(self, key: str) -> str | None:
        """Return a raw value converted to text."""
        value = self.raw.get(key)

        if value is None:
            return None

        return str(value)

    @staticmethod
    def _format_duration(seconds: int | None) -> str | None:
        """Convert seconds to HH:MM:SS."""

        if seconds is None:
            return None

        seconds = max(0, seconds)

        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"