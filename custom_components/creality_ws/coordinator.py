"""WebSocket coordinator for Creality Print Viewer."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from websockets.exceptions import ConnectionClosed

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import CrealityClient
from .const import DOMAIN, RECONNECT_DELAY
from .printer_state import PrinterState

_LOGGER = logging.getLogger(__name__)


class CrealityCoordinator(DataUpdateCoordinator[PrinterState]):
    """Maintain printer state and distribute updates to entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: CrealityClient,
    ) -> None:
        """Initialize the coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )

        self.client = client

        self.data = PrinterState()
        self._raw_state: dict[str, Any] = {}

        self._listener_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def async_start(self) -> None:
        """Start the WebSocket listener in the background."""

        if self._listener_task is not None:
            return

        self._stop_event.clear()

        self._listener_task = self.hass.async_create_task(
            self._listen_loop(),
            f"{DOMAIN}_websocket_listener",
        )

    async def async_stop(self) -> None:
        """Stop the WebSocket listener."""

        self._stop_event.set()

        if self._listener_task is None:
            return

        self._listener_task.cancel()

        try:
            await self._listener_task
        except asyncio.CancelledError:
            pass

        self._listener_task = None

    async def _listen_loop(self) -> None:
        """Receive printer messages and reconnect after failures."""

        while not self._stop_event.is_set():
            try:
                _LOGGER.info(
                    "Connecting to Creality printer at %s",
                    self.client.websocket_url,
                )

                async for received_data in self.client.async_messages():
                    self.last_update_success = True
                    self._process_data(received_data)

            except asyncio.CancelledError:
                raise

            except ConnectionClosed as err:
                self.last_update_success = False

                _LOGGER.warning(
                    "WebSocket connection to %s closed: %s",
                    self.client.websocket_url,
                    err,
                )

            except (OSError, TimeoutError) as err:
                self.last_update_success = False

                _LOGGER.warning(
                    "Cannot connect to %s: %s",
                    self.client.websocket_url,
                    err,
                )

            except Exception:
                self.last_update_success = False

                _LOGGER.exception(
                    "Unexpected WebSocket error for %s",
                    self.client.websocket_url,
                )

            if not self._stop_event.is_set():
                await asyncio.sleep(RECONNECT_DELAY)

    def _process_data(
        self,
        received_data: dict[str, Any],
    ) -> None:
        """Merge one partial update into the printer state."""

        self._raw_state.update(received_data)

        printer_state = PrinterState.from_dict(self._raw_state)

        self.async_set_updated_data(printer_state)