import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from ta.momentum import RSIIndicator

st.set_page_config(
    page_title="Stock Analyzer V2",
    layout="wide"
)

# =========================================
# HELPERS
# =========================================

def clean(x):

    try:

        if x is None:
            return None

        if np.isnan(x):
            return None

        return float(x)

    except:

        return None


def pct(x):

    if x is None:
        return None

    return x * 100


def show(x, percent=False):

    if x is None:
        return "N/A"

    if percent:
        return f"{x:.2f}%"

    return f"{x:.2f}"


# =========================================
# DCF
# =========================================

def dcf_value(
    fcf,
    shares,
    growth,
    discount,
    terminal,
    years
):

    if (
        not fcf
        or not shares
    ):
        return None

    growth /= 100
    discount /= 100
    terminal /= 100

    if discount <= terminal:
        return None

    pv = 0

    current_fcf = fcf

    for year in range(
        1,
        years + 1
    ):

        current_fcf *= (
            1 + growth
        )

        pv += (
            current_fcf
            /
            ((1 + discount) ** year)
        )

    terminal_fcf = (
        current_fcf
        * (1 + terminal)
    )

    terminal_value = (
        terminal_fcf
        /
        (discount - terminal)
    )

    terminal_pv = (
        terminal_value
        /
        ((1 + discount) ** years)
    )

    total = (
        pv + terminal_pv
    )

    return (
        total / shares
    )


# =========================================
# SIDEBAR
# =========================================

st.sidebar.header(
    "DCF Settings"
)

growth = st.sidebar.slider(
    "Growth %",
    0.0,
    20.0,
    8.0
)

discount = st.sidebar.slider(
    "Discount %",
    5.0,
    20.0,
    10.0
)

terminal = st.sidebar.slider(
    "Terminal %",
    0.0,
    5.0,
    2.5
)

years = st.sidebar.slider(
    "Years",
    5,
    15,
    10
)

# =========================================
# INPUT
# =========================================

st.title(
    "📈 Stock Analyzer V2"
)

ticker_symbol = st.text_input(
    "Ticker",
    "MSFT"
).upper()

if not ticker_symbol:

    st.stop()

try:

    ticker = yf.Ticker(
        ticker_symbol
    )

    info = ticker.info

    hist = ticker.history(
        period="2y",
        auto_adjust=True
    )

    if hist.empty:

        st.error(
            "No market data."
        )

        st.stop()

    # =====================================
    # TECHNICAL
    # =====================================

    hist["RSI"] = (
        RSIIndicator(
            hist["Close"]
        ).rsi()
    )

    hist["SMA50"] = (
        hist["Close"]
        .rolling(50)
        .mean()
    )

    hist["SMA200"] = (
        hist["Close"]
        .rolling(200)
        .mean()
    )

    current_price = (
        hist["Close"]
        .iloc[-1]
    )

    current_rsi = (
        hist["RSI"]
        .dropna()
        .iloc[-1]
    )

    sma50 = (
        hist["SMA50"]
        .dropna()
        .iloc[-1]
    )

    sma200 = (
        hist["SMA200"]
        .dropna()
        .iloc[-1]
    )

    # =====================================
    # FUNDAMENTALS
    # =====================================

    pe = clean(
        info.get("trailingPE")
    )
        
    forward_pe = clean(
        info.get("forwardPE")
    )

    peg = clean(
        info.get("pegRatio")
    )

    ev_ebitda = clean(
        info.get(
            "enterpriseToEbitda"
        )
    )

    roe = pct(
        clean(
            info.get(
                "returnOnEquity"
            )
        )
    )

    revenue_growth = pct(
        clean(
            info.get(
                "revenueGrowth"
            )
        )
    )

    earnings_growth = pct(
        clean(
            info.get(
                "earningsGrowth"
            )
        )
    )

    debt = clean(
        info.get(
            "debtToEquity"
        )
    )

    market_cap = clean(
        info.get(
            "marketCap"
        )
    )

    fcf = clean(
        info.get(
            "freeCashflow"
        )
    )

    shares = clean(
        info.get(
            "sharesOutstanding"
        )
    )

    fcf_yield = None

    if (
        fcf
        and market_cap
    ):

        fcf_yield = (
            fcf /
            market_cap
        ) * 100

    # =====================================
    # DCF
    # =====================================

    fair_value = dcf_value(
        fcf,
        shares,
        growth,
        discount,
        terminal,
        years
    )

    mos = None

    if fair_value:

        mos = (
            (
                fair_value
                - current_price
            )
            /
            fair_value
        ) * 100

    # =====================================
    # BUFFETT
    # =====================================

    buffett = 0

    if roe and roe > 15:
        buffett += 1

    if debt and debt < 50:
        buffett += 1

    if revenue_growth and revenue_growth > 0:
        buffett += 1

    if fcf_yield and fcf_yield > 5:
        buffett += 1

    # =====================================
    # LYNCH
    # =====================================

    lynch = 0

    if peg and peg < 1.5:
        lynch += 1

    if earnings_growth and earnings_growth > 15:
        lynch += 1

    if debt and debt < 100:
        lynch += 1

    # =====================================
    # SCORE
    # =====================================

    score = 0

    if pe:

        if pe < 15:
            score += 15

        elif pe < 25:
            score += 10

    if forward_pe:

        if forward_pe < 15:
            score += 10

        elif forward_pe < 25:
            score += 5

    if peg:

        if peg < 1:
            score += 10

        elif peg < 1.5:
            score += 5

    if fcf_yield:

        if fcf_yield > 8:
            score += 15

        elif fcf_yield > 5:
            score += 10

    if roe:

        if roe > 20:
            score += 10

        elif roe > 15:
            score += 5

    if revenue_growth:

        if revenue_growth > 15:
            score += 10

        elif revenue_growth > 10:
            score += 5

    if earnings_growth:

        if earnings_growth > 15:
            score += 10

        elif earnings_growth > 10:
            score += 5

    if debt:

        if debt < 50:
            score += 10

        elif debt < 100:
            score += 5

    if mos:

        if mos > 30:
            score += 20

        elif mos > 20:
            score += 15

        elif mos > 10:
            score += 10

    score = min(
        score,
        100
    )

    # =====================================
    # SIGNAL
    # =====================================

    if score >= 85:

        signal = "🚀 STRONG BUY"

    elif score >= 70:

        signal = "✅ BUY"

    elif score >= 55:

        signal = "🟡 HOLD"

    else:

        signal = "🔴 AVOID"

    if current_rsi > 70:

        signal = "🔴 TAKE PROFITS"

    # =====================================
    # DASHBOARD
    # =====================================

    c1,c2,c3,c4,c5,c6 = st.columns(6)

    c1.metric(
        "Price",
        f"${current_price:.2f}"
    )

    c2.metric(
        "DCF",
        (
            f"${fair_value:.2f}"
            if fair_value
            else "N/A"
        )
    )

    c3.metric(
        "MOS",
        (
            f"{mos:.1f}%"
            if mos is not None
            else "N/A"
        )
    )

    c4.metric(
        "Score",
        f"{score}/100"
    )

    c5.metric(
        "Signal",
        signal
    )

    c6.metric(
        "Buffett",
        f"{buffett}/4"
    )

    # =====================================
    # TABLE
    # =====================================

    df = pd.DataFrame({

        "Metric":[

            "P/E",
            "Forward P/E",
            "PEG",
            "EV/EBITDA",

            "ROE",

            "Revenue Growth",

            "Earnings Growth",

            "Debt/Equity",

            "FCF Yield",

            "Buffett",
            "Lynch"

        ],

        "Value":[

            show(pe),
            show(forward_pe),
            show(peg),
            show(ev_ebitda),

            show(
                roe,
                True
            ),

            show(
                revenue_growth,
                True
            ),

            show(
                earnings_growth,
                True
            ),

            show(debt),

            show(
                fcf_yield,
                True
            ),

            f"{buffett}/4",
            f"{lynch}/3"

        ]

    })

    st.subheader(
        "Fundamental Analysis"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # =====================================
    # DCF HEATMAP
    # =====================================

    if fair_value:

        growths = np.arange(
            3,
            16,
            1
        )

        discounts = np.arange(
            6,
            16,
            1
        )

        matrix = []

        for d in discounts:

            row = []

            for g in growths:

                value = dcf_value(
                    fcf,
                    shares,
                    g,
                    d,
                    terminal,
                    years
                )

                row.append(
                    round(value,0)
                    if value
                    else np.nan
                )

            matrix.append(row)

        heatmap = pd.DataFrame(
            matrix,
            index=[
                f"{x}%"
                for x in discounts
            ],
            columns=[
                f"{x}%"
                for x in growths
            ]
        )

        st.subheader(
            "DCF Sensitivity Heatmap"
        )

        fig_heatmap = px.imshow(
            heatmap,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdYlGn"
        )

        st.plotly_chart(
            fig_heatmap,
            use_container_width=True
        )

    # =====================================
    # CHART
    # =====================================

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["Close"],
            name="Price"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["SMA50"],
            name="SMA50"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist["SMA200"],
            name="SMA200"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

except Exception as e:

    st.error(str(e))
