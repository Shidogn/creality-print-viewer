"""Config flow for Creality Print Viewer."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from websockets.exceptions import WebSocketException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .client import CrealityClient
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class CrealityConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle the Creality Print Viewer config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle setup initiated by the user."""

        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()

            if not host:
                errors[CONF_HOST] = "invalid_host"
            else:
                client = CrealityClient(
                    host=host,
                    websocket_port=DEFAULT_PORT,
                )

                try:
                    initial_state = await client.async_get_initial_state()

                except (OSError, TimeoutError, WebSocketException):
                    errors["base"] = "cannot_connect"

                except Exception:
                    _LOGGER.exception(
                        "Unexpected error while connecting to %s",
                        host,
                    )
                    errors["base"] = "unknown"

                else:
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()

                    hostname = initial_state.get("hostname")

                    title = (
                        str(hostname).strip()
                        if hostname
                        else f"Creality {host}"
                    )

                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_HOST: host,
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )