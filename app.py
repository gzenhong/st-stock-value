import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="st-stock-value 投資儀表板", layout="wide")

st.title("📊 個人投資組合視覺化儀表板")

# 1. 取得即時匯率 (美金對台幣)
@st.cache_data(ttl=3600)
def get_usd_twd():
    try:
        usdtwd = yf.Ticker("TWD=X").history(period="1d")['Close'].iloc[-1]
        return usdtwd
    except:
        return 32.0  # 萬一抓不到匯率時的保底值

usd_rate = get_usd_twd()

# 2. 初始資料設定
default_data = [
    {"股票代碼": "2330.TW", "數量 (股)": 1000},
    {"股票代碼": "QQQ", "數量 (股)": 10},
    {"股票代碼": "2308.TW", "數量 (股)": 500},
]

# 介面佈局：左側輸入，右側顯示
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 資產清單")
    df_input = st.data_editor(
        pd.DataFrame(default_data),
        num_rows="dynamic",
        use_container_width=True
    )
    
    calc_btn = st.button("🚀 開始計算並更新數據", use_container_width=True)

if calc_btn:
    with st.spinner('正在分析市場數據...'):
        try:
            tickers = df_input["股票代碼"].tolist()
            # 抓取所有股票數據
            data = yf.download(tickers, period="1d")['Close']
            
            prices = {}
            if len(tickers) == 1:
                prices[tickers[0]] = data.iloc[-1]
            else:
                prices = data.iloc[-1].to_dict()

            # 計算邏輯
            results = []
            for _, row in df_input.iterrows():
                symbol = row["股票代碼"]
                qty = row["數量 (股)"]
                price = prices.get(symbol, 0)
                
                # 自動判斷幣別 (簡單判斷：有 .TW 為台幣，其餘視為美金)
                is_us_stock = ".TW" not in symbol.upper()
                currency = "USD" if is_us_stock else "TWD"
                
                # 計算單筆市值 (原幣)
                market_val_orig = price * qty
                # 換算為台幣
                market_val_twd = market_val_orig * usd_rate if is_us_stock else market_val_orig
                
                results.append({
                    "代碼": symbol,
                    "幣別": currency,
                    "目前市價": round(price, 2),
                    "市值 (TWD)": round(market_val_twd, 0)
                })

            df_res = pd.DataFrame(results)
            total_twd = df_res["市值 (TWD)"].sum()

            with col2:
                # 顯示總資產卡片
                st.subheader("📈 運算結果")
                m1, m2 = st.columns(2)
                m1.metric("總資產 (TWD)", f"${total_twd:,.0f}")
                m2.metric("當前匯率 (USD/TWD)", f"{usd_rate:.2f}")

                # 圓餅圖
                fig = px.pie(df_res, values='市值 (TWD)', names='代碼', 
                             title='資產配置比例', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)

                # 詳細表格
                st.dataframe(df_res, use_container_width=True)

        except Exception as e:
            st.error(f"分析失敗：{e}")

st.divider()
st.caption(f"數據來源：Yahoo Finance | 更新時間：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")