import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. 頁面基本設定
st.set_page_config(page_title="st-stock-value 投資儀表板", layout="wide")

st.title("📊 個人投資組合視覺化儀表板")

# 2. 取得即時匯率函式
@st.cache_data(ttl=3600)
def get_usd_twd():
    try:
        data = yf.download("TWD=X", period="5d", progress=False)
        if not data.empty:
            return float(data['Close'].dropna().iloc[-1])
        return 32.0
    except:
        return 32.0

usd_rate = get_usd_twd()

# 3. 初始資料與介面佈局
default_data = [
    {"股票代碼": "2330.TW", "數量 (股)": 1000},
    {"股票代碼": "QQQ", "數量 (股)": 10},
    {"股票代碼": "2308.TW", "數量 (股)": 500},
]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 資產清單")
    df_input = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic", use_container_width=True)
    calc_btn = st.button("🚀 開始計算並更新數據", use_container_width=True)

# 4. 運算邏輯
if calc_btn:
    with st.spinner('正在分析市場數據 (含跨時區回溯)...'):
        try:
            valid_df = df_input.dropna(subset=["股票代碼"])
            tickers = [t.strip().upper() for t in valid_df["股票代碼"].tolist() if t.strip()]
            
            if not tickers:
                st.warning("請先輸入有效的股票代碼")
            else:
                raw_data = yf.download(tickers, period="5d", group_by='ticker', progress=False)
                
                results = []
                for _, row in valid_df.iterrows():
                    symbol = row["股票代碼"].strip().upper()
                    qty = row["數量 (股)"]
                    
                    try:
                        if len(tickers) == 1:
                            ticker_df = raw_data
                        else:
                            ticker_df = raw_data[symbol]
                        
                        price_series = ticker_df['Close'].dropna()
                        price = float(price_series.iloc[-1]) if not price_series.empty else 0.0
                    except:
                        price = 0.0

                    is_us_stock = ".TW" not in symbol
                    currency = "USD" if is_us_stock else "TWD"
                    market_val_twd = (price * qty * usd_rate) if is_us_stock else (price * qty)
                    
                    # 這裡加入了「數量」欄位
                    results.append({
                        "代碼": symbol,
                        "數量": qty, 
                        "幣別": currency,
                        "目前市價": round(price, 2),
                        "市值 (TWD)": round(market_val_twd, 0)
                    })

                df_res = pd.DataFrame(results)
                total_twd = float(df_res["市值 (TWD)"].sum())

                with col2:
                    st.subheader("📈 運算結果")
                    m1, m2 = st.columns(2)
                    m1.metric("總資產 (TWD)", f"${total_twd:,.0f}")
                    m2.metric("當前匯率 (USD/TWD)", f"{usd_rate:.2f}")

                    # 圓餅圖
                    fig = px.pie(df_res, values='市值 (TWD)', names='代碼', 
                                 title='資產配置比例 (台幣計價)', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 顯示含有「數量」的最終表格
                    st.dataframe(df_res, use_container_width=True)

        except Exception as e:
            st.error(f"分析失敗：{e}")

st.divider()
st.caption(f"數據來源：Yahoo Finance | 更新時間：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")