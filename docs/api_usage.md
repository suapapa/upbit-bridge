# REST API v1 사용 가이드

Upbit Bridge의 `/api/v1/` 엔드포인트는 잔고·주문·공개 시세처럼 **스크립트·크론·봇**에 맞는 요청-응답 REST API입니다. MCP(`/sse`)나 WebSocket(`/ws/`)과 같은 프로세스에서 함께 제공됩니다.

OpenAPI(Swagger UI): [http://localhost:8000/docs/api](http://localhost:8000/docs/api)  
스펙 JSON: [http://localhost:8000/docs/api.json](http://localhost:8000/docs/api.json)

## 인증

| 계층 | 설명 |
|------|------|
| Bridge Bearer | `UPBIT_BRIDGE_AUTH_TOKEN`이 설정된 경우 `Authorization: Bearer <token>` 필요 (`/docs/api`는 예외로 공개) |
| Upbit API 키 | 컨테이너 `.env`의 `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY` — 클라이언트에 노출하지 않음 |

```bash
export TOKEN=your_bearer_token_here
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/accounts
```

키가 없으면 인증 API는 `503`과 함께 오류를 반환합니다.

## 엔드포인트

### 계정

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/api/v1/accounts` | 전체 잔고 |
| `GET` | `/api/v1/accounts/{currency}` | 단일 통화 잔고 (예: `KRW`, `BTC`) |

### 주문

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/api/v1/orders` | 주문 생성 |
| `GET` | `/api/v1/orders` | 주문 목록 (`state=wait\|done\|cancel`) |
| `DELETE` | `/api/v1/orders` | 미체결 일괄 취소 |
| `GET` | `/api/v1/orders/chance?market=` | 주문 가능 정보 |
| `GET` | `/api/v1/orders/{uuid}` | 주문 상세 |
| `DELETE` | `/api/v1/orders/{uuid}` | 단건 취소 |

### 시세·마켓 (공개 데이터, Upbit 키 불필요)

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/api/v1/markets` | 거래 가능 마켓 목록 (`?details=true`) |
| `GET` | `/api/v1/ticker?markets=` | 현재가 (복수 콤마 구분) |
| `GET` | `/api/v1/orderbook?markets=` | 호가 (`?count=` 깊이) |
| `GET` | `/api/v1/trades?market=` | 최근 체결 |
| `GET` | `/api/v1/candles?market=&interval=` | 캔들 (`format=json\|csv`) |

`UPBIT_BRIDGE_AUTH_TOKEN`이 설정된 경우 시세 API도 Bearer가 필요합니다. Upbit API 키는 계정·주문에만 필요합니다.

## 예시

### 잔고 조회

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/accounts | jq .

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/accounts/KRW | jq .
```

### 지정가 매수

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "market": "KRW-BTC",
    "side": "bid",
    "ord_type": "limit",
    "volume": "0.0001",
    "price": "100000000"
  }' \
  http://localhost:8000/api/v1/orders | jq .
```

- `ord_type=limit` — `volume` + `price` 필수
- `ord_type=price` — 시장가 매수, `price`(주문 총액) 필수
- `ord_type=market` — 시장가 매도, `volume` 필수

### 미체결 조회·취소

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orders?state=wait&market=KRW-BTC" | jq .

curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orders/{uuid}" | jq .

curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orders?cancel_side=all&count=20" | jq .
```

### 시세 조회

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/ticker?markets=KRW-BTC,KRW-ETH" | jq .

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/orderbook?market=KRW-BTC&count=5" | jq .

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/candles?market=KRW-BTC&interval=minute60&count=24" | jq .

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/candles?market=KRW-BTC&interval=day&count=30&format=csv"
```

## 오류 형식

```json
{
  "error": {
    "message": "유효하지 않은 마켓 코드입니다.",
    "status": 400
  }
}
```

## MCP / WebSocket과의 역할

| 채널 | 적합한 일 |
|------|-----------|
| REST `/api/v1/` | 잔고, 주문 CRUD, 시세 스냅샷, 스크립트·봇 |
| MCP `/sse` | 에이전트 도구·분석·프롬프트 |
| WS `/ws/` | 실시간 ticker / myOrder / myAsset |

## 관련 문서

- [MCP 사용 가이드](./mcp_usage.md)
- [WebSocket 게이트웨이 사용 가이드](./ws_usage.md)
