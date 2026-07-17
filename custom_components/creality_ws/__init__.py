"""Creality Print Viewer integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .client import CrealityClient
from .const import DEFAULT_PORT
from .coordinator import CrealityCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CAMERA,
]


@dataclass(slots=True)
class CrealityRuntimeData:
    """Runtime objects shared by integration platforms."""

    client: CrealityClient
    coordinator: CrealityCoordinator


type CrealityConfigEntry = ConfigEntry[CrealityRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrealityConfigEntry,
) -> bool:
    """Set up Creality Print Viewer from a config entry."""

    client = CrealityClient(
        host=entry.data[CONF_HOST],
        websocket_port=DEFAULT_PORT,
    )

    coordinator = CrealityCoordinator(
        hass=hass,
        client=client,
    )

    entry.runtime_data = CrealityRuntimeData(
        client=client,
        coordinator=coordinator,
    )

    await coordinator.async_start()

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: CrealityConfigEntry,
) -> bool:
    """Unload Creality Print Viewer."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        await entry.runtime_data.coordinator.async_stop()

    return unload_ok