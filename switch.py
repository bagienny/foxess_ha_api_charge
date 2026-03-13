from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, entry, async_add_entities):
    """Set up FoxESS switches based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device_sn = entry.data["device_sn"]

    entities = [
        FoxESSChargeTimerSwitch(coordinator, device_sn, "enable1", "FoxESS Charge Timer 1"),
        FoxESSChargeTimerSwitch(coordinator, device_sn, "enable2", "FoxESS Charge Timer 2"),
    ]

    async_add_entities(entities)


class FoxESSChargeTimerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a FoxESS Charge Enable switch."""

    def __init__(self, coordinator, device_sn, key, name):
        """Initialize the switch."""
        super().__init__(coordinator)
        self.key = key
        self._device_sn = device_sn
        self._attr_name = name
        # Including serial number ensures uniqueness across multiple inverters
        self._attr_unique_id = f"{device_sn}_{key}"
        
        # Optional: Link this switch to the device in the HA UI
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_sn)},
            "name": "FoxESS Inverter",
            "manufacturer": "FoxESS",
        }

    @property
    def is_on(self):
        """Return True if the entity is on."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get(self.key, False)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._async_set_state(True)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on (Enable this specific timer)."""
        _LOGGER.debug("Turning on FoxESS timer: %s", self.key)
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_enable,
                self.key,  # "enable1" or "enable2"
                True       # Enable
            )
            # Optimistic update: Update local data immediately for a snappy UI
            self.coordinator.data[self.key] = True
            self.async_write_ha_state()
            
            # Refresh from cloud to confirm
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on FoxESS switch %s: %s", self.key, err)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off (Disable this specific timer)."""
        _LOGGER.debug("Turning off FoxESS timer: %s", self.key)
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_enable,
                self.key,
                False      # Disable
            )
            # Optimistic update
            self.coordinator.data[self.key] = False
            self.async_write_ha_state()
            
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off FoxESS switch %s: %s", self.key, err)
