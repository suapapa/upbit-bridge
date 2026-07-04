def order_help() -> str:
    """
    주문 생성에 대한 도움말 프롬프트를 생성합니다.
    """
    return """사용자에게 업비트 주문 생성 방법을 안내하거나 대신 주문을 수행해야 하는 상황입니다.
아래의 "업비트 주문 생성 가이드"를 참고하여, 사용자에게 주문 절차를 명확히 설명하거나, 제공된 예시를 바탕으로 알맞은 매개변수를 구성해 `create_order` 도구를 호출하세요.

<order_guide>
업비트 주문 생성 가이드

주문을 생성하기 위해 다음 정보가 필요합니다:
1. 마켓 코드 (예: KRW-BTC, KRW-ETH)
2. 주문 종류 (side)
   - bid: 매수
   - ask: 매도
3. 주문 타입 (ord_type)
   - limit: 지정가 주문 (volume과 price 모두 필요)
   - price: 시장가 매수 (price만 필요, 주문 총액 - KRW 기준)
   - market: 시장가 매도 (volume만 필요, 주문 수량 - 코인 기준)
4. volume: 주문량 (지정가 및 시장가 매도시 필수)
5. price: 주문 가격 (지정가 및 시장가 매수시 필수)

주문 예시:
1. 비트코인 100,000원어치 시장가 매수:
   create_order(market="KRW-BTC", side="bid", ord_type="price", price="100000")
2. 이더리움 0.1개 시장가 매도:
   create_order(market="KRW-ETH", side="ask", ord_type="market", volume="0.1")
3. 리플 500개 1,000원에 지정가 매수:
   create_order(market="KRW-XRP", side="bid", ord_type="limit", volume="500", price="1000")
</order_guide>

행동 지침:
- 사용자가 주문을 요청하면, 필요한 파라미터(마켓, 종류, 타입, 수량/가격)가 모두 갖춰졌는지 먼저 확인하세요.
- 정보가 부족한 경우 사용자에게 어떤 값이 더 필요한지 친절하게 물어보세요.
- 실제 주문 도구를 호출하기 전, 안전을 위해 `get_accounts` 도구를 사용하여 보유 잔고나 코인이 충분한지 확인하는 것을 권장합니다.
- 주문이 실행된 후에는 `get_orders` 도구로 결과를 확인하거나, 취소가 필요할 경우 `cancel_order` 도구를 사용하세요.
"""