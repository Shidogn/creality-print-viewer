"""Camera platform for Creality Print Viewer."""

from __future__ import annotations

import asyncio
import logging

import aiohttp
from aiohttp import web

from homeassistant.components.camera import Camera
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import (
    async_aiohttp_proxy_web,
    async_get_clientsession,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CrealityConfigEntry
from .client import CrealityClient
from .entity import build_device_info

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrealityConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality printer camera."""

    client = entry.runtime_data.client

    async_add_entities(
        [
            CrealityPrinterCamera(
                client=client,
                entry=entry,
            )
        ]
    )


class CrealityPrinterCamera(Camera):
    """Represent the printer's built-in MJPEG camera."""

    _attr_has_entity_name = True
    _attr_translation_key = "camera"
    _attr_should_poll = False

    def __init__(
        self,
        client: CrealityClient,
        entry: CrealityConfigEntry,
    ) -> None:
        """Initialize the camera."""

        super().__init__()

        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_camera"
        self._attr_device_info = build_device_info(entry)

    async def async_camera_image(
        self,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes | None:
        """Return a JPEG snapshot from the printer."""

        session = async_get_clientsession(self.hass)

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with session.get(
                    self._client.camera_snapshot_url
                ) as response:
                    response.raise_for_status()
                    return await response.read()

        except TimeoutError:
            _LOGGER.warning(
                "Timeout while requesting camera snapshot from %s",
                self._client.camera_snapshot_url,
            )

        except aiohttp.ClientError as err:
            _LOGGER.warning(
                "Cannot retrieve camera snapshot from %s: %s",
                self._client.camera_snapshot_url,
                err,
            )

        return None

    async def handle_async_mjpeg_stream(
        self,
        request: web.Request,
    ) -> web.StreamResponse | None:
        """Proxy the native MJPEG stream through Home Assistant."""

        session = async_get_clientsession(self.hass)

        stream_request = session.get(
            self._client.camera_stream_url
        )

        return await async_aiohttp_proxy_web(
            self.hass,
            request,
            stream_request,
        )