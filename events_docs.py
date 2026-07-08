"""AsyncAPI docs routes and payloads for /docs/events."""

from starlette.responses import HTMLResponse, JSONResponse

EVENTS_DOC_PATH = "/docs/events"
EVENTS_DOC_SPEC_PATH = "/docs/events.json"
PUBLIC_DOC_PATHS = (EVENTS_DOC_PATH, EVENTS_DOC_SPEC_PATH)

ASYNCAPI_SPEC: dict = {
    "asyncapi": "2.6.0",
    "info": {
        "title": "Upbit Bridge WebSocket Gateway",
        "version": "1.0.0",
        "description": (
            "Unified /ws/ gateway for Upbit public and private streams. "
            "Clients send Upbit-compatible subscription array payloads."
        ),
    },
    "defaultContentType": "application/json",
    "servers": {
        "local": {
            "url": "localhost:8000",
            "protocol": "ws",
            "description": "Local development server",
        }
    },
    "channels": {
        "/ws/": {
            "description": "Single websocket entrypoint for all subscriptions",
            "publish": {
                "summary": "Client sends subscription payload",
                "message": {"$ref": "#/components/messages/ClientSubscription"},
            },
            "subscribe": {
                "summary": "Server relays upstream events or error payload",
                "message": {
                    "oneOf": [
                        {"$ref": "#/components/messages/UpbitEvent"},
                        {"$ref": "#/components/messages/GatewayError"},
                    ]
                },
            },
        }
    },
    "components": {
        "messages": {
            "ClientSubscription": {
                "name": "ClientSubscription",
                "title": "Client subscription array",
                "payload": {"$ref": "#/components/schemas/ClientSubscriptionPayload"},
            },
            "UpbitEvent": {
                "name": "UpbitEvent",
                "title": "Upbit event payload",
                "payload": {"$ref": "#/components/schemas/UpbitEventPayload"},
            },
            "GatewayError": {
                "name": "GatewayError",
                "title": "Gateway validation or routing error",
                "payload": {"$ref": "#/components/schemas/GatewayErrorPayload"},
            },
        },
        "schemas": {
            "ClientSubscriptionPayload": {
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/components/schemas/SubscriptionItem"},
                "examples": [
                    [
                        {"ticket": "01234567-89ab-cdef-0123-456789abcdef"},
                        {"type": "ticker", "codes": ["KRW-BTC"]},
                        {"format": "DEFAULT"},
                    ],
                    [
                        {"ticket": "01234567-89ab-cdef-0123-456789abcdef"},
                        {"type": "ticker", "codes": ["KRW-BTC"]},
                        {"type": "myOrder", "codes": ["KRW-BTC"]},
                        {"format": "DEFAULT"},
                    ],
                ],
            },
            "SubscriptionItem": {
                "type": "object",
                "additionalProperties": True,
                "oneOf": [
                    {"required": ["ticket"]},
                    {"required": ["type"]},
                    {"required": ["format"]},
                    {"required": ["method"]},
                ],
                "properties": {
                    "ticket": {"type": "string"},
                    "type": {
                        "type": "string",
                        "description": "ticker, trade, orderbook, candle.*, myOrder, myAsset",
                    },
                    "codes": {"type": "array", "items": {"type": "string"}},
                    "format": {
                        "type": "string",
                        "enum": ["DEFAULT", "SIMPLE", "JSON_LIST", "SIMPLE_LIST"],
                    },
                    "method": {"type": "string", "enum": ["LIST_SUBSCRIPTIONS"]},
                },
            },
            "UpbitEventPayload": {
                "type": "object",
                "description": "Upbit upstream response object. Shape varies by stream type.",
                "additionalProperties": True,
            },
            "GatewayErrorPayload": {
                "type": "object",
                "required": ["error"],
                "properties": {"error": {"type": "string"}},
                "additionalProperties": False,
                "examples": [{"error": "Unknown subscription type(s): unknown"}],
            },
        },
    },
}

EVENTS_DOC_HTML = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Upbit Bridge Events API</title>
    <style>
      html, body {{
        height: 100%;
        margin: 0;
        background: #0b1020;
      }}
      #asyncapi {{
        height: 100%;
      }}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/@asyncapi/react-component@1.5.25/styles/default.min.css" />
  </head>
  <body>
    <div id="asyncapi"></div>

    <script src="https://unpkg.com/@asyncapi/react-component@1.5.25/browser/standalone/index.js"></script>
    <script>
      try {{
        AsyncApiStandalone.render(
          {{
            schema: {{
              url: "{EVENTS_DOC_SPEC_PATH}",
              options: {{
                method: "GET",
                mode: "cors",
              }},
            }},
            config: {{
              show: {{
                sidebar: true,
                info: true,
                servers: true,
                operations: true,
                messages: true,
                schemas: true,
              }},
            }},
          }},
          document.getElementById("asyncapi")
        );
      }} catch (err) {{
        document.body.innerHTML = "<pre style='color:#fff;padding:16px'>Failed to load AsyncAPI spec: "
          + err + "</pre>";
      }}
    </script>
  </body>
</html>
"""


async def events_doc(_request):
    return HTMLResponse(EVENTS_DOC_HTML)


async def events_spec(_request):
    return JSONResponse(ASYNCAPI_SPEC)
