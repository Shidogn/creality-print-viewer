"""Local client for Creality Print Viewer."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

import asyncio

CONNECTION_TIMEOUT = 10

class CrealityClient:
    """Provide local access to a Creality printer."""

    def __init__(
        self,
        host: str,
        websocket_port: int = 9999,
        camera_port: int = 8080,
    ) -> None:
        """Initialize the Creality client."""

        self.host = host
        self.websocket_port = websocket_port
        self.camera_port = camera_port

    @property
    def websocket_url(self) -> str:
        """Return the printer WebSocket URL."""
        return f"ws://{self.host}:{self.websocket_port}"

    @property
    def camera_stream_url(self) -> str:
        """Return the printer MJPEG stream URL."""
        return f"http://{self.host}:{self.camera_port}/?action=stream"

    @property
    def camera_snapshot_url(self) -> str:
        """Return the printer snapshot URL."""
        return f"http://{self.host}:{self.camera_port}/?action=snapshot"

    async def async_connect_websocket(self) -> ClientConnection:
        """Open and return a WebSocket connection."""
        return await websockets.connect(
            self.websocket_url,
            open_timeout=10,
            close_timeout=5,
        )
    async def async_get_initial_state(self) -> dict[str, Any]:
        """Connect to the printer and return its first valid state."""

        async with await self.async_connect_websocket() as websocket:
            async with asyncio.timeout(CONNECTION_TIMEOUT):
                while True:
                    message = await websocket.recv()
                    parsed = self._parse_message(message)

                    if parsed:
                        return parsed

    async def async_messages(self) -> AsyncIterator[dict[str, Any]]:
        """Yield valid dictionary messages from the printer."""

        async with await self.async_connect_websocket() as websocket:
            async for message in websocket:
                parsed = self._parse_message(message)

                if parsed is not None:
                    yield parsed

    @staticmethod
    def _parse_message(
        message: str | bytes,
    ) -> dict[str, Any] | None:
        """Convert one WebSocket message into a dictionary."""

        if isinstance(message, bytes):
            message = message.decode("utf-8")

        try:
            parsed = json.loads(message)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

        if not isinstance(parsed, dict):
            return None

        return parsed