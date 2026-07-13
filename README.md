# Upbit Bridge

Upbit Bridge는 Model Context Protocol(MCP), REST API, WebSockets를 기반으로 업비트(Upbit) 가상자산 거래소 OpenAPI를 편리하게 이어주는 통합 게이트웨이입니다. 시세 조회(현재가, 호가, 체결 내역, 차트 데이터), 계좌 정보 조회, 주문 작성 및 취소, 입출금 관리, 기술적 지표 분석 등 업비트 거래소 서비스와 연동할 수 있는 다양한 도구를 제공합니다.

## 주요 기능

- 시장 데이터 조회 (현재가, 호가, 체결 내역, 캔들 데이터)
- 계좌 정보 확인 (잔고, 주문 내역)
- 주문 생성 및 취소
- 입출금 기능 지원
- 기술적 분석 도구 제공
- REST API v1 (`/api/v1/`) — 잔고·주문용 스크립트/봇 엔드포인트
- WebSocket 게이트웨이 (`/ws/`) — public/private 실시간 스트림

## 시작하기 전에

서비스를 이용하려면 먼저 업비트 API 키가 필요합니다.

1. 계정이 없다면 [업비트](https://upbit.com)에 회원가입을 해 주세요.
2. [업비트 개발자 센터](https://upbit.com/service_center/open_api_guide)에 접속합니다.
3. Open API Key를 새로 발급받습니다.
4. 쓰임새에 맞게 적절한 권한(조회, 주문, 입출금 등)을 설정해 주세요.
5. 발급받은 API 키는 `.env` 파일에 안전하게 저장합니다. (사용법 섹션 참고)

> 시세나 호가, 캔들 같은 공개 API만 사용하신다면 API 키가 없어도 작동합니다.

### 주의사항

- 본 서버는 실제 거래를 실행할 수 있으므로 다룰 때 각별히 주의해 주시기 바랍니다.
- API 키는 안전하게 보관하시고, 실수로 공개 저장소에 업로드하지 않도록 유의해 주세요.
- SSE 엔드포인트를 외부에 노출할 때는 `UPBIT_BRIDGE_AUTH_TOKEN`을 설정해 안전하게 차단막을 마련해 두는 것이 좋습니다.

## 사용법

이 MCP 서버는 Docker 컨테이너를 바탕으로 SSE transport(`http://0.0.0.0:8000/sse`)를 거쳐 실행할 수 있습니다.

### 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.

```env
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
UPBIT_BRIDGE_AUTH_TOKEN=your_bearer_token_here
```

| 변수 | 필수 여부 | 설명 |
|------|------|------|
| `UPBIT_ACCESS_KEY` | 선택 | 업비트 Access Key (계정·주문·입출금 API 용도) |
| `UPBIT_SECRET_KEY` | 선택 | 업비트 Secret Key |
| `UPBIT_BRIDGE_AUTH_TOKEN` | 권장 | SSE/WebSocket/REST 엔드포인트 Bearer 인증 토큰. 설정하지 않으면 `/sse`, `/messages`, `/ws/`, `/api/v1` 경로가 보호되지 않습니다. |

### 2. Docker 이미지 실행

**GHCR에서 가져오기 (권장)**

```bash
docker pull ghcr.io/suapapa/upbit-bridge:latest

docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-bridge:latest
```

**로컬에서 빌드하기**

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

컨테이너가 제대로 실행되었는지 확인해 봅니다.

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. MCP 클라이언트 연결

Claude Desktop, Cursor 등 MCP 클라이언트에서 Upbit Bridge를 연동하고 활용하는 구체적인 방법은 [MCP 사용 가이드](docs/mcp_usage.md)를 참고해 주세요. (SSE 및 stdio 전송 방식 모두 지원)

### 4. REST API v1 (`/api/v1/`)

잔고 조회와 주문 CRUD를 `curl`·스크립트에서 바로 호출할 수 있습니다. OpenAPI UI는 `/docs/api`입니다.

```bash
curl -H "Authorization: Bearer $UPBIT_BRIDGE_AUTH_TOKEN" \
  http://localhost:8000/api/v1/accounts
```

상세 엔드포인트·예시는 [REST API 사용 가이드](docs/api_usage.md)를 참고해 주세요.

### 5. WebSocket 게이트웨이 (`/ws/`)

단일 `/ws/` 엔드포인트 하나로 업비트 public 시세(`ticker`, `trade`, `orderbook`, `candle.*`)와 private 계정 스트림(`myOrder`, `myAsset`)을 모두 받아볼 수 있습니다. 상세한 연결 방법과 구독 예시, 혼합 구독 및 에러 처리 방안은 [WebSocket 게이트웨이 사용 가이드](docs/ws_usage.md)에서 확인하실 수 있습니다.

## 문서 안내

| 문서 | 설명 |
|------|------|
| [MCP 사용 가이드](docs/mcp_usage.md) | Claude Desktop 및 Cursor 연결 설정 (SSE, stdio) |
| [MCP 도구 소개](docs/mcp-tools.md) | Tool, Resource, Prompt 목록 및 설명 |
| [Upbit SDK ↔ MCP 구현 현황](docs/upbit-sdk-mcp-coverage.md) | SDK 대비 MCP 커버리지 체크리스트 |
| [REST API 사용 가이드](docs/api_usage.md) | `/api/v1/` 잔고·주문, OpenAPI (`/docs/api`) |
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

## 라이선스

MIT
