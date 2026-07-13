"""OpenAPI docs routes for REST API v1."""

from starlette.responses import HTMLResponse, JSONResponse

API_DOC_PATH = "/docs/api"
API_DOC_SPEC_PATH = "/docs/api.json"
API_PUBLIC_DOC_PATHS = (API_DOC_PATH, API_DOC_SPEC_PATH)

OPENAPI_SPEC: dict = {
    "openapi": "3.0.3",
    "info": {
        "title": "Upbit Bridge REST API",
        "version": "1.0.0",
        "description": (
            "Script-friendly REST endpoints for account balances and order management. "
            "Requires `Authorization: Bearer <UPBIT_BRIDGE_AUTH_TOKEN>` when the token is set. "
            "Upbit API keys stay on the server."
        ),
    },
    "servers": [{"url": "http://localhost:8000", "description": "Local development server"}],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "UPBIT_BRIDGE_AUTH_TOKEN",
            }
        },
        "schemas": {
            "Error": {
                "type": "object",
                "required": ["error"],
                "properties": {
                    "error": {
                        "type": "object",
                        "required": ["message", "status"],
                        "properties": {
                            "message": {"type": "string"},
                            "status": {"type": "integer"},
                        },
                    }
                },
            },
            "Account": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "currency": {"type": "string", "example": "KRW"},
                    "balance": {"type": "string"},
                    "locked": {"type": "string"},
                    "avg_buy_price": {"type": "string"},
                    "avg_buy_price_modified": {"type": "boolean"},
                    "unit_currency": {"type": "string", "example": "KRW"},
                },
            },
            "Order": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "uuid": {"type": "string", "format": "uuid"},
                    "side": {"type": "string", "enum": ["bid", "ask"]},
                    "ord_type": {"type": "string", "enum": ["limit", "price", "market"]},
                    "price": {"type": "string"},
                    "state": {"type": "string"},
                    "market": {"type": "string", "example": "KRW-BTC"},
                    "volume": {"type": "string"},
                    "remaining_volume": {"type": "string"},
                    "executed_volume": {"type": "string"},
                },
            },
            "CreateOrderRequest": {
                "type": "object",
                "required": ["market", "side", "ord_type"],
                "properties": {
                    "market": {"type": "string", "example": "KRW-BTC"},
                    "side": {"type": "string", "enum": ["bid", "ask"]},
                    "ord_type": {
                        "type": "string",
                        "enum": ["limit", "price", "market"],
                        "description": "limit=지정가, price=시장가 매수, market=시장가 매도",
                    },
                    "volume": {
                        "type": "string",
                        "description": "필수: limit, market(매도)",
                    },
                    "price": {
                        "type": "string",
                        "description": "필수: limit, price(시장가 매수 — 주문 총액)",
                    },
                },
            },
        },
    },
    "security": [{"BearerAuth": []}],
    "paths": {
        "/api/v1/accounts": {
            "get": {
                "summary": "List account balances",
                "operationId": "listAccounts",
                "tags": ["Accounts"],
                "responses": {
                    "200": {
                        "description": "Account list",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Account"},
                                }
                            }
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "503": {
                        "description": "Upbit API keys not configured",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
            }
        },
        "/api/v1/accounts/{currency}": {
            "get": {
                "summary": "Get a single currency balance",
                "operationId": "getAccount",
                "tags": ["Accounts"],
                "parameters": [
                    {
                        "name": "currency",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "example": "KRW"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Account",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Account"}
                            }
                        },
                    },
                    "404": {
                        "description": "Currency not found",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
            }
        },
        "/api/v1/orders": {
            "get": {
                "summary": "List orders",
                "operationId": "listOrders",
                "tags": ["Orders"],
                "parameters": [
                    {
                        "name": "market",
                        "in": "query",
                        "schema": {"type": "string", "example": "KRW-BTC"},
                    },
                    {
                        "name": "state",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["wait", "done", "cancel"],
                            "default": "wait",
                        },
                    },
                    {
                        "name": "page",
                        "in": "query",
                        "schema": {"type": "integer", "minimum": 1, "default": 1},
                        "description": "Used only when state=wait",
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 100,
                        },
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Order list",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Order"},
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "summary": "Create an order",
                "operationId": "createOrder",
                "tags": ["Orders"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateOrderRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Created order",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
            },
            "delete": {
                "summary": "Cancel open orders",
                "operationId": "cancelOpenOrders",
                "tags": ["Orders"],
                "parameters": [
                    {
                        "name": "cancel_side",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["bid", "ask", "all"],
                            "default": "all",
                        },
                    },
                    {
                        "name": "count",
                        "in": "query",
                        "schema": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 300,
                            "default": 20,
                        },
                    },
                    {
                        "name": "pairs",
                        "in": "query",
                        "schema": {"type": "string"},
                        "description": "Comma-separated markets",
                    },
                    {
                        "name": "excluded_pairs",
                        "in": "query",
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "quote_currencies",
                        "in": "query",
                        "schema": {"type": "string", "example": "KRW"},
                    },
                    {
                        "name": "order_by",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "default": "desc",
                        },
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Cancel result",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "additionalProperties": True}
                            }
                        },
                    }
                },
            },
        },
        "/api/v1/orders/chance": {
            "get": {
                "summary": "Get order chance for a market",
                "operationId": "getOrderChance",
                "tags": ["Orders"],
                "parameters": [
                    {
                        "name": "market",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "example": "KRW-BTC"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order chance",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "additionalProperties": True}
                            }
                        },
                    }
                },
            }
        },
        "/api/v1/orders/{uuid}": {
            "get": {
                "summary": "Get an order by UUID",
                "operationId": "getOrder",
                "tags": ["Orders"],
                "parameters": [
                    {
                        "name": "uuid",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Order",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    }
                },
            },
            "delete": {
                "summary": "Cancel an order by UUID",
                "operationId": "cancelOrder",
                "tags": ["Orders"],
                "parameters": [
                    {
                        "name": "uuid",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Cancelled order",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    }
                },
            },
        },
    },
}

API_DOC_HTML = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Upbit Bridge REST API</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
    <style>
      body {{
        margin: 0;
        background: #0b1020;
      }}
      .swagger-ui .topbar {{
        display: none;
      }}
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({{
        url: "{API_DOC_SPEC_PATH}",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
      }});
    </script>
  </body>
</html>
"""


async def api_doc(_request):
    return HTMLResponse(API_DOC_HTML)


async def api_spec(_request):
    return JSONResponse(OPENAPI_SPEC)
