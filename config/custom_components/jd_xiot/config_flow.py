"""Config flow for JingDong XIoT."""

import logging

from aiohttp import ClientError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client

from .const import CONF_COOKIE, DOMAIN

_LOGGER = logging.getLogger(__name__)

# 配置流程的数据结构
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COOKIE): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JingDong XIoT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            cookie = user_input[CONF_COOKIE]

            # 验证 Cookie 是否有效
            valid = await self._test_cookie(cookie)
            if valid:
                return self.async_create_entry(title="JingDong XIoT", data=user_input)
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def _test_cookie(self, cookie: str) -> bool:
        """Test if the provided cookie is valid by calling the API."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        headers = {"Cookie": cookie}
        try:
            async with session.get(
                "https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger",
                headers=headers,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    return data.get("code") == 0
                return False
        except ClientError as e:
            _LOGGER.error("Error testing cookie: %s", e)
            return False
