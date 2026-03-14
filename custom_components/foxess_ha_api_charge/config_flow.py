import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("api_key"): str,
    vol.Required("device_sn"): str,
})

class FoxESSChargeScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="FoxESS Charge Periods", data=user_input
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
