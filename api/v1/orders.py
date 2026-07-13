"""Order endpoints."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from api.v1.errors import error_response, map_upbit_exception, require_api_keys
from config import is_valid_market, validate_order_params
from upbit_client import get_authenticated_client, to_serializable


def _split_csv(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = ",".join(part.strip() for part in value.split(",") if part.strip())
    return cleaned or None


async def create_order(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    try:
        body = await request.json()
    except Exception:
        return error_response("JSON body가 필요합니다.")

    if not isinstance(body, dict):
        return error_response("JSON object body가 필요합니다.")

    market = body.get("market")
    side = body.get("side")
    ord_type = body.get("ord_type")
    volume = body.get("volume")
    price = body.get("price")

    if not isinstance(market, str) or not isinstance(side, str) or not isinstance(ord_type, str):
        return error_response("market, side, ord_type은 필수 문자열입니다.")

    volume_str = None if volume is None else str(volume)
    price_str = None if price is None else str(price)

    ok, message = validate_order_params(market, side, ord_type, volume_str, price_str)
    if not ok:
        return error_response(message)

    params: dict[str, Any] = {
        "market": market,
        "side": side,
        "ord_type": ord_type,
    }
    if volume_str is not None:
        params["volume"] = volume_str
    if price_str is not None:
        params["price"] = price_str

    try:
        client = get_authenticated_client()
        order = await client.orders.create(**params)
        return JSONResponse(to_serializable(order), status_code=201)
    except Exception as exc:
        return map_upbit_exception(exc)


async def list_orders(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    market = request.query_params.get("market")
    state = request.query_params.get("state", "wait")
    if state not in ("wait", "done", "cancel"):
        return error_response("state는 wait, done, cancel 중 하나여야 합니다.")

    if market and not is_valid_market(market):
        return error_response("유효하지 않은 마켓 코드입니다.")

    try:
        page = int(request.query_params.get("page", "1"))
        limit = int(request.query_params.get("limit", "100"))
    except ValueError:
        return error_response("page와 limit는 정수여야 합니다.")

    if page < 1:
        return error_response("page는 1 이상이어야 합니다.")
    if not 1 <= limit <= 100:
        return error_response("limit는 1~100 사이여야 합니다.")

    try:
        client = get_authenticated_client()
        if state == "wait":
            params: dict[str, Any] = {"page": page, "limit": limit}
            if market:
                params["market"] = market
            page_result = await client.orders.list_open(**params)
            return JSONResponse(to_serializable(page_result.items))

        params = {"limit": limit, "state": state}
        if market:
            params["market"] = market
        orders = await client.orders.list_closed(**params)
        return JSONResponse(to_serializable(orders))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_order(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    uuid = request.path_params["uuid"]
    try:
        client = get_authenticated_client()
        order = await client.orders.retrieve(uuid=uuid)
        return JSONResponse(to_serializable(order))
    except Exception as exc:
        return map_upbit_exception(exc)


async def cancel_order(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    uuid = request.path_params["uuid"]
    try:
        client = get_authenticated_client()
        order = await client.orders.cancel(uuid=uuid)
        return JSONResponse(to_serializable(order))
    except Exception as exc:
        return map_upbit_exception(exc)


async def cancel_open_orders(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    cancel_side = request.query_params.get("cancel_side", "all")
    if cancel_side not in ("bid", "ask", "all"):
        return error_response("cancel_side는 bid, ask, all 중 하나여야 합니다.")

    order_by = request.query_params.get("order_by", "desc")
    if order_by not in ("asc", "desc"):
        return error_response("order_by는 asc 또는 desc여야 합니다.")

    try:
        count = int(request.query_params.get("count", "20"))
    except ValueError:
        return error_response("count는 정수여야 합니다.")

    if not 1 <= count <= 300:
        return error_response("count는 1~300 사이여야 합니다.")

    params: dict[str, Any] = {
        "cancel_side": cancel_side,
        "count": count,
        "order_by": order_by,
    }
    if pairs := _split_csv(request.query_params.get("pairs")):
        params["pairs"] = pairs
    if excluded_pairs := _split_csv(request.query_params.get("excluded_pairs")):
        params["excluded_pairs"] = excluded_pairs
    if quote_currencies := _split_csv(request.query_params.get("quote_currencies")):
        params["quote_currencies"] = quote_currencies

    try:
        client = get_authenticated_client()
        result = await client.orders.cancel_open(**params)
        return JSONResponse(to_serializable(result))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_order_chance(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    market = request.query_params.get("market")
    if not market:
        return error_response("market 쿼리 파라미터가 필요합니다.")
    if not is_valid_market(market):
        return error_response("유효하지 않은 마켓 코드입니다.")

    try:
        client = get_authenticated_client()
        chance = await client.orders.retrieve_chance(market=market)
        return JSONResponse(to_serializable(chance))
    except Exception as exc:
        return map_upbit_exception(exc)
