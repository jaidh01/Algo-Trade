import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from backend import fetch_candle_data, live_data, start_background
import time

st.set_page_config(layout="wide")

# 🔥 Start background (WebSocket)
start_background()

# 🔽 Sidebar
option = st.sidebar.selectbox(
    "Select Index",
    ["NIFTY", "SENSEX"]
)

st.title(f"📊 {option} Chart")

# ✅ FETCH HISTORICAL DATA
if option == "NIFTY":
    data = fetch_candle_data("NIFTY", "99926000", "NSE")

elif option == "SENSEX":
    data = fetch_candle_data("SENSEX", "99919000", "BSE")

# ✅ 🔥 ADD LIVE PRICE HERE
# if live_data.get(option):
#     ltp = live_data[option].get("last_traded_price")
#     st.metric(f"{option} Live Price", ltp)

# ✅ CHART BELOW
if data:
    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume"
    ])

    df["time"] = pd.to_datetime(df["time"])
    if live_data.get(option):
        ltp = live_data[option].get("last_traded_price")

        if ltp:
            # Update last candle
            df.iloc[-1, df.columns.get_loc("close")] = ltp

            # Adjust high/low
            df.iloc[-1, df.columns.get_loc("high")] = max(df.iloc[-1]["high"], ltp)
            df.iloc[-1, df.columns.get_loc("low")] = min(df.iloc[-1]["low"], ltp)

    fig = go.Figure()

    color = "green" if df["close"].iloc[-1] >= df["open"].iloc[0] else "red"

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["close"],
        mode="lines",
        line=dict(color=color, width=2),
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_range=[
            df["close"].min() * 0.995,
            df["close"].max() * 1.005
        ]
    )

    st.plotly_chart(fig, width='stretch')

else:
    st.warning("No data available")

time.sleep(2)
st.rerun()












# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# from backend import fetch_candle_data

# st.set_page_config(layout="wide")

# st.title("📊 Bank Nifty Chart (Real Data)")

# data = fetch_candle_data()

# if data:

#     df = pd.DataFrame(data, columns=[
#         "time", "open", "high", "low", "close", "volume"
#     ])

#     df["time"] = pd.to_datetime(df["time"])

#     # 🔥 Price Line Chart
#     fig = go.Figure()

#     fig.add_trace(go.Scatter(
#         x=df["time"],
#         y=df["close"],
#         mode="lines",
#         name="Price",
#         line=dict(width=2)
#     ))

#     fig.update_layout(
#         title="Bank Nifty Intraday",
#         xaxis_title="Time",
#         yaxis_title="Price",
#         height=500
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     # 🔥 Volume Chart
#     st.subheader("Volume")

#     fig2 = go.Figure()

#     fig2.add_trace(go.Bar(
#         x=df["time"],
#         y=df["volume"],
#         name="Volume"
#     ))

#     fig2.update_layout(height=200)

#     st.plotly_chart(fig2, use_container_width=True)

# else:
#     st.warning("No data available")