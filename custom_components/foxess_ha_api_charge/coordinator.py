import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class FoxESSCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="foxess_charge_schedule",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(
                self.api.get_charge_times
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with FoxESS API: {err}")
