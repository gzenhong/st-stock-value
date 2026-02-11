# 修正後的抓取數據邏輯
def get_latest_data(tickers):
    # 抓取最近 5 天的數據，確保一定能涵蓋到上一個交易日（即便中間有週末）
    data = yf.download(tickers, period="5d", group_by='ticker', progress=False)
    
    latest_prices = {}
    for ticker in tickers:
        try:
            # 取得該股票的收盤價序列
            if len(tickers) == 1:
                df = data
            else:
                df = data[ticker]
            
            # 移除 NaN 並取最後一個有效值
            valid_series = df['Close'].dropna()
            if not valid_series.empty:
                latest_prices[ticker] = valid_series.iloc[-1]
            else:
                latest_prices[ticker] = 0.0
        except:
            latest_prices[ticker] = 0.0
    return latest_prices