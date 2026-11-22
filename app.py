import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ta
from ta.trend import MACD
from ta.volatility import BollingerBands
import math

st.set_page_config(
    page_title="Stock Analyzer Pro",
    layout="wide"
)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def clean(x):

    if x is None:
        return None

    try:
        if np.isnan(x):
            return None
    except:
        pass

    try:
        return float(x)
    except:
        return None


def pct(x):

    if x is None:
        return None

    return x * 100


def show(x, p=False):

    if x is None:
        return "N/A"

    if p:
        return f"{x:.2f}%"

    return f"{x:.2f}"


def human(n):

    if n is None:
        return "N/A"

    if n > 1e12:
        return f"{n/1e12:.2f}T"

    if n > 1e9:
        return f"{n/1e9:.2f}B"

    if n > 1e6:
        return f"{n/1e6:.2f}M"

    return str(round(n))


# ---------------------------------------------------
# DCF
# ---------------------------------------------------

def dcf_model(
    fcf,
    shares,
    growth,
    discount,
    terminal,
    years
):

    if (
        fcf is None
        or shares is None
        or shares == 0
    ):
        return None

    growth /= 100
    discount /= 100
    terminal /= 100

    if discount <= terminal:
        return None

    pv = 0

    current_fcf = fcf

    for year in range(1, years + 1):

        current_fcf *= (1 + growth)

        pv += (
            current_fcf
            /
            ((1 + discount) ** year)
        )

    terminal_fcf = current_fcf * (
        1 + terminal
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

    total_value = pv + terminal_pv

    return total_value / shares


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("DCF Settings")

growth = st.sidebar.slider(
    "FCF Growth %",
    0.0, 20.0, 8.0
)

discount = st.sidebar.slider(
    "Discount Rate %",
    5.0, 20.0, 10.0
)

terminal = st.sidebar.slider(
    "Terminal Growth %",
    0.0, 5.0, 2.5
)

years = st.sidebar.slider(
    "Years",
    5, 15, 10
)

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------

st.title("📈 Stock Analyzer Pro")

ticker_input = st.text_input(
    "Ticker",
    value="MSFT"
).upper()

if ticker_input:

    try:

        ticker = yf.Ticker(
            ticker_input
        )

        info = ticker.info

        hist = ticker.history(
            period="2y",
            auto_adjust=True
        )

        if hist.empty:

            st.error(
                "No data found"
            )

            st.stop()

        # TECHNICAL

        hist["RSI"] = (
            ta.momentum
            .RSIIndicator(
                hist["Close"]
            )
            .rsi()
        )

        macd_indicator = MACD(
            hist["Close"]
        )

        hist["MACD"] = (
          macd_indicator.macd()
        )

        hist["MACD_SIGNAL"] = (
         macd_indicator.macd_signal()
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

        bb = BollingerBands(
            hist["Close"]
        )

        hist["BB_UPPER"] = (
            bb.bollinger_hband()
        )

        hist["BB_LOWER"] = (
            bb.bollinger_lband()
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

        # FUNDAMENTALS

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

        gross_margin = pct(
            clean(
                info.get(
                    "grossMargins"
                )
            )
        )

        debt = clean(
            info.get(
                "debtToEquity"
            )
        )

        roa = pct(
            clean(
                info.get(
                    "returnOnAssets"
                )
            )
        )

        operating_margin = pct(
            clean(
                info.get(
                    "operatingMargins"
                )
            )
        )

        net_margin = pct(
            clean(
               info.get(
                   "profitMargins"
               )
            )
        )

        price_sales = clean(
            info.get(
                "priceToSalesTrailing12Months"
            )
        )

        price_book = clean(
            info.get(
                "priceToBook"
            )
        )

        current_ratio = clean(
            info.get(
                "currentRatio"
            )
        )

        quick_ratio = clean(
            info.get(
                "quickRatio"
            )
        )

        dividend_yield = pct(
            clean(
                info.get(
                    "dividendYield"
                )
            )
        )

        beta = clean(
            info.get(
                "beta"
            )
        )

        total_cash = clean(
            info.get(
                "totalCash"
            )
        )

        total_debt = clean(
            info.get(
                "totalDebt"
            )
        )
        market_cap = clean(
            info.get(
                "marketCap"
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

        # Buffett

        buffett = 0

        if roe and roe > 15:
            buffett += 1

        if gross_margin and gross_margin > 40:
            buffett += 1

        if debt and debt < 50:
            buffett += 1

        if revenue_growth and revenue_growth > 0:
            buffett += 1

        if fcf_yield and fcf_yield > 5:
            buffett += 1

        # Lynch

        lynch = 0

        if peg and peg < 1.5:
            lynch += 1

        if earnings_growth and earnings_growth > 15:
            lynch += 1

        if debt and debt < 100:
            lynch += 1

        # DCF

        fair_value = dcf_model(
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

        # TOP METRICS

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "Price",
            f"${current_price:.2f}"
        )

        c2.metric(
            "RSI",
            f"{current_rsi:.1f}"
        )

        c3.metric(
            "DCF",
            (
                f"${fair_value:.2f}"
                if fair_value
                else "N/A"
            )
        )

        c4.metric(
            "Margin Of Safety",
            (
                f"{mos:.1f}%"
                if mos is not None
                else "N/A"
            )
        )

        # TABLE

        df = pd.DataFrame({

            "Metric":[

                metrics = [

            ("P/E", pe),
            ("Forward P/E", forward_pe),
            ("PEG", peg),
            ("P/S", price_sales),
            ("P/B", price_book),
            ("EV/EBITDA", ev_ebitda),

            ("ROE %", roe),
            ("ROA %", roa),
            ("ROIC %", roic),

            ("Gross Margin %", gross_margin),
            ("Operating Margin %", operating_margin),
            ("Net Margin %", net_margin),

            ("Revenue Growth %", revenue_growth),
            ("Earnings Growth %", earnings_growth),

            ("Debt/Equity", debt_equity),

            ("Current Ratio", current_ratio),
            ("Quick Ratio", quick_ratio),

            ("FCF Yield %", fcf_yield),

            ("Dividend Yield %", dividend_yield),

            ("Beta", beta),

            ("Volatility %", volatility),

            ("Sharpe Ratio", sharpe_ratio),

            ("Max Drawdown %", max_drawdown)

]

metrics_df = pd.DataFrame(
    metrics,
    columns=[
        "Metric",
        "Value"
    ]
)

st.subheader(
    "Full Analysis"
)

st.dataframe(
    metrics_df,
    use_container_width=True
)
            ],

            "Value":[

                show(pe),

                show(forward_pe),

                show(peg),

                show(ev_ebitda),

                show(roe,True),

                show(
                    revenue_growth,
                    True
                ),

                show(
                    earnings_growth,
                    True
                ),

                show(
                    fcf_yield,
                    True
                ),

                show(
                    debt,
                    True
                ),

                human(
                    market_cap
                )

            ]

        })

        st.subheader(
            "Fundamentals"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        # SCORES

        col1,col2 = st.columns(2)

        col1.metric(
            "Buffett",
            f"{buffett}/5"
        )

        col2.metric(
            "Lynch",
            f"{lynch}/3"
        )

        # HEATMAP

        if (
            fair_value
            and shares
        ):

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

                    value = dcf_model(
                        fcf,
                        shares,
                        g,
                        d,
                        terminal,
                        years
                    )

                    row.append(
                        value
                    )

                matrix.append(
                    row
                )

            heatmap = pd.DataFrame(
                matrix,
                index=
                discounts,
                columns=
                growths
            )

            st.subheader(
                "DCF Heatmap"
            )

            fig = px.imshow(

                heatmap,

                text_auto=".0f",

                aspect="auto",

                color_continuous_scale="RdYlGn"

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # PRICE CHART

        st.subheader(
            "Price Chart"
        )

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

        st.error(
            str(e)
        )
