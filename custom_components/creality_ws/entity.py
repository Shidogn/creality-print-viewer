"""Entity helpers for Creality Print Viewer."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CrealityConfigEntry
from .const import DOMAIN
from .coordinator import CrealityCoordinator


def build_device_info(
    entry: CrealityConfigEntry,
) -> DeviceInfo:
    """Return device information shared by all printer entities."""

    return DeviceInfo(
        identifiers={
            (DOMAIN, entry.entry_id),
        },
        name=entry.title,
        manufacturer="Creality",
    )


class CrealityEntity(CoordinatorEntity[CrealityCoordinator]):
    """Base coordinator entity for a Creality printer."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CrealityCoordinator,
        entry: CrealityConfigEntry,
    ) -> None:
        """Initialize the Creality entity."""

        super().__init__(coordinator)

        self._attr_device_info = build_device_info(entry)