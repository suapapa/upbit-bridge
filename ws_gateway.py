"""Smart WebSocket gateway: routes public/private Upbit streams on a single /ws/ endpoint."""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from starlette.websockets import WebSocket, WebSocketDisconnect

from config import UPBIT_ACCESS_KEY
from upbit_client import get_authenticated_client, get_public_client

log = logging.getLogger(__name__)

PUBLIC_TYPES = frozenset({"ticker", "trade", "orderbook"})
PRIVATE_TYPES = frozenset({"myOrder", "myAsset"})


def _is_public_type(type_name: str) -> bool:
    return type_name in PUBLIC_TYPES or type_name.startswith("candle.")


def _is_private_type(type_name: str) -> bool:
    return type_name in PRIVATE_TYPES


@dataclass
class ParsedMessage:
    ticket: dict[str, Any] | None = None
    format_entry: dict[str, Any] | None = None
    public_entries: list[dict[str, Any]] = field(default_factory=list)
    private_entries: list[dict[str, Any]] = field(default_factory=list)
    is_list_subscriptions: bool = False
    unknown_types: list[str] = field(default_factory=list)


def parse_message(text: str) -> ParsedMessage:
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array")

    parsed = ParsedMessage()
    for item in data:
        if not isinstance(item, dict):
            continue
        if "ticket" in item:
            parsed.ticket = item
        elif "format" in item:
            parsed.format_entry = item
        elif item.get("method") == "LIST_SUBSCRIPTIONS":
            parsed.is_list_subscriptions = True
        elif "type" in item:
            type_name = item["type"]
            if _is_private_type(type_name):
                parsed.private_entries.append(item)
            elif _is_public_type(type_name):
                parsed.public_entries.append(item)
            else:
                parsed.unknown_types.append(type_name)

    return parsed


def build_upstream_payload(
    ticket: dict[str, Any] | None,
    format_entry: dict[str, Any] | None,
    type_entries: list[dict[str, Any]],
) -> str:
    parts: list[dict[str, Any]] = []
    if ticket is not None:
        parts.append(ticket)
    parts.extend(type_entries)
    if format_entry is not None:
        parts.append(format_entry)
    return json.dumps(parts)


class UpstreamChannel:
    def __init__(self, name: str, connect_factory: Callable):
        self.name = name
        self._connect_factory = connect_factory
        self._conn_manager = None
        self._connection = None
        self._reader_task: asyncio.Task | None = None

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def connect(self, on_message: Callable[[str], Any]) -> None:
        if self._connection is not None:
            return

        self._conn_manager = self._connect_factory()
        self._connection = await self._conn_manager.enter()
        self._reader_task = asyncio.create_task(self._read_loop(on_message))
        log.debug("Upstream %s connected", self.name)

    async def send_raw(self, data: str, on_message: Callable[[str], Any]) -> None:
        await self.connect(on_message)
        await self._connection.send_raw(data)

    async def _read_loop(self, on_message: Callable[[str], Any]) -> None:
        from websockets.exceptions import ConnectionClosedOK

        try:
            while self._connection is not None:
                raw = await self._connection.recv_bytes()
                text = raw.decode() if isinstance(raw, bytes) else raw
                await on_message(text)
        except ConnectionClosedOK:
            pass
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Upstream %s read loop failed", self.name)

    async def close(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        if self._conn_manager is not None:
            await self._conn_manager.__aexit__(None, None, None)
            self._conn_manager = None
            self._connection = None


class WsGatewaySession:
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket
        self._send_lock = asyncio.Lock()
        self._closed = False
        self._public = UpstreamChannel(
            "public",
            lambda: get_public_client().ws_public.connect_public(),
        )
        self._private = UpstreamChannel(
            "private",
            lambda: get_authenticated_client().ws_private.connect_private(),
        )

    async def send_to_client(self, text: str) -> None:
        async with self._send_lock:
            if not self._closed:
                await self._websocket.send_text(text)

    async def send_error(self, message: str) -> None:
        await self.send_to_client(json.dumps({"error": message}))

    async def route_message(self, text: str) -> None:
        try:
            parsed = parse_message(text)
        except (json.JSONDecodeError, ValueError) as exc:
            await self.send_error(str(exc))
            return

        if parsed.unknown_types:
            await self.send_error(f"Unknown subscription type(s): {', '.join(parsed.unknown_types)}")
            return

        if parsed.is_list_subscriptions:
            await self._route_list_subscriptions(text)
            return

        if not parsed.public_entries and not parsed.private_entries:
            await self.send_error("No subscription types in message")
            return

        if parsed.private_entries and not UPBIT_ACCESS_KEY:
            await self.send_error("API 키가 설정되지 않았습니다. private 스트림에는 UPBIT_ACCESS_KEY가 필요합니다.")
            return

        forward = self.send_to_client

        if parsed.public_entries:
            payload = build_upstream_payload(
                parsed.ticket, parsed.format_entry, parsed.public_entries
            )
            try:
                await self._public.send_raw(payload, forward)
            except Exception as exc:
                log.exception("Failed to send to public upstream")
                await self.send_error(f"Public upstream error: {exc}")

        if parsed.private_entries:
            payload = build_upstream_payload(
                parsed.ticket, parsed.format_entry, parsed.private_entries
            )
            try:
                await self._private.send_raw(payload, forward)
            except Exception as exc:
                log.exception("Failed to send to private upstream")
                await self.send_error(f"Private upstream error: {exc}")

    async def _route_list_subscriptions(self, text: str) -> None:
        active = [ch for ch in (self._public, self._private) if ch.is_connected]
        if not active:
            await self.send_error("No active upstream connections for LIST_SUBSCRIPTIONS")
            return

        forward = self.send_to_client
        for channel in active:
            try:
                await channel.send_raw(text, forward)
            except Exception as exc:
                log.exception("LIST_SUBSCRIPTIONS failed on %s upstream", channel.name)
                await self.send_error(f"{channel.name} upstream error: {exc}")

    async def run(self) -> None:
        await self._websocket.accept()

        try:
            while True:
                message = await self._websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if "text" in message:
                    await self.route_message(message["text"])
                elif "bytes" in message:
                    await self.route_message(message["bytes"].decode())
        except WebSocketDisconnect:
            pass
        finally:
            self._closed = True
            await self._public.close()
            await self._private.close()
            try:
                await self._websocket.close()
            except RuntimeError:
                pass


async def handle_ws_gateway(websocket: WebSocket) -> None:
    """Route client WebSocket messages to ws_public and/or ws_private upstreams."""
    await WsGatewaySession(websocket).run()
