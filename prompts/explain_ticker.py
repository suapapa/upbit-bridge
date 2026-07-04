def explain_ticker(ticker_data: dict) -> str:
    """Create a prompt explaining ticker data"""
    market = ticker_data.get('market', '알 수 없음')
    trade_price = ticker_data.get('trade_price', 0)
    high_price = ticker_data.get('high_price', 0)
    low_price = ticker_data.get('low_price', 0)
    change_rate = ticker_data.get('signed_change_rate', 0) * 100
    
    return f"""당신은 암호화폐 시세 분석 전문가입니다. 다음은 특정 마켓의 현재 시세 데이터입니다.

<ticker_data>
마켓: {market}
현재가: {trade_price:,} KRW
고가(당일): {high_price:,} KRW
저가(당일): {low_price:,} KRW
전일 대비 변동률: {change_rate:.2f}%
</ticker_data>

이 데이터를 바탕으로 현재 시장 상황을 요약해 주세요. 다음 사항을 포함하여 분석하세요:
1. 가격 동향: 변동률과 고가/저가 대비 현재가의 위치를 고려하여 단기적인 추세(상승, 하락, 횡보)를 평가하세요.
2. 변동성 평가: 고가와 저가의 차이를 통해 해당 자산의 당일 변동성을 설명하세요.
3. 투자자 관점의 의미: 이러한 시세 움직임이 현재 투자자들에게 어떤 의미를 갖는지 간결하고 명확하게 설명해 주세요.

결과는 읽기 쉬운 마크다운 형식으로 제공하세요.
"""