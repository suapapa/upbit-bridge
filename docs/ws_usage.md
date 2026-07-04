# WebSocket 게이트웨이(`/ws/`) 사용 가이드

Upbit Bridge의 `/ws/` 엔드포인트는 업비트 WebSocket API를 **단 하나의 연결**로 편리하게 이용하도록 돕는 스마트 게이트웨이입니다.

클라이언트는 업비트가 제공하는 기존 WebSocket 프로토콜 명세를 그대로 따르면 됩니다. 게이트웨이 서버가 클라이언트의 구독 메시지를 분석하여 **공개(public)** 스트림과 **비공개(private)** 스트림으로 자동 분류한 뒤, 각각의 업스트림(upstream) 서버로 안전하게 전달합니다.

| 구분 | 스트림 유형 | 업비트 업스트림 주소 | API 키 |
|------|-------------|-----------------|--------|
| 공개 (Public) | `ticker`, `trade`, `orderbook`, `candle.*` | `wss://api.upbit.com/websocket/v1` | 불필요 |
| 비공개 (Private) | `myOrder`, `myAsset` | `wss://api.upbit.com/websocket/v1/private` | 컨테이너에 등록된 API 키 사용 |

비공개 스트림에 필요한 JWT 인증 절차는 **게이트웨이 서버가 대신 처리**합니다. 따라서 클라이언트가 업비트 Access Key를 직접 전송할 필요가 없어 보안상 매우 안전합니다.

---

## 시작하기

### 1. 서버 실행

Docker를 사용하여 SSE 전송 모드로 구동합니다. (기본 포트는 `8000`입니다)

```bash
docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-bridge:latest
```

로컬 환경에서 직접 실행할 때는 아래 명령어를 입력합니다.

```bash
python main.py --transport sse
```

### 2. 환경 변수 설정

| 변수명 | 공개 스트림 | 비공개 스트림 | 설명 |
|------|:-------------:|:--------------:|------|
| `UPBIT_BRIDGE_AUTH_TOKEN` | 권장 | 권장 | `/ws/` 경로 접속 시 사용할 Bearer 토큰입니다. 설정하지 않으면 엔드포인트가 보호되지 않습니다. |
| `UPBIT_ACCESS_KEY` | — | **필수** | 비공개 스트림 연결용 Access Key |
| `UPBIT_SECRET_KEY` | — | **필수** | 비공개 스트림 연결용 Secret Key |

### 3. 연결 주소(URL)

```
ws://localhost:8000/ws/
```

실제 서비스 배포 환경(프로덕션)에서는 안전한 `wss://` 프로토콜과 도메인 호스트 주소를 활용해 주세요.

`UPBIT_BRIDGE_AUTH_TOKEN`이 활성화되어 있다면, WebSocket 연결 요청(Handshake) 시 아래와 같이 헤더에 Bearer 토큰을 담아서 보냅니다.

```
Authorization: Bearer your_sse_bearer_token_here
```

---

## 메시지 규격

업비트 공식 WebSocket 규격과 마찬가지로, **JSON 배열** 형태의 텍스트 메시지를 보냅니다.

```json
[
  {"ticket": "요청을 구분하기 위한 고유 ID (UUID 권장)"},
  {"type": "스트림 유형", "codes": ["KRW-BTC"]},
  {"format": "DEFAULT"}
]
```

| 필드명 | 필수 여부 | 설명 |
|------|------|------|
| `ticket` | 권장 | 요청 식별자입니다. UUID를 지정하면 충돌을 효과적으로 방지할 수 있습니다. |
| `type` | ✅ | 구독하려는 스트림의 종류 (아래 표 참고) |
| `codes` | 유형별 상이 | 마켓 코드 목록입니다. `myAsset` 유형에는 기입하지 않습니다. |
| `format` | 선택 | 데이터 포맷 지정 (`DEFAULT`, `SIMPLE`, `JSON_LIST`, `SIMPLE_LIST`) |

### 지원하는 스트림 종류

**공개 스트림 (시장 전체 공통 데이터)**

| `type` 값 | 설명 |
|--------|------|
| `ticker` | 현재가 정보 |
| `trade` | 실시간 체결 내역 |
| `orderbook` | 호가창 스냅샷 |
| `candle.1s`, `candle.1m`, `candle.5m` … | 실시간 캔들 데이터 (`candle.{간격}`) |

**비공개 스트림 (사용자 개인 계정 데이터)**

| `type` 값 | 설명 |
|--------|------|
| `myOrder` | 내 주문 상태 변화 알림 (체결, 취소 등) |
| `myAsset` | 내 잔고 변동 알림 |

---

## 활용 예시 (Python)

### 1. 현재가 구독하기 (공개 스트림)

API 키 설정 없이도 원활히 작동합니다.

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

### 2. 실시간 체결 내역 구독하기 (공개 스트림)

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "trade", "codes": ["KRW-BTC"]},
    {"format": "SIMPLE"},
]))
```

### 3. 호가 정보 구독하기 (공개 스트림)

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "orderbook", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

### 4. 내 주문 정보 구독하기 (비공개 스트림)

게이트웨이 서버 컨테이너에 `UPBIT_ACCESS_KEY`와 `UPBIT_SECRET_KEY`가 올바르게 설정되어 있어야 합니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myOrder", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

`codes` 필드를 아예 생략하거나 빈 배열로 보내면, 업비트 API 본래 스펙에 따라 마켓 구분 없이 내 모든 주문 현황을 실시간으로 수신합니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myOrder"},
    {"format": "DEFAULT"},
]))
```

### 5. 내 보유 자산 구독하기 (비공개 스트림)

`myAsset` 유형은 별도의 마켓 코드(`codes`) 필드가 필요하지 않습니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "myAsset"},
    {"format": "DEFAULT"},
]))
```

### 6. 공개 및 비공개 채널 혼합 구독하기

하나의 JSON 구독 메시지에 공개와 비공개 타입을 섞어서 보낼 수 있습니다. 게이트웨이가 수신 즉시 이를 분류해 각 업스트림에 전달합니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"type": "ticker", "codes": ["KRW-BTC"]},
    {"type": "myOrder", "codes": ["KRW-BTC"]},
    {"format": "DEFAULT"},
]))
```

이 메시지를 받으면 서버 내부에서 아래와 같이 두 갈래로 나눕니다.

- 공개 업스트림 전송 → `ticker` 채널 구독
- 비공개 업스트림 전송 → `myOrder` 채널 구독

이후 발생하는 모든 실시간 이벤트는 **단 하나의 클라이언트 WebSocket 연결**을 통해 통합 전달됩니다.

### 7. 구독 중인 목록 조회하기

WebSocket 연결이 활성화된 상태에서 현재 구독하고 있는 스트림 정보를 확인할 수 있습니다.

```python
await ws.send(json.dumps([
    {"ticket": str(uuid.uuid4())},
    {"method": "LIST_SUBSCRIPTIONS"},
]))
```

공개 및 비공개 업스트림 채널이 모두 활성화되어 있는 경우, **각 업스트림의 응답 결과가 서로 다른 별개의 메시지**로 반환됩니다.

### 8. 연결 상태에서 추가로 구독하기

WebSocket 연결을 해제하지 않고 새로운 구독 메시지를 보낼 수 있습니다. 이 경우 필요한 업스트림 채널이 그 시점에 실시간(Lazy)으로 연결됩니다.

```python
async with websockets.connect(uri, additional_headers=headers) as ws:
    # 먼저 ticker 스트림만 구독
    await ws.send(json.dumps([
        {"ticket": str(uuid.uuid4())},
        {"type": "ticker", "codes": ["KRW-BTC"]},
    ]))

    # 이후 동일한 연결 상에서 myOrder 스트림을 추가로 구독
    await ws.send(json.dumps([
        {"ticket": str(uuid.uuid4())},
        {"type": "myOrder", "codes": ["KRW-BTC"]},
    ]))

    async for message in ws:
        print(message)
```

---

## 전체 실행 예제 스크립트

아래 Python 스크립트는 연결 수립, 혼합 구독 요청, 30초간의 이벤트 실시간 수신 및 연결 종료까지의 전 과정을 보여줍니다.

```python
import asyncio
import json
import uuid

import websockets

WS_URL = "ws://localhost:8000/ws/"
TOKEN = "your_bearer_token_here"  # UPBIT_BRIDGE_AUTH_TOKEN이 설정되지 않은 상태라면 headers 옵션을 비워두어도 무방합니다.


async def main():
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None

    async with websockets.connect(WS_URL, additional_headers=headers) as ws:
        await ws.send(json.dumps([
            {"ticket": str(uuid.uuid4())},
            {"type": "ticker", "codes": ["KRW-BTC"]},
            {"type": "myOrder", "codes": ["KRW-BTC"]},
            {"format": "DEFAULT"},
        ]))
        print("구독 요청이 완료되었습니다. 이벤트를 기다리는 중입니다... (30초 동안 유지)")

        try:
            async with asyncio.timeout(30):
                async for message in ws:
                    data = json.loads(message)
                    stream_type = data.get("type", "unknown")
                    print(f"[{stream_type}] {message[:120]}...")
        except TimeoutError:
            print("대기 시간이 만료되어 연결을 안전하게 마칩니다.")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 내부 동작 아키텍처

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as MCP_Server_ws
    participant Public as ws_public
    participant Private as ws_private

    Client->>Gateway: WebSocket 연결 요청 (/ws/)
    Client->>Gateway: 구독 JSON 요청 (ticker + myOrder)
    Gateway->>Gateway: 메시지 분석 및 분류 작업 진행
    Gateway->>Public: ticker 구독 요청 전송
    Gateway->>Private: myOrder 구독 요청 전송 (JWT 인증 대행)
    Public-->>Gateway: ticker 실시간 이벤트 발생
    Private-->>Gateway: myOrder 실시간 이벤트 발생
    Gateway-->>Client: 실시간 이벤트 최종 중계 (Relay)
```

- **지연 연결(Lazy Connect)**: 공개 채널만 사용하면 `ws_public`만 활성화되고, 비공개 채널 정보가 유입되는 시점에 비로소 `ws_private` 커넥션이 맺어집니다.
- **1대1 세션 매핑**: 클라이언트의 WebSocket 연결 1개당 내부 업스트림 커넥션은 최대 2개(공개 1개 + 비공개 1개)까지만 생성되므로 관리가 수월합니다.
- **표준 프로토콜 호환**: 업비트의 공식 WebSocket 개발 문서에 명시된 원본 메시지 형식을 일관되게 지원합니다.

---

## 오류 대응 응답 포맷

게이트웨이에서 특정 메시지를 원활하게 처리하지 못하는 경우 아래와 같은 JSON 에러 규격으로 응답을 돌려줍니다.

```json
{"error": "API 키가 설정되지 않았습니다. private 스트림에는 UPBIT_ACCESS_KEY가 필요합니다."}
```

| 예외 상황 | 에러 메시지 예시 |
|------|------------------|
| 비공개 구독 요청 시 API 키 누락 | `API 키가 설정되지 않았습니다. private 스트림에는 UPBIT_ACCESS_KEY가 필요합니다.` |
| 잘못되거나 존재하지 않는 `type` 지정 | `Unknown subscription type(s): ...` |
| 구독할 유형을 비워둔 채 전송 | `No subscription types in message` |
| 규격에 맞지 않는 잘못된 포맷의 데이터 전송 | `Expected a JSON array` |
| Bearer 토큰 인증 실패 | WebSocket 연결 자체 거부 (HTTP 4401 코드 반환) |

---

## 자주 묻는 질문(FAQ)

### 업비트 API 키를 클라이언트 앱에 직접 입력해야 하나요?

아닙니다. 비공개 스트림 연결에 필요한 JWT 인증 서명은 **게이트웨이 서버 컨테이너 내부의** `UPBIT_ACCESS_KEY`와 `UPBIT_SECRET_KEY`를 바탕으로 자동 처리됩니다. 클라이언트 측은 게이트웨이 접속 시 필요한 `UPBIT_BRIDGE_AUTH_TOKEN` 정보만 알고 있으면 됩니다.

### 공개 스트림만 이용하는 경우에도 API 키 설정이 필수인가요?

아닙니다. `ticker`, `trade`, `orderbook`, `candle.*`와 같은 시장 정보 채널은 API 키 등록 절차 없이 자유롭게 연결해서 활용하실 수 있습니다.

### 업비트 서버에 다이렉트로 연동하는 방식과 비교해 어떤 이점이 있나요?

- **인증 간소화**: 클라이언트가 골치 아픈 JWT 서명 알고리즘을 매번 구현할 필요가 없습니다.
- **통합 커넥션**: 공개 정보와 비공개 정보를 하나의 `ws://host/ws/` 주소로 간결하게 취합할 수 있습니다.
- **접근 통제**: 게이트웨이 레벨에서 `UPBIT_BRIDGE_AUTH_TOKEN`을 통해 악성 접속 시도를 사전에 차단합니다.

### 기존 REST MCP 도구와 함께 병행해 사용할 수 있나요?

네, 가능합니다. 단일 컨테이너 내부에서 `/sse` 경로(MCP Tool 호출 처리)와 `/ws/` 경로(실시간 메시지 중계)를 모두 동시 지원합니다. 일반적으로 개별 정보 확인은 MCP 도구를, 실시간 시세 변동 관찰은 WebSocket을 나누어 병용하는 방식이 권장됩니다.

---

## 참고 사이트 링크

- [업비트 공식 WebSocket API 개발 가이드](https://docs.upbit.com/reference/websocket)
- [Upbit SDK ↔ MCP 구현 현황](./upbit-sdk-mcp-coverage.md)
- [프로젝트 README](../README.md) — 컨테이너 실행 및 환경 변수 상세 안내

---

## 운영 시 유의사항

- 비공개(Private) 스트림을 사용하시는 경우 **실제 사용자 계정의 매매 내역 및 자산 현황**이 고스란히 유출될 수 있습니다. 운영망에 노출하실 때는 반드시 강력한 임의 문자열로 `UPBIT_BRIDGE_AUTH_TOKEN` 설정을 적용해 주십시오.
- 본 서버는 실거래가 유효한 API 키 정보를 보관할 수 있습니다. 거래소 API 설정 시 주문이나 출금 등의 권한은 가급적 최소화하여 발급받는 것을 권장합니다.
- WebSocket 연결은 장시간 유지되는 스트림 속성을 지닙니다. 네트워크 불안정으로 인한 접속 유실을 감안하여 클라이언트 측 애플리케이션 개발 시 적절한 자동 재연결(Auto-reconnect) 전략을 설계하는 것이 안전합니다.
