import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import FoxESSApi
from .const import DOMAIN
from .coordinator import FoxESSCoordinator # Import your new class

async def async_setup_entry(hass, entry):
    api = FoxESSApi(entry.data["api_key"], entry.data["device_sn"])
    
    # Use your new class instead of the generic DataUpdateCoordinator
    coordinator = FoxESSCoordinator(hass, api)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["time", "switch"])
    return True
