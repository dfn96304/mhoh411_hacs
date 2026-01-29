"""Coordinator for MHO-H411."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_POLL_INTERVAL, DEFAULT_POLL_SECONDS, UUID_BATTERY_READ, UUID_TEMP_READ

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class MhoData:
    """Parsed sensor data."""

    temperature_c: float | None
    humidity_pct: int | None
    co2_ppm: int | None
    voltage_v: float | None
    battery_pct: int | None
    raw_hex: str | None = None


def _parse_readings(packet: bytes) -> tuple[float | None, int | None, int | None, float | None, str | None]:
    """Parse the MHO-H411 temperature/humidity/voltage/co2 payload."""
    if not packet:
        return None, None, None, None, None

    raw_hex = packet.hex(" ")

    # Expected layout (from elsemieni-mho-h411):
    # 0..1: temp (int16, little-endian, signed), value / 100
    # 2   : humidity (uint8)
    # 3..4: voltage (uint16, little-endian)
    # 5..6: co2 (uint16, little-endian) - 65535 means "disabled"
    if len(packet) < 7:
        return None, None, None, None, raw_hex

    temp_raw = int.from_bytes(packet[0:2], "little", signed=True)
    temperature_c = temp_raw / 100.0

    humidity_pct = packet[2]

    voltage_mv = int.from_bytes(packet[3:5], "little", signed=False)
    voltage_v = voltage_mv / 1000.0

    co2_ppm = int.from_bytes(packet[5:7], "little", signed=False)
    if co2_ppm == 65535:
        co2_ppm = None

    return temperature_c, humidity_pct, co2_ppm, voltage_v, raw_hex


class MhoH411Coordinator(DataUpdateCoordinator[MhoData]):
    """Fetch data from the MHO-H411 via HA Bluetooth (supports proxies)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.address: str = entry.data["address"]

        poll_seconds = int(entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_SECONDS))

        super().__init__(
            hass,
            _LOGGER,
            name=f"mhoh411_{self.address}",
            update_interval=timedelta(seconds=poll_seconds),
        )

    async def _async_update_data(self) -> MhoData:
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

        if ble_device is None:
            raise UpdateFailed("Device not found via any Bluetooth adapter/proxy")

        client = None
        try:
            # establish_connection provides retries/backoff and works well with HA Bluetooth.
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                ble_device.name or self.address,
                max_attempts=3,
            )

            temp_packet = await client.read_gatt_char(UUID_TEMP_READ)
            batt_packet = await client.read_gatt_char(UUID_BATTERY_READ)

            temperature_c, humidity_pct, co2_ppm, voltage_v, raw_hex = _parse_readings(temp_packet)

            battery_pct: int | None
            if batt_packet and len(batt_packet) >= 1:
                battery_pct = int.from_bytes(batt_packet[0:1], "little", signed=True)
            else:
                battery_pct = None

            return MhoData(
                temperature_c=temperature_c,
                humidity_pct=humidity_pct,
                co2_ppm=co2_ppm,
                voltage_v=voltage_v,
                battery_pct=battery_pct,
                raw_hex=raw_hex,
            )

        except Exception as err:
            raise UpdateFailed(f"BLE update failed: {err}") from err
        finally:
            if client is not None:
                try:
                    await client.disconnect()
                except Exception:
                    # Some BLE stacks may already be disconnected; ignore.
                    pass
