"""SSE and WebSocket transport with optional Bearer token authentication."""

import secrets

import uvicorn
from api.v1 import V1_ROUTES
from api.v1.openapi import (
    API_DOC_PATH,
    API_DOC_SPEC_PATH,
    API_PUBLIC_DOC_PATHS,
    api_doc,
    api_spec,
)
from events_docs import (
    EVENTS_DOC_PATH,
    EVENTS_DOC_SPEC_PATH,
    PUBLIC_DOC_PATHS,
    events_doc,
    events_spec,
)
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route, WebSocketRoute

from ws_gateway import handle_ws_gateway

# Docs + health stay reachable without Bearer when auth is enabled.
_PUBLIC_PATHS = frozenset({"/health", *PUBLIC_DOC_PATHS, *API_PUBLIC_DOC_PATHS})


def verify_bearer(headers: list[tuple[bytes, bytes]], token: str) -> bool:
    auth_header = ""
    for key, value in headers:
        if key.lower() == b"authorization":
            auth_header = value.decode()
            break

    if not auth_header.startswith("Bearer "):
        return False

    provided_token = auth_header[7:]
    return secrets.compare_digest(provided_token, token)


class BearerTokenMiddleware:
    """Pure ASGI middleware supporting both HTTP and WebSocket."""

    def __init__(self, app, token: str):
        self.app = app
        self._token = token

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in _PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        if not verify_bearer(scope.get("headers", []), self._token):
            if scope["type"] == "http":
                response = JSONResponse({"detail": "Unauthorized"}, status_code=401)
                await response(scope, receive, send)
            else:
                await send({"type": "websocket.close", "code": 4401})
            return

        await self.app(scope, receive, send)


async def run_sse_async(mcp, token: str | None = None) -> None:
    """Run the MCP server over SSE and WebSocket, optionally requiring a Bearer token."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp._mcp_server.run(
                streams[0],
                streams[1],
                mcp._mcp_server.create_initialization_options(),
            )
        return Response()

    async def health(_request):
        return JSONResponse({"status": "ok"})

    starlette_app = Starlette(
        debug=mcp.settings.debug,
        routes=[
            Route("/health", endpoint=health),
            Route(EVENTS_DOC_PATH, endpoint=events_doc),
            Route(EVENTS_DOC_SPEC_PATH, endpoint=events_spec),
            Route(API_DOC_PATH, endpoint=api_doc),
            Route(API_DOC_SPEC_PATH, endpoint=api_spec),
            *V1_ROUTES,
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            WebSocketRoute("/ws/", endpoint=handle_ws_gateway),
        ],
    )

    if token:
        starlette_app = BearerTokenMiddleware(starlette_app, token=token)

    config = uvicorn.Config(
        starlette_app,
        host=mcp.settings.host,
        port=mcp.settings.port,
        log_level=mcp.settings.log_level.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()
