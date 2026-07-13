"""Account balance endpoints."""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from api.v1.errors import error_response, map_upbit_exception, require_api_keys
from upbit_client import get_authenticated_client, to_serializable


async def list_accounts(_request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    try:
        client = get_authenticated_client()
        accounts = await client.accounts.list()
        return JSONResponse(to_serializable(accounts))
    except Exception as exc:
        return map_upbit_exception(exc)


async def get_account(request: Request) -> JSONResponse:
    if err := require_api_keys():
        return err

    currency = request.path_params["currency"].upper()
    try:
        client = get_authenticated_client()
        accounts = await client.accounts.list()
        serialized = to_serializable(accounts)
        for account in serialized:
            if str(account.get("currency", "")).upper() == currency:
                return JSONResponse(account)
        return error_response(f"잔고에서 '{currency}'를 찾을 수 없습니다.", 404)
    except Exception as exc:
        return map_upbit_exception(exc)
