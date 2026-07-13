"""Starlette route table for REST API v1."""

from starlette.routing import Route

from api.v1 import accounts, orders

V1_ROUTES = [
    Route("/api/v1/accounts", endpoint=accounts.list_accounts, methods=["GET"]),
    Route("/api/v1/accounts/{currency}", endpoint=accounts.get_account, methods=["GET"]),
    # Static path before /orders/{uuid}
    Route("/api/v1/orders/chance", endpoint=orders.get_order_chance, methods=["GET"]),
    Route("/api/v1/orders", endpoint=orders.create_order, methods=["POST"]),
    Route("/api/v1/orders", endpoint=orders.list_orders, methods=["GET"]),
    Route("/api/v1/orders", endpoint=orders.cancel_open_orders, methods=["DELETE"]),
    Route("/api/v1/orders/{uuid}", endpoint=orders.get_order, methods=["GET"]),
    Route("/api/v1/orders/{uuid}", endpoint=orders.cancel_order, methods=["DELETE"]),
]
