"""Sensors for MHO-H411."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MhoH411Coordinator


@dataclass(frozen=True, kw_only=True)
class MhoSensorEntityDescription(SensorEntityDescription):
    """Entity description for MHO-H411 sensors."""

    value_attr: str


SENSORS: tuple[MhoSensorEntityDescription, ...] = (
    MhoSensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        state_class=SensorStateClass.MEASUREMENT,
        value_attr="temperature_c",
    ),
    MhoSensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        value_attr="humidity_pct",
    ),
    MhoSensorEntityDescription(
        key="co2",
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement="ppm",
        state_class=SensorStateClass.MEASUREMENT,
        value_attr="co2_ppm",
    ),
    MhoSensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        value_attr="battery_pct",
    ),
    MhoSensorEntityDescription(
        key="voltage",
        name="Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement="V",
        state_class=SensorStateClass.MEASUREMENT,
        value_attr="voltage_v",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: MhoH411Coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [MhoH411Sensor(coordinator, entry, description) for description in SENSORS]
    )


class MhoH411Sensor(CoordinatorEntity[MhoH411Coordinator], SensorEntity):
    """Representation of an MHO-H411 sensor."""

    entity_description: MhoSensorEntityDescription

    def __init__(
        self,
        coordinator: MhoH411Coordinator,
        entry: ConfigEntry,
        description: MhoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description

        address = entry.data["address"]

        self._attr_unique_id = f"{address}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=f"MHO-H411 {address}",
            manufacturer="Xiaomi/Mijia",
            model="MHO-H411",
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        return getattr(data, self.entity_description.value_attr)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None
