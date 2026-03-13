import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed # Added UpdateFailed

from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class FoxESSCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FoxESS data."""

    def __init__(self, hass, api):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="foxess_charge_schedule",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            # Running the sync API call in the executor thread
            return await self.hass.async_add_executor_job(
                self.api.get_charge_times
            )
        except Exception as err:
            # This is key: it tells HA the update failed so entities can show 'unavailable'
            raise UpdateFailed(f"Error communicating with FoxESS API: {err}")
