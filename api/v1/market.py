"""Public market data endpoints."""

from __future__ import annotations

from typing import Any, Literal, cast

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from api.v1.errors import error_response, map_upbit_exception
from config import is_valid_interval, is_valid_market
from format_output import format_candles_csv
from upbit_client import get_public_client, to_serializable

CANDLE_METHODS = {
    "second": "list_seconds",
    "day": "list_days",
    "week": "list_weeks",
    "month": "list_months",
    "year": "list_years",
}

MinuteUnit = Literal[1, 3, 5, 10, 15, 30, 60, 240]

MINUTE_UNITS: dict[str, MinuteUnit] = {
    "minute1": 1,
    "minute3": 3,
    "minute5": 5,
    "minute10": 10,
    "minute15": 15,
    "minute30": 30,
    "minute60": 60,
    "minute240": 240,
}


def _parse_markets(request: Request) -> list[str] | JSONResponse:
    raw = request.query_params.get("markets") or request.query_params.get("market")
    if not raw:
        return error_response("markets 또는 market 쿼리 파라미터가 필요합니다.")

    markets = [part.strip().upper() for part in raw.split(",") if part.strip()]
    if not markets:
        return error_response("markets 또는 market 쿼리 파라미터가 필요합니다.")

    for market in markets:
        if not is_valid_market(market):
            return error_response(f"유효하지 않은 마켓 코드입니다: {market}")
    return markets


def _parse_single_market(request: Request) -> str | JSONResponse:
    raw = request.query_params.get("market") or request.query_params.get("markets")
    if not raw:
        return error_response("market 쿼리 파라미터가 필요합니다.")

    market = raw.split(",")[0].strip().upper()
    if not market or not is_valid_market(market):
        return error_response("유효하지 않은 마켓 코드입니다.")
    return market


async def list_markets(request: Request) -> JSONResponse:
    details_raw = request.query_params.get("details", "false").lower()
    is_details = details_raw in ("1", "true", "yes")

    try:
        client = get_public_client()
        markets = await client.trading_pairs.list(is_details=is_details)
        return JSONResponse(to_serializable(markets))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_ticker(request: Request) -> JSONResponse:
    markets = _parse_markets(request)
    if isinstance(markets, JSONResponse):
        return markets

    try:
        client = get_public_client()
        tickers = await client.tickers.list_by_trading_pairs(markets=",".join(markets))
        return JSONResponse(to_serializable(tickers))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_orderbook(request: Request) -> JSONResponse:
    markets = _parse_markets(request)
    if isinstance(markets, JSONResponse):
        return markets

    params: dict[str, Any] = {"markets": ",".join(markets)}
    if count_raw := request.query_params.get("count"):
        try:
            count = int(count_raw)
        except ValueError:
            return error_response("count는 정수여야 합니다.")
        if not 1 <= count <= 30:
            return error_response("count는 1~30 사이여야 합니다.")
        params["count"] = count

    try:
        client = get_public_client()
        orderbooks = await client.orderbooks.list(**params)
        return JSONResponse(to_serializable(orderbooks))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_trades(request: Request) -> JSONResponse:
    market = _parse_single_market(request)
    if isinstance(market, JSONResponse):
        return market

    params: dict[str, Any] = {"market": market}
    if count_raw := request.query_params.get("count"):
        try:
            count = int(count_raw)
        except ValueError:
            return error_response("count는 정수여야 합니다.")
        if not 1 <= count <= 500:
            return error_response("count는 1~500 사이여야 합니다.")
        params["count"] = count

    if cursor := request.query_params.get("cursor"):
        params["cursor"] = cursor
    if to := request.query_params.get("to"):
        params["to"] = to
    if days_ago_raw := request.query_params.get("days_ago"):
        try:
            params["days_ago"] = int(days_ago_raw)
        except ValueError:
            return error_response("days_ago는 정수여야 합니다.")

    try:
        client = get_public_client()
        trades = await client.trades.list(**params)
        return JSONResponse(to_serializable(trades))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_candles(request: Request) -> Response:
    market = _parse_single_market(request)
    if isinstance(market, JSONResponse):
        return market

    interval = request.query_params.get("interval", "minute1")
    if not is_valid_interval(interval):
        return error_response(
            "interval은 second, minute1|3|5|10|15|30|60|240, day, week, month, year 중 하나여야 합니다."
        )

    try:
        count = int(request.query_params.get("count", "200"))
    except ValueError:
        return error_response("count는 정수여야 합니다.")
    if not 1 <= count <= 200:
        return error_response("count는 1~200 사이여야 합니다.")

    fmt = request.query_params.get("format", "json").lower()
    if fmt not in ("json", "csv"):
        return error_response("format은 json 또는 csv여야 합니다.")

    params: dict[str, Any] = {"market": market, "count": count}
    if to := request.query_params.get("to"):
        params["to"] = to

    try:
        client = get_public_client()
        candles_resource = client.candles

        if interval in MINUTE_UNITS:
            candles = await candles_resource.list_minutes(MINUTE_UNITS[interval], **params)
        else:
            method = getattr(candles_resource, CANDLE_METHODS[interval])
            candles = await method(**params)

        candle_dicts = cast(list[dict[str, Any]], to_serializable(candles))
        if fmt == "csv":
            return PlainTextResponse(
                format_candles_csv(candle_dicts, market, interval),
                media_type="text/csv; charset=utf-8",
            )
        return JSONResponse(candle_dicts)
    except Exception as exc:
        return map_upbit_exception(exc)
