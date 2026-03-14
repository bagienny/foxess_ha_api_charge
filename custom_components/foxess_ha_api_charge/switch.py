from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_sn = entry.data["device_sn"]

    entities = [
        FoxESSChargeTimerSwitch(coordinator, device_sn, "enable1", "FoxESS Charge Timer 1"),
        FoxESSChargeTimerSwitch(coordinator, device_sn, "enable2", "FoxESS Charge Timer 2"),
    ]

    async_add_entities(entities)


class FoxESSChargeTimerSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, device_sn, key, name):
        super().__init__(coordinator)
        self.key = key
        self._device_sn = device_sn
        self._attr_name = name
        self._attr_unique_id = f"{device_sn}_{key}"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_sn)},
            "name": "FoxESS Inverter",
            "manufacturer": "FoxESS",
        }

    @property
    def is_on(self):
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get(self.key, False)

    async def async_turn_on(self, **kwargs):
        await self._async_set_state(True)

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("Turning on FoxESS timer: %s", self.key)
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_enable,
                self.key,
                True
            )
            self.coordinator.data[self.key] = True
            self.async_write_ha_state()
            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on FoxESS switch %s: %s", self.key, err)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("Turning off FoxESS timer: %s", self.key)
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_enable,
                self.key,
                False 
            )
            self.coordinator.data[self.key] = False
            self.async_write_ha_state()
            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off FoxESS switch %s: %s", self.key, err)
