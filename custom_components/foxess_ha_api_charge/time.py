from homeassistant.components.time import TimeEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import time as dt_time
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_sn = entry.data["device_sn"]

    entities = [
        FoxESSTime(coordinator, device_sn, "start1", "Charge Timer 1 Start"),
        FoxESSTime(coordinator, device_sn, "end1", "Charge Timer 1 End"),
        FoxESSTime(coordinator, device_sn, "start2", "Charge Timer 2 Start"),
        FoxESSTime(coordinator, device_sn, "end2", "Charge Timer 2 End"),
    ]
    async_add_entities(entities)

class FoxESSTime(CoordinatorEntity, TimeEntity):

    def __init__(self, coordinator, device_sn, key, name):
        super().__init__(coordinator)
        self.key = key
        self._device_sn = device_sn
        self._attr_name = name
        self._attr_unique_id = f"{device_sn}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_sn)},
            "name": "FoxESS Inverter",
        }

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
            
        hour = data.get(f"h_{self.key}", 0)
        minute = data.get(f"m_{self.key}", 0)
        return dt_time(hour, minute)

    async def async_set_value(self, value: dt_time):
        d = self.coordinator.data
        
        vals = {
            "h1s": d["h_start1"], "m1s": d["m_start1"],
            "h1e": d["h_end1"], "m1e": d["m_end1"],
            "h2s": d["h_start2"], "m2s": d["m_start2"],
            "h2e": d["h_end2"], "m2e": d["m_end2"],
            "en1": d["enable1"], "en2": d["enable2"]
        }

        vals[f"h{self.key[5:]}{self.key[0]}"] = value.hour

        if self.key == "start1":
            vals["h1s"], vals["m1s"] = value.hour, value.minute
        elif self.key == "end1":
            vals["h1e"], vals["m1e"] = value.hour, value.minute
        elif self.key == "start2":
            vals["h2s"], vals["m2s"] = value.hour, value.minute
        elif self.key == "end2":
            vals["h2e"], vals["m2e"] = value.hour, value.minute

        await self.hass.async_add_executor_job(
            self.coordinator.api.set_charge_times,
            vals["h1s"], vals["m1s"], vals["h1e"], vals["m1e"],
            vals["h2s"], vals["m2s"], vals["h2e"], vals["m2e"],
            vals["en1"], vals["en2"]
        )
        await self.coordinator.async_request_refresh()
