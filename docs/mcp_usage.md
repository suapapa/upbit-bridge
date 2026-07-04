# MCP (Model Context Protocol) 사용 가이드

Upbit Bridge는 Claude Desktop, Cursor 등 다양한 LLM 클라이언트가 업비트의 시세 조회, 계정 정보 조회, 주문 처리 등을 수행할 수 있도록 **MCP(Model Context Protocol)** 서버 기능을 제공합니다.

Upbit Bridge는 두 가지 전송 방식(SSE, stdio)을 모두 지원합니다. 사용 중인 환경에 맞추어 설정해 보세요.

---

## 1. 전송 방식(Transport) 선택

### 💡 SSE (Server-Sent Events) 방식 (권장)
* **특징**: Upbit Bridge를 Docker 컨테이너 등으로 상시 가동(포트 `8000`)하고, 클라이언트가 HTTP/SSE 엔드포인트를 통해 접속합니다.
* **장점**: 동일한 서버에서 **실시간 WebSocket 게이트웨이(`/ws/`)**와 **MCP 서비스**를 함께 제공할 수 있어 리소스를 효율적으로 쓰고 통합 관리가 쉽습니다.
* **보안**: `UPBIT_MCP_SSE_TOKEN` 환경 변수를 설정하여 허가되지 않은 클라이언트의 접근을 막을 수 있습니다.

### 🔌 stdio 방식
* **특징**: 클라이언트가 필요할 때 Upbit Bridge 프로세스(`python main.py`)를 직접 실행하여 표준 입출력(stdio)으로 통신합니다.
* **장점**: 별도의 백그라운드 서버 프로세스(Docker 등)를 띄워두지 않아도 클라이언트 실행 시점에 자동으로 구동되므로 가볍습니다.

---

## 2. SSE 방식으로 연결하기 (Docker 환경 권장)

### step 1. 서버 구동
먼저 Docker를 사용해 Upbit Bridge 서버를 구동합니다. 보안을 위해 `UPBIT_MCP_SSE_TOKEN`을 설정하는 것을 권장합니다.

```bash
docker run -d \
  --name upbit-bridge \
  --env-file .env \
  -p 8000:8000 \
  ghcr.io/suapapa/upbit-bridge:latest
```

정상적으로 구동되면 `http://localhost:8000/sse` 엔드포인트를 통해 MCP 클라이언트가 접속할 수 있습니다.

### step 2. 클라이언트 설정

#### 1) Claude Desktop 설정
설정 파일([설정 파일 위치 안내](#claude-desktop-설정-파일-위치))을 열어 아래와 같이 추가합니다.

* **인증 토큰(`UPBIT_MCP_SSE_TOKEN`)을 설정한 경우**:
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
3. 아래 정보를 입력하고 저장합니다:
   * **Name**: `upbit-bridge`
   * **Type**: `SSE`
   * **URL**: `http://localhost:8000/sse`
   > [!NOTE]
   > Cursor에서 헤더(`Authorization`) 인증이 필요한 경우, URL 뒤에 쿼리 스트링으로 토큰을 추가해 연동할 수도 있습니다: `http://localhost:8000/sse?token=your_sse_bearer_token_here` (서버가 쿼리 파라미터 인증도 지원하는지 확인 필요)

---

## 3. stdio 방식으로 연결하기 (로컬 직접 구동)

Docker 없이 로컬 환경에 설치된 Python 환경에서 클라이언트가 프로세스를 직접 실행하도록 설정하는 방법입니다.

### step 1. 가상환경 및 의존성 준비
로컬 프로젝트 폴더에 가상환경이 구축되어 있고 라이브러리가 설치되어 있어야 합니다.

```bash
cd /path/to/upbit-bridge
uv sync  # 또는 pip install -r requirements.txt
```

### step 2. 클라이언트 설정

#### 1) Claude Desktop 설정
설정 파일에 아래와 같이 추가합니다. 로컬 실행이므로 API 키를 환경변수로 직접 주입해 줍니다.

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
*(참고: `uv` 대신 일반 `python` 가상환경 바이너리 경로를 직접 지정해 실행할 수도 있습니다.)*

#### 2) Cursor 설정
1. **Cursor Settings** > **Features** > **MCP** 메뉴로 이동합니다.
2. `+ Add New MCP Server` 버튼을 클릭합니다.
3. 아래 정보를 입력하고 저장합니다:
   * **Name**: `upbit-bridge-local`
   * **Type**: `command`
   * **Command**: `uv --directory /Users/suapapa/ai/mcp/upbit-mcp-server run main.py`

---

## 附录. Claude Desktop 설정 파일 위치

사용 중인 OS에 따라 설정 파일(`config.json`)의 위치가 다릅니다.

* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

---

## 🔗 함께 보기
* [MCP 도구 목록 및 설명 문서](./mcp-tools.md)
* [WebSocket 게이트웨이 사용 가이드](./ws_usage.md)
