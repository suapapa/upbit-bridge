"""HTTP error helpers for REST API v1."""

from __future__ import annotations

from upbit import APIError, APIStatusError, UpbitError

from starlette.responses import JSONResponse


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        {"error": {"message": message, "status": status_code}},
        status_code=status_code,
    )


def require_api_keys() -> JSONResponse | None:
    from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY

    if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
        return error_response(
            "업비트 API 키가 설정되지 않았습니다. "
            "컨테이너에 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정해주세요.",
            status_code=503,
        )
    return None


def map_upbit_exception(exc: Exception) -> JSONResponse:
    if isinstance(exc, APIStatusError):
        status = exc.status_code if 400 <= exc.status_code < 600 else 502
        return error_response(f"업비트 API 오류: {exc.status_code} - {exc.message}", status)
    if isinstance(exc, APIError):
        return error_response(f"업비트 API 오류: {exc.message}", 502)
    if isinstance(exc, UpbitError):
        return error_response(f"업비트 API 오류: {exc}", 502)
    return error_response(f"API 호출 중 오류 발생: {exc}", 500)
