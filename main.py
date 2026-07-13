# main.py
import asyncio

from fastmcp import FastMCP
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, UPBIT_BRIDGE_AUTH_TOKEN

from tools.get_ticker import get_ticker
from tools.get_orderbook import get_orderbook
from tools.get_trades import get_trades
from tools.get_candles import get_candles
from tools.get_accounts import get_accounts
from tools.create_order import create_order
from tools.get_orders import get_orders
from tools.get_order import get_order
from tools.get_order_chance import get_order_chance
from tools.cancel_order import cancel_order
from tools.cancel_open_orders import cancel_open_orders
from tools.get_market_summary import get_market_summary
from tools.get_deposits_withdrawals import get_deposits_withdrawals
from tools.create_withdraw import create_withdraw
from tools.get_deposit_coin_address import get_deposit_coin_address
from tools.list_withdraw_coin_addresses import list_withdraw_coin_addresses
from tools.get_wallet_status import get_wallet_status
from tools.technical_analysis import technical_analysis

from prompts.explain_ticker import explain_ticker
from prompts.analyze_portfolio import analyze_portfolio
from prompts.order_help import order_help
from prompts.trading_strategy import trading_strategy

from resources.get_market_list import get_market_list

from mcp_context import patch_fastmcp_context_logging
from mcp_logging import install_tool_call_logging

patch_fastmcp_context_logging()

if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
    print("⚠️  경고: 업비트 API 키가 설정되지 않았습니다. 공개 API만 사용 가능합니다.")
    print("     .env 파일에 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정해주세요.")
else:
    print("✅ 업비트 API 키가 확인되었습니다. 모든 기능을 사용할 수 있습니다.")

mcp = FastMCP(
    "Upbit MCP Server", 
    description="Upbit 암호화폐 거래소 API와 연동된 MCP 서버",
    dependencies=[
        "fastmcp>=0.1.8",
        "upbit-sdk>=0.9.0",
        "python-dotenv",
        "numpy"
    ]
)

mcp.tool()(get_ticker)
mcp.tool()(get_orderbook)
mcp.tool()(get_trades)
mcp.tool()(get_candles)
mcp.tool()(get_accounts)
mcp.tool()(create_order)
mcp.tool()(get_orders)
mcp.tool()(get_order)
mcp.tool()(get_order_chance)
mcp.tool()(cancel_order)
mcp.tool()(cancel_open_orders)
mcp.tool()(get_market_summary)
mcp.tool()(get_deposits_withdrawals)
mcp.tool()(create_withdraw)
mcp.tool()(get_deposit_coin_address)
mcp.tool()(list_withdraw_coin_addresses)
mcp.tool()(get_wallet_status)
mcp.tool()(technical_analysis)

mcp.resource("market://list")(get_market_list)

mcp.prompt()(explain_ticker)
mcp.prompt()(analyze_portfolio)
mcp.prompt()(order_help)
mcp.prompt()(trading_strategy)

install_tool_call_logging(mcp)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upbit MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind for SSE transport (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind for SSE transport (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print(f"업비트 MCP 서버가 {args.transport} 모드로 시작되었습니다!")
    
    if args.transport == "sse":
        from sse_auth import run_sse_async

        mcp.settings.host = args.host
        mcp.settings.port = args.port

        if UPBIT_BRIDGE_AUTH_TOKEN:
            print("🔒 SSE/WebSocket Bearer 토큰 인증이 활성화되었습니다.")
        else:
            print("⚠️  경고: UPBIT_BRIDGE_AUTH_TOKEN이 설정되지 않았습니다. SSE/WebSocket 엔드포인트가 보호되지 않습니다.")

        print(f"📡 WebSocket gateway (public + private): ws://{args.host}:{args.port}/ws/")
        print(f"🛠  REST API v1: http://{args.host}:{args.port}/api/v1/  (docs: /docs/api)")
        if not UPBIT_ACCESS_KEY:
            print("⚠️  경고: API 키가 없어 /ws/ private 스트림(myOrder, myAsset)과 /api/v1 인증 API를 사용할 수 없습니다.")

        asyncio.run(run_sse_async(mcp, token=UPBIT_BRIDGE_AUTH_TOKEN))
    else:
        mcp.run(transport="stdio")