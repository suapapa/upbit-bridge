# MCP(Model Context Protocol) 사용 가이드

Upbit Bridge는 Claude Desktop, Cursor 등 다양한 LLM 클라이언트에서 업비트의 시세 조회, 계좌 정보 확인, 주문 처리 등을 손쉽게 수행할 수 있도록 **MCP(Model Context Protocol)** 서버 기능을 지원합니다.

Upbit Bridge는 두 가지 전송 방식(SSE, stdio)을 모두 제공합니다. 사용 환경에 알맞은 방식을 선택하여 설정해 보세요.

---

## 1. 전송 방식 선택

### 💡 SSE(Server-Sent Events) 방식 (권장)
* **특징**: Upbit Bridge를 Docker 컨테이너 등으로 상시 구동(포트 `8000`)해 두고, 클라이언트가 HTTP/SSE 엔드포인트로 접속하는 방식입니다.
* **장점**: 하나의 서버 프로세스에서 **실시간 WebSocket 게이트웨이(`/ws/`)**와 **MCP 서비스**를 동시에 제공할 수 있어 서버 자원을 효율적으로 쓰고 관리하기가 편합니다.
* **보안**: `UPBIT_BRIDGE_AUTH_TOKEN` 환경 변수를 설정하여 승인되지 않은 외부 클라이언트의 임의 접근을 안전하게 차단할 수 있습니다.

### 🔌 stdio 방식
* **특징**: 클라이언트가 필요할 때 Upbit Bridge 프로세스(`python main.py`)를 직접 실행하여 표준 입출력(stdio)으로 통신하는 방식입니다.
* **장점**: Docker와 같은 별도의 백그라운드 서버를 항상 띄워둘 필요 없이, 클라이언트를 실행하는 순간 자동으로 구동되므로 훨씬 간편합니다.

---

## 2. SSE 방식으로 연결하기 (Docker 환경 권장)

### 1단계. 서버 실행
먼저 Docker를 사용해 Upbit Bridge 서버를 켭니다. 보안을 위해 `UPBIT_BRIDGE_AUTH_TOKEN`을 설정해 두는 것을 권장합니다.

```bash
docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-bridge:latest
```

서버가 정상적으로 구동되면 MCP 클라이언트가 `http://localhost:8000/sse` 엔드포인트로 접속할 수 있습니다.

### 2단계. 클라이언트 설정

#### 1) Claude Desktop 설정
설정 파일([설정 파일 위치 안내](#부록-claude-desktop-설정-파일-위치))을 열어 아래 내용을 추가합니다.

* **인증 토큰(`UPBIT_BRIDGE_AUTH_TOKEN`)을 설정한 경우**:
  ```json
  {
    "mcpServers": {
      "upbit-bridge": {
        "url": "http://localhost:8000/sse",
        "headers": {
          "Authorization": "Bearer your_sse_bearer_token_here"
        }
      }
    }
  }
  ```
* **인증 토큰을 설정하지 않은 경우** (`headers` 생략 가능):
  ```json
  {
    "mcpServers": {
      "upbit-bridge": {
        "url": "http://localhost:8000/sse"
      }
    }
  }
  ```

#### 2) Cursor 설정
1. **Cursor Settings** > **Features** > **MCP** 메뉴로 이동합니다.
2. `+ Add New MCP Server` 버튼을 클릭합니다.
3. 아래 정보를 입력하고 저장합니다.
   * **Name**: `upbit-bridge`
   * **Type**: `SSE`
   * **URL**: `http://localhost:8000/sse`
   > [!NOTE]
   > Cursor에서 헤더(`Authorization`) 인증이 필요한 경우, URL 뒤에 쿼리 스트링으로 토큰을 추가해 연동할 수 있습니다. 예: `http://localhost:8000/sse?token=your_sse_bearer_token_here` (서버에서 쿼리 파라미터 인증을 지원하는지 먼저 확인해 주시기 바랍니다)

---

## 3. stdio 방식으로 연결하기 (로컬 직접 구동)

Docker를 쓰지 않고 로컬에 구축된 Python 환경에서 클라이언트가 프로세스를 직접 실행하도록 설정하는 방법입니다.

### 1단계. 가상환경 및 의존성 패키지 준비
로컬 프로젝트 폴더에 가상환경이 구축되어 있고 관련 라이브러리가 설치되어 있어야 합니다.

```bash
cd /path/to/upbit-bridge
uv sync  # 또는 pip install -r requirements.txt
```

### 2단계. 클라이언트 설정

#### 1) Claude Desktop 설정
설정 파일에 아래와 같이 등록합니다. 로컬에서 실행하는 것이므로 API 키를 환경변수로 직접 주입해 줍니다.

```json
{
  "mcpServers": {
    "upbit-bridge-local": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/suapapa/ai/mcp/upbit-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "UPBIT_ACCESS_KEY": "your_access_key_here",
        "UPBIT_SECRET_KEY": "your_secret_key_here"
      }
    }
  }
}
```
*(참고: `uv` 대신 일반 `python` 가상환경의 바이너리 경로를 직접 지정해 실행할 수도 있습니다.)*

#### 2) Cursor 설정
1. **Cursor Settings** > **Features** > **MCP** 메뉴로 이동합니다.
2. `+ Add New MCP Server` 버튼을 클릭합니다.
3. 아래 정보를 입력하고 저장합니다.
   * **Name**: `upbit-bridge-local`
   * **Type**: `command`
   * **Command**: `uv --directory /Users/suapapa/ai/mcp/upbit-mcp-server run main.py`

---

## 부록. Claude Desktop 설정 파일 위치

사용하는 운영체제(OS)에 따라 설정 파일(`config.json`)의 경로가 다릅니다.

* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

---

## 🔗 함께 보기
* [MCP 도구 목록 및 설명 문서](./mcp-tools.md)
* [WebSocket 게이트웨이 사용 가이드](./ws_usage.md)
