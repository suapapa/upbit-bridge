def analyze_portfolio(account_data: list[dict]) -> str:
    """
    사용자의 포트폴리오를 분석하는 프롬프트를 생성합니다.
    """
    portfolio_summary = ""
    total_krw = 0
    
    for asset in account_data:
        if asset['currency'] == 'KRW':
            total_krw = float(asset['balance'])
        else:
            avg_buy_price = float(asset.get('avg_buy_price', 0)) or 0
            asset_value = float(asset['balance']) * avg_buy_price
            portfolio_summary += f"- {asset['currency']}: {asset['balance']} 개 보유 (평균 매수가: {asset.get('avg_buy_price', '정보 없음')} KRW, 매수 금액: {asset_value:,.0f} 원)\n"
    
    return f"""당신은 전문적인 암호화폐 포트폴리오 분석가입니다. 아래 제공된 사용자의 업비트 포트폴리오 데이터를 바탕으로 심층적인 분석 및 투자 조언을 제공하세요.

<portfolio_data>
현재 KRW(원화) 잔액: {total_krw:,.0f} 원

보유 자산 내역:
{portfolio_summary}</portfolio_data>

다음 지침에 따라 분석을 수행하세요:
1. 포트폴리오 구성 분석: 각 자산의 비중을 평가하고 포트폴리오의 다각화 수준을 점검하세요.
2. 시장 상황 연계: 필요하다면 `get_ticker` 도구를 활용하여 각 보유 자산의 현재 시세를 확인하세요. 이를 통해 매수 시점 대비 현재 수익률 상황을 추정하고 분석에 포함하세요.
3. 리스크 평가: 현재 포트폴리오가 가진 잠재적 리스크(예: 특정 자산에 과도한 편중, 현금 비중 부족 등)를 식별하세요.
4. 실행 가능한 조언: 포트폴리오 리밸런싱, 추가 매수/매도 포지션 등 구체적이고 실질적인 투자 전략을 제안하세요.

결과는 명확한 마크다운 형식으로 가독성 있게 작성해주세요.
"""