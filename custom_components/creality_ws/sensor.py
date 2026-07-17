"""Sensor platform for Creality Print Viewer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CrealityConfigEntry
from .coordinator import CrealityCoordinator
from .entity import CrealityEntity
from .printer_state import PrinterState


@dataclass(frozen=True, kw_only=True)
class CrealitySensorEntityDescription(SensorEntityDescription):
    """Describe a Creality sensor."""

    value_fn: Callable[[PrinterState], object | None]


SENSOR_DESCRIPTIONS: tuple[CrealitySensorEntityDescription, ...] = (
    CrealitySensorEntityDescription(
        key="nozzle_temperature",
        translation_key="nozzle_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.nozzle_temperature,
    ),
    CrealitySensorEntityDescription(
        key="bed_temperature",
        translation_key="bed_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.bed_temperature,
    ),
    CrealitySensorEntityDescription(
        key="target_nozzle_temperature",
        translation_key="target_nozzle_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.target_nozzle_temperature,
    ),
    CrealitySensorEntityDescription(
        key="target_bed_temperature",
        translation_key="target_bed_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.target_bed_temperature,
    ),
    CrealitySensorEntityDescription(
        key="print_progress",
        translation_key="print_progress",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.print_progress,
    ),
    CrealitySensorEntityDescription(
        key="current_layer",
        translation_key="current_layer",
        icon="mdi:layers",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda state: state.current_layer,
    ),
    CrealitySensorEntityDescription(
        key="total_layers",
        translation_key="total_layers",
        icon="mdi:layers-triple",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda state: state.total_layers,
    ),
    CrealitySensorEntityDescription(
        key="print_job_time",
        translation_key="print_job_time",
        icon="mdi:timer-outline",
        value_fn=lambda state: state.print_job_time,
    ),
    CrealitySensorEntityDescription(
        key="print_left_time",
        translation_key="print_left_time",
        icon="mdi:timer-sand",
        value_fn=lambda state: state.print_left_time,
    ),
    CrealitySensorEntityDescription(
        key="print_file_name",
        translation_key="print_file_name",
        icon="mdi:file-outline",
        value_fn=lambda state: state.print_file_name,
    ),
    CrealitySensorEntityDescription(
        key="feedrate_percentage",
        translation_key="feedrate_percentage",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:speedometer",
        value_fn=lambda state: state.feedrate_percentage,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrealityConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Creality sensors from a config entry."""

    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        CrealitySensor(
            coordinator=coordinator,
            entry=entry,
            description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class CrealitySensor(
    CrealityEntity,
    SensorEntity,
):
    """Represent one Creality printer sensor."""

    entity_description: CrealitySensorEntityDescription

    def __init__(
        self,
        coordinator: CrealityCoordinator,
        entry: CrealityConfigEntry,
        description: CrealitySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(
            coordinator=coordinator,
            entry=entry,
        )

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> object | None:
        """Return the current sensor value."""

        return self.entity_description.value_fn(self.coordinator.data)