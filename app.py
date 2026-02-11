import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="股票市值計算器", layout="centered")

st.title("📈 股票市值實時計算")

# 1. 初始資料設定 (模擬你的表格結構)
default_data = [
    {"股票代碼": "2308.TW", "數量 (股)": 1000},
    {"股票代碼": "2337.TW", "數量 (股)": 2000},
    {"股票代碼": "2344.TW", "數量 (股)": 500},
    {"股票代碼": "1605.TW", "數量 (股)": 1500},
]

# 2. 提供可編輯的表格介面
st.subheader("請輸入股票代碼與持有股數")
df_input = st.data_editor(
    pd.DataFrame(default_data),
    num_rows="dynamic",
    use_container_width=True,
    key="stock_editor"
)

if st.button("更新市價並計算"):
    with st.spinner('正在從 Yahoo Finance 抓取最新數據...'):
        try:
            # 3. 抓取市價邏輯
            tickers = df_input["股票代碼"].tolist()
            # 一次性抓取多支股票的最新資訊
            data = yf.download(tickers, period="1d")['Close']
            
            # 處理單支與多支股票回傳格式不同的問題
            if len(tickers) == 1:
                latest_prices = {tickers[0]: data.iloc[-1]}
            else:
                latest_prices = data.iloc[-1].to_dict()

            # 4. 計算市價與市值
            df_input["目前市價"] = df_input["股票代碼"].map(latest_prices).round(2)
            df_input["市值"] = (df_input["目前市價"] * df_input["數量 (股)"]).round(0)

            # 5. 輸出結果表格
            st.divider()
            st.dataframe(df_input, use_container_width=True)

            # 6. 計算總資產
            total_value = df_input["市值"].sum()
            st.metric(label="總資產 (TWD)", value=f"{total_value:,.0f}")
            
        except Exception as e:
            st.error(f"抓取資料時發生錯誤: {e}")
            st.info("請檢查股票代碼格式是否正確（例如台股需加 .TW）")

st.caption("註：市價抓取自 Yahoo Finance，可能會有延遲。")