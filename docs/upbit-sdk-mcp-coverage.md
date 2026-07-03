# Upbit SDK ↔ MCP 기능 커버리지

[upbit-sdk-python](https://github.com/upbit-official/upbit-sdk-python) `v0.9.0` 기준으로, SDK가 제공하는 API와 이 MCP 서버에서 노출하는 기능을 대조한 체크리스트입니다.

**범례**

| 기호 | 의미 |
|------|------|
| ✅ | MCP로 제공 중 (`main.py`에 등록됨) |
| 🔶 | 구현은 되어 있으나 MCP에 미등록 |
| ❌ | 미구현 |
| ➖ | REST API 아님 (WebSocket 등) |

**MCP 노출 유형**

- **Tool** — 에이전트가 호출하는 함수
- **Resource** — 읽기 전용 데이터 URI
- **Prompt** — SDK API와 무관한 프롬프트 템플릿
- **Composite** — SDK 메서드 여러 개를 조합한 상위 기능

---

## 요약

| 구분 | SDK 메서드 수 | MCP 제공 | 구현만 됨 | 미구현 |
|------|--------------|----------|-----------|--------|
| REST API | 48 | 23 | 0 | 25 |
| WebSocket | 2 | 2 | 0 | 0 |

> SDK 메서드 48개 + WebSocket 2개 = 총 50개 항목 기준

---

## Accounts

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.accounts.list` | `GET /v1/accounts` | ✅ | `get_accounts` | 인증 필요 |

---

## TravelRule

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.travel_rule.list_vasps` | `GET /v1/travel_rule/vasps` | ❌ | — | |
| `client.travel_rule.verify_deposit_by_txid` | `POST /v1/travel_rule/deposit/txid` | ❌ | — | |
| `client.travel_rule.verify_deposit_by_uuid` | `POST /v1/travel_rule/deposit/uuid` | ❌ | — | |

---

## WalletStatus

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.wallet_status.list` | `GET /v1/status/wallet` | ✅ | `get_wallet_status` | |

---

## APIKeys

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.api_keys.list` | `GET /v1/api_keys` | ❌ | — | |

---

## Orders

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.orders.create` | `POST /v1/orders` | ✅ | `create_order` | 인증 필요 |
| `client.orders.retrieve` | `GET /v1/order` | ✅ | `get_order` | 인증 필요 |
| `client.orders.cancel` | `DELETE /v1/order` | ✅ | `cancel_order` | 인증 필요 |
| `client.orders.list_open` | `GET /v1/orders/open` | ✅ | `get_orders` | `state=wait` 시 사용 |
| `client.orders.list_closed` | `GET /v1/orders/closed` | ✅ | `get_orders` | `state=done\|cancel` 시 사용 |
| `client.orders.cancel_and_new` | `POST /v1/orders/cancel_and_new` | ❌ | — | |
| `client.orders.cancel_by_uuids` | `DELETE /v1/orders/uuids` | ❌ | — | |
| `client.orders.cancel_open` | `DELETE /v1/orders/open` | ✅ | `cancel_open_orders` | |
| `client.orders.list_by_uuids` | `GET /v1/orders/uuids` | ❌ | — | |
| `client.orders.retrieve_chance` | `GET /v1/orders/chance` | ✅ | `get_order_chance` | |
| `client.orders.test_create` | `POST /v1/orders/test` | ❌ | — | |

---

## Withdraws

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.withdraws.retrieve` | `GET /v1/withdraw` | ❌ | — | |
| `client.withdraws.list` | `GET /v1/withdraws` | ✅ | `get_deposits_withdrawals` | `transaction_type=withdraw` |
| `client.withdraws.cancel_withdrawal` | `DELETE /v1/withdraws/coin` | ❌ | — | |
| `client.withdraws.create_krw_withdrawal` | `POST /v1/withdraws/krw` | ✅ | `create_withdraw` | |
| `client.withdraws.create_withdrawal` | `POST /v1/withdraws/coin` | ✅ | `create_withdraw` | |
| `client.withdraws.list_coin_addresses` | `GET /v1/withdraws/coin_addresses` | ✅ | `list_withdraw_coin_addresses` | |
| `client.withdraws.retrieve_chance` | `GET /v1/withdraws/chance` | ❌ | — | |

---

## Deposits

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.deposits.retrieve` | `GET /v1/deposit` | ❌ | — | |
| `client.deposits.list` | `GET /v1/deposits` | ✅ | `get_deposits_withdrawals` | `transaction_type=deposit` |
| `client.deposits.create_coin_address` | `POST /v1/deposits/generate_coin_address` | ❌ | — | |
| `client.deposits.deposit_krw` | `POST /v1/deposits/krw` | ❌ | — | |
| `client.deposits.list_coin_addresses` | `GET /v1/deposits/coin_addresses` | ❌ | — | |
| `client.deposits.retrieve_chance` | `GET /v1/deposits/chance/coin` | ❌ | — | |
| `client.deposits.retrieve_coin_address` | `GET /v1/deposits/coin_address` | ✅ | `get_deposit_coin_address` | |

---

## TradingPairs

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.trading_pairs.list` | `GET /v1/market/all` | ✅ | `get_market_list` (Resource) | `market://list` |
| `client.trading_pairs.list` | `GET /v1/market/all` | ✅ | `get_market_summary` (Composite) | KRW 마켓 수 집계에 사용 |

---

## Tickers

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.tickers.list_by_trading_pairs` | `GET /v1/ticker` | ✅ | `get_ticker` | 단일/복수 마켓 |
| `client.tickers.list_by_quote_currencies` | `GET /v1/ticker/all` | ✅ | `get_market_summary` (Composite) | KRW 전체 티커 조회 |

---

## Orderbooks

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.orderbooks.list` | `GET /v1/orderbook` | ✅ | `get_orderbook` | |
| `client.orderbooks.list_instruments` | `GET /v1/orderbook/instruments` | ❌ | — | |

---

## Trades

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.trades.list` | `GET /v1/trades/ticks` | ✅ | `get_trades` | |

---

## Candles

| SDK 메서드 | HTTP | MCP | MCP 이름 | 비고 |
|------------|------|-----|----------|------|
| `client.candles.list_minutes` | `GET /v1/candles/minutes/{unit}` | ✅ | `get_candles` | minute1~240 지원 |
| `client.candles.list_days` | `GET /v1/candles/days` | ✅ | `get_candles` | |
| `client.candles.list_weeks` | `GET /v1/candles/weeks` | ✅ | `get_candles` | |
| `client.candles.list_months` | `GET /v1/candles/months` | ✅ | `get_candles` | |
| `client.candles.list_seconds` | `GET /v1/candles/seconds` | ✅ | `get_candles` | `interval=second` |
| `client.candles.list_years` | `GET /v1/candles/years` | ✅ | `get_candles` | `interval=year` |
| `client.candles.*` | — | ✅ | `technical_analysis` (Composite) | `list_minutes` / `list_days` 사용 |

---

## WebSocket

| SDK 영역 | MCP | 비고 |
|----------|-----|------|
| `WsPublic` | ✅ | `/ws/` 게이트웨이 (public 타입 자동 라우팅) |
| `WsPrivate` | ✅ | `/ws/` 게이트웨이 (private 타입 자동 라우팅, 컨테이너 API 키로 JWT 인증) |

---

## MCP 전용 기능 (SDK에 직접 대응 없음)

| 유형 | 이름 | 설명 |
|------|------|------|
| Tool (Composite) | `get_market_summary` | 주요 코인·거래량·등락률 상위 종목 요약 |
| Tool (Composite) | `technical_analysis` | 캔들 데이터 기반 기술적 지표 계산 |
| Prompt | `explain_ticker` | 티커 해석 프롬프트 |
| Prompt | `analyze_portfolio` | 포트폴리오 분석 프롬프트 |
| Prompt | `order_help` | 주문 도움말 프롬프트 |
| Prompt | `trading_strategy` | 매매 전략 프롬프트 |

---

## `main.py` 등록 현황

### 등록된 Tool (18개)

- [x] `get_ticker`
- [x] `get_orderbook`
- [x] `get_trades`
- [x] `get_candles`
- [x] `get_accounts`
- [x] `create_order`
- [x] `get_orders`
- [x] `get_order`
- [x] `get_order_chance`
- [x] `cancel_order`
- [x] `cancel_open_orders`
- [x] `get_market_summary`
- [x] `get_deposits_withdrawals`
- [x] `create_withdraw`
- [x] `get_deposit_coin_address`
- [x] `list_withdraw_coin_addresses`
- [x] `get_wallet_status`
- [x] `technical_analysis`

### 구현됐으나 미등록 Tool

없음 (모든 구현 도구가 `main.py`에 등록됨)

### 등록된 Resource (1개)

- [x] `get_market_list` — URI: `market://list`

### 등록된 Prompt (4개)

- [x] `explain_ticker`
- [x] `analyze_portfolio`
- [x] `order_help`
- [x] `trading_strategy`

---

## 추가 구현 후보

아래 SDK 기능은 아직 MCP에 없습니다.

1. `client.orders.test_create` — 테스트 주문
2. `client.orders.cancel_and_new` — 주문 취소 후 신규 주문
3. `client.orders.cancel_by_uuids` — UUID 목록 일괄 취소
4. `client.orders.list_by_uuids` — UUID 목록 주문 조회
5. `client.deposits.list_coin_addresses` — 입금 주소 목록 조회
6. TravelRule, APIKeys 관련 API

---

*마지막 업데이트: upbit-sdk `0.9.0`, MCP 서버 `main.py` 기준*
