# Upbit Bridge

A unified gateway and bridge for [Upbit](https://upbit.com) Cryptocurrency Exchange OpenAPI using the Model Context Protocol (MCP) and WebSockets. This project provides tools to interact with Upbit exchange services, such as retrieving market data (quotes, orderbooks, trade history, chart data), account information, creating and canceling orders, managing deposits/withdrawals, and performing technical analysis.

## Features

- Market data retrieval (ticker, orderbook, trades, candle data)
- Account information (balance, order history)
- Order creation and cancellation
- Deposit and withdrawal functions
- Technical analysis tools

## Documentation

| 문서 | 설명 |
|------|------|
| [MCP 사용 가이드](docs/mcp_usage.md) | Claude Desktop 및 Cursor 연결 설정 (SSE, stdio) |
| [MCP 도구 소개](docs/mcp-tools.md) | Tool, Resource, Prompt 목록 및 설명 |
| [Upbit SDK ↔ MCP 구현 현황](docs/upbit-sdk-mcp-coverage.md) | SDK 대비 MCP 커버리지 체크리스트 |
| [WebSocket 게이트웨이 사용 가이드](docs/ws_usage.md) | `/ws/` 연결, 구독 예시, public/private 라우팅 |

<details>
  <summary><strong>채팅 예시</strong></summary>
  <br/>
  <p>
    아래는 실제 채팅 예시 이미지입니다.
  </p>
  <img src="./assets/img1.png" alt="example1" width="600"/>
    <img src="./assets/img2.png" alt="example2" width="600"/>
</details>

## Prerequisites

Before you begin, you need to get your Upbit API keys:

1. Create an account on [Upbit](https://upbit.com) if you don't already have one
2. Go to the [Upbit Developer Center](https://upbit.com/service_center/open_api_guide)
3. Create a new API key
4. Make sure to set appropriate permissions (read, trade, withdraw as needed)
5. Store your API keys in a `.env` file (see Usage section)

> 공개 API(시세, 호가, 캔들 등)만 사용할 경우 API 키 없이도 동작합니다.

## Usage

이 MCP 서버는 Docker 컨테이너로 SSE transport(`http://0.0.0.0:8000/sse`)를 통해 실행됩니다.

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만듭니다.

```env
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
UPBIT_MCP_SSE_TOKEN=your_sse_bearer_token_here
```

| 변수 | 필수 | 설명 |
|------|------|------|
| `UPBIT_ACCESS_KEY` | 선택 | 업비트 Access Key (계정·주문·입출금 API) |
| `UPBIT_SECRET_KEY` | 선택 | 업비트 Secret Key |
| `UPBIT_MCP_SSE_TOKEN` | 권장 | SSE/WebSocket 엔드포인트 Bearer 인증 토큰. 미설정 시 `/sse`, `/messages`, `/ws/`가 보호되지 않습니다. |

### 2. Docker 이미지 실행

**GHCR에서 pull (권장)**

```bash
docker pull ghcr.io/suapapa/upbit-bridge:latest

docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-bridge:latest
```

**로컬에서 빌드**

```bash
git clone https://github.com/suapapa/upbit-bridge.git
cd upbit-bridge

docker build -t upbit-bridge .

docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  upbit-bridge
```

컨테이너가 정상 기동되었는지 확인합니다.

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. MCP 클라이언트 연결

Claude Desktop, Cursor 등 MCP 클라이언트에서 Upbit Bridge를 연결하고 사용하는 방법은 **[MCP 사용 가이드](docs/mcp_usage.md)**를 참고하세요. (SSE 및 stdio 전송 방식 모두 지원)

### 4. WebSocket 게이트웨이 (`/ws/`)

단일 `/ws/` 엔드포인트에서 업비트 public 시세(`ticker`, `trade`, `orderbook`, `candle.*`)와 private 계정 스트림(`myOrder`, `myAsset`)을 모두 사용할 수 있습니다. 연결 방법, 구독 예시, 혼합 구독, 에러 처리 등은 **[WebSocket 게이트웨이 사용 가이드](docs/ws_usage.md)**에서 확인하세요.

## Caution

- This server can process real trades, so use it carefully.
- Keep your API keys secure and never commit them to public repositories.
- `UPBIT_MCP_SSE_TOKEN`을 설정하여 SSE 엔드포인트를 외부에 노출할 때 반드시 보호하세요.

## License

MIT
