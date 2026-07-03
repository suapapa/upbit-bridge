# WebSocket 게이트웨이 (`/ws/`) 사용 가이드

Upbit MCP Server의 `/ws/` 엔드포인트는 업비트 WebSocket API를 **하나의 연결**로 사용할 수 있게 해 주는 스마트 게이트웨이입니다.

클라이언트는 업비트 WebSocket 프로토콜을 그대로 따르면 됩니다. 서버가 구독 메시지를 읽어 **public** 스트림과 **private** 스트림을 자동으로 나눠 각각의 upstream에 전달합니다.

| 구분 | 스트림 타입 | 업비트 upstream | API 키 |
|------|-------------|-----------------|--------|
| Public | `ticker`, `trade`, `orderbook`, `candle.*` | `wss://api.upbit.com/websocket/v1` | 불필요 |
| Private | `myOrder`, `myAsset` | `wss://api.upbit.com/websocket/v1/private` | 컨테이너에 설정된 키 사용 |

Private 스트림의 JWT 인증은 **서버가 대신 처리**합니다. 클라이언트가 업비트 Access Key를 직접 넘길 필요는 없습니다.

---

## 시작하기

### 1. 서버 실행

Docker로 SSE transport 모드로 기동합니다 (기본 포트 `8000`).

```bash
docker run -d \
  --name upbit-mcp-server \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-mcp-server:latest
```

로컬에서 직접 실행할 경우:

```bash
python main.py --transport sse
```

### 2. 환경 변수

| 변수 | Public 스트림 | Private 스트림 | 설명 |
|------|:-------------:|:--------------:|------|
| `UPBIT_MCP_SSE_TOKEN` | 권장 | 권장 | `/ws/` 접속 시 Bearer 토큰. 미설정 시 엔드포인트가 보호되지 않습니다. |
| `UPBIT_ACCESS_KEY` | — | **필수** | Private 스트림용 |
| `UPBIT_SECRET_KEY` | — | **필수** | Private 스트림용 |

### 3. 연결 URL

```
ws://localhost:8000/ws/
```

프로덕션에서는 `wss://`와 실제 호스트를 사용합니다.

`UPBIT_MCP_SSE_TOKEN`이 설정된 경우, WebSocket handshake 시 헤더에 Bearer 토큰을 포함합니다.

```
Authorization: Bearer your_sse_bearer_token_here
```

---

## 메시지 형식

업비트 WebSocket과 동일하게, **JSON 배열**을 텍스트로 전송합니다.

```json
[
  {"ticket": "요청을 구분하는 고유 ID (UUID 권장)"},
  {"type": "스트림 종류", "codes": ["KRW-BTC"]},
  {"format": "DEFAULT"}
]
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `ticket` | 권장 | 요청 식별자. UUID를 쓰면 충돌을 피하기 쉽습니다. |
| `type` | ✅ | 구독할 스트림 종류 (아래 표 참고) |
| `codes` | 타입별 상이 | 마켓 코드 목록. `myAsset`에는 사용하지 않습니다. |
| `format` | 선택 | `DEFAULT`, `SIMPLE`, `JSON_LIST`, `SIMPLE_LIST` |

### 지원하는 스트림 타입

**Public** (시장 전체 데이터)

| `type` | 설명 |
|--------|------|
| `ticker` | 현재가 |
| `trade` | 실시간 체결 |
| `orderbook` | 호가 |
| `candle.1s`, `candle.1m`, `candle.5m` … | 실시간 캔들 (`candle.{간격}`) |

**Private** (내 계정 데이터)

| `type` | 설명 |
|--------|------|
| `myOrder` | 내 주문 상태 변화 (체결, 취소 등) |
| `myAsset` | 내 잔고 변화 |

---

## 사용 예시

### Python — 현재가 구독 (Public)

API 키 없이도 동작합니다.

```python
import asyncio
import json
import uuid

import websockets

async def main():
    uri = "ws://localhost:8000/ws/"
    headers = {"Authorization": "Bearer your_sse_bearer_token_here"}

    async with websockets.connect(uri, additional_headers=headers) as ws:
        await ws.send(json.dumps([
            {"ticket": str(uuid.uuid4())},
            {"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]},
            {"format": "DEFAULT"},
        ]))

        async for message in ws:
            print(message)

asyncio.run(main())
```

### Python — 실시간 체결 구독 (Public)

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "trade", "codes": ["KRW-BTC"]},
    {"format": "SIMPLE"},
]))
```

### Python — 호가 구독 (Public)

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "orderbook", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

### Python — 내 주문 구독 (Private)

컨테이너에 `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY`가 설정되어 있어야 합니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myOrder", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

`codes`를 생략하거나 빈 배열로내면 전체 마켓의 내 주문을 받을 수 있습니다 (업비트 API 동작과 동일).

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myOrder"},
    {"format": "DEFAULT"},
]))
```

### Python — 내 잔고 구독 (Private)

`myAsset`은 마켓 코드(`codes`)를 받지 않습니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myAsset"},
    {"format": "DEFAULT"},
]))
```

### Python — Public + Private 혼합 구독

한 메시지에 public과 private 타입을 함께 넣을 수 있습니다. 서버가 자동으로 분리해 각 upstream에 전달합니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "ticker", "codes": ["KRW-BTC"]},
    {"type": "myOrder", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

이 경우 서버 내부에서는 다음 두 메시지로 나뉩니다.

- Public upstream → `ticker` 구독
- Private upstream → `myOrder` 구독

수신 이벤트는 **하나의 WebSocket 연결**으로 모두 전달됩니다.

### Python — 구독 목록 조회

연결이 열린 뒤, 현재 구독 중인 스트림을 확인할 수 있습니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"method": "LIST_SUBSCRIPTIONS"},
]))
```

Public과 Private upstream이 모두 활성화된 경우, **각 upstream의 응답이 별도 메시지**로 돌아옵니다.

### Python — 연결 후 추가 구독

WebSocket 연결을 유지한 채 새 구독 메시지를내면 됩니다. 필요한 upstream만 lazy하게 연결됩니다.

```python
async with websockets.connect(uri, additional_headers=headers) as ws:
    # 먼저 ticker만
    await ws.send(json.dumps([
        {"ticket": str(uuid.uuid4())},
        {"type": "ticker", "codes": ["KRW-BTC"]},
    ]))

    # 이후 myOrder 추가
    await ws.send(json.dumps([
        {"ticket": str(uuid.uuid4())},
        {"type": "myOrder", "codes": ["KRW-BTC"]},
    ]))

    async for message in ws:
        print(message)
```

---

## 완성 예제 스크립트

아래 스크립트는 연결 → 혼합 구독 → 30초간 수신 → 종료까지 한 번에 보여 줍니다.

```python
import asyncio
import json
import uuid

import websockets

WS_URL = "ws://localhost:8000/ws/"
TOKEN = "your_sse_bearer_token_here"  # UPBIT_MCP_SSE_TOKEN 미설정 시 headers 생략 가능


async def main():
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None

    async with websockets.connect(WS_URL, additional_headers=headers) as ws:
        await ws.send(json.dumps([
            {"ticket": str(uuid.uuid4())},
            {"type": "ticker", "codes": ["KRW-BTC"]},
            {"type": "myOrder", "codes": ["KRW-BTC"]},
            {"format": "DEFAULT"},
        ]))
        print("구독 완료. 이벤트 수신 중... (30초)")

        try:
            async with asyncio.timeout(30):
                async for message in ws:
                    data = json.loads(message)
                    stream_type = data.get("type", "unknown")
                    print(f"[{stream_type}] {message[:120]}...")
        except TimeoutError:
            print("종료")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 동작 원리

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as MCP_Server_ws
    participant Public as ws_public
    participant Private as ws_private

    Client->>Gateway: WebSocket connect /ws/
    Client->>Gateway: 구독 JSON (ticker + myOrder)
    Gateway->>Gateway: 메시지 파싱 및 분리
    Gateway->>Public: ticker 구독
    Gateway->>Private: myOrder 구독 (JWT 자동)
    Public-->>Gateway: ticker 이벤트
    Private-->>Gateway: myOrder 이벤트
    Gateway-->>Client: 이벤트 relay
```

- **Lazy connect**: public만 쓰면 `ws_public`만, private만 쓰면 `ws_private`만 연결됩니다.
- **1:1 세션**: 클라이언트 WebSocket 하나당 upstream은 최대 2개(public + private)입니다.
- **프로토콜 호환**: 업비트 공식 WebSocket 문서의 메시지 형식을 그대로 사용합니다.

---

## 에러 응답

게이트웨이가 메시지를 처리하지 못하면 JSON 형태의 에러를 돌려줍니다.

```json
{"error": "API 키가 설정되지 않았습니다. private 스트림에는 UPBIT_ACCESS_KEY가 필요합니다."}
```

| 상황 | 에러 메시지 예시 |
|------|------------------|
| Private 구독인데 API 키 없음 | `API 키가 설정되지 않았습니다...` |
| 알 수 없는 `type` | `Unknown subscription type(s): ...` |
| 빈 구독 메시지 | `No subscription types in message` |
| 잘못된 JSON | `Expected a JSON array` |
| Bearer 토큰 불일치 | WebSocket 연결 자체가 거부됨 (HTTP 4401) |

---

## 자주 묻는 질문

### 업비트 API 키를 클라이언트에 넣어야 하나요?

아닙니다. Private 스트림은 **서버 컨테이너의** `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY`로 인증합니다. 클라이언트는 `UPBIT_MCP_SSE_TOKEN`(설정한 경우)만 알면 됩니다.

### Public만 쓰고 싶은데 API 키가 꼭 필요한가요?

아닙니다. `ticker`, `trade`, `orderbook`, `candle.*` 구독은 API 키 없이 사용할 수 있습니다.

### 업비트에 직접 연결하는 것과 뭐가 다른가요?

- Private 스트림: 클라이언트가 JWT를 만들 필요 없음
- 단일 URL: public/private를 하나의 `ws://host/ws/`로 통합
- 접근 제어: `UPBIT_MCP_SSE_TOKEN`으로 게이트웨이 자체를 보호 가능

### REST MCP Tool과 같이 쓸 수 있나요?

네. 같은 컨테이너에서 `/sse`(MCP Tool)와 `/ws/`(실시간 스트림)를 동시에 제공합니다. 시세 조회는 MCP Tool, 실시간 모니터링은 WebSocket으로 나눠 쓰면 됩니다.

---

## 참고 링크

- [업비트 WebSocket API 문서](https://docs.upbit.com/reference/websocket)
- [Upbit SDK ↔ MCP 구현 현황](./upbit-sdk-mcp-coverage.md)
- [프로젝트 README](../README.md) — Docker 실행 및 환경 변수 설정

---

## 주의사항

- Private 스트림에는 **실제 계정의 주문·잔고 정보**가 포함됩니다. `UPBIT_MCP_SSE_TOKEN`을 반드시 설정하세요.
- 이 서버는 실거래 API 키로 동작할 수 있습니다. 키 권한(조회/주문/출금)을 최소한으로 설정하세요.
- WebSocket은 장시간 연결입니다. 클라이언트 측에서 재연결 로직을 구현하는 것을 권장합니다.
