#!/usr/bin/env python
# coding: utf-8

# ***Building an interactive web app for technical analysis using Streamlit***
# 
# In this chapter, we have already covered the basics of technical analysis, which can help traders make their decision. However, until now everything was quite static—we downloaded the data, calculated an indicator, plotted it, and if we wanted to change the asset or the range of dates, we had to repeat all the steps. What if there was a better and more interactive way to approach this challenge?
# 
# This is exactly where Streamlit comes into play. Streamlit is an open source framework (and a company under the same name, similarly to Plotly) that allows us to build interactive web apps using only Python, all within minutes. Below you can find the highlights of Streamlit:
# 
# - It is easy to learn and can generate results very quickly
# - It is Python only; no frontend experience is required
# - It allows us to focus purely on the data/ML sides of the app
# - We can use Streamlit’s hosting services for our apps
# 
# In this recipe, we will build an interactive app used for technical analysis. You will be able to select any of the constituents of the S&P 500 and carry out a simple analysis quickly and in an interactive way. What is more, you can easily expand the app to add more features such as different indicators and assets, or even embed backtesting of trading strategies within the app.
# 
# ***Getting ready***
# 
# This recipe is slightly different than the rest. The code of our app “lives” in a single Python script (technical_analysis_app.py), which has around a hundred lines of code. A very basic app can be much more concise, but we wanted to go over some of the most interesting features of Streamlit, even if they are not strictly necessary to make a basic app for technical analysis.
# 
# In general, Streamlit executes code from top to bottom, which makes the explanation easier to fit into the structure used in this book. Thus, the steps in this recipe are not steps per se—they cannot/should not be executed on their own. Instead, they are a step-by-step walkthrough of all the components of the app. While building your own apps or expanding this one, you can freely change the order of the steps as you see fit (as long as they are aligned with Streamlit’s framework).

# import yfinance as yf
# import streamlit as st
# import datetime
# import pandas as pd
# import cufflinks as cf
# from plotly.offline import iplot
# cf.go_offline()

# **1. Import the libraries**

# In[157]:


import yfinance as yf
import streamlit as st
import datetime
import pandas as pd
#!pip install cufflinks
import cufflinks as cf
from plotly.offline import iplot
from plotly.subplots import make_subplots
cf.go_offline()

import plotly.graph_objects as go
import pandas as pd

import requests
from io import StringIO


# **2. Define a function for downloading a list of S&P 500 constituents from Wikipedia**

# In[158]:


@st.cache
def get_sp500_components():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    df = pd.read_html(StringIO(response.text))[0]
    tickers = df["Symbol"].to_list()
    tickers_companies_dict = dict(
        zip(df["Symbol"], df["Security"])
    )
    return tickers, tickers_companies_dict


# **3. Define a function for downloading historical stock prices using yfinance**

# In[159]:


@st.cache
def load_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)

    # Flatten MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# **4. Define a function for storing downloaded data as a CSV file**

# In[160]:


@st.cache
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")


# **5. Define the part of the sidebar used for selecting the ticker and the dates**

# In[161]:


st.sidebar.header("Stock Parameters")
available_tickers, tickers_companies_dict = get_sp500_components()
ticker = st.sidebar.selectbox(
    "Ticker", 
    available_tickers, 
    format_func=tickers_companies_dict.get
)
start_date = st.sidebar.date_input(
    "Start date", 
    datetime.date(2019, 1, 1)
)
end_date = st.sidebar.date_input(
    "End date", 
    datetime.date.today()
)
if start_date > end_date:
    st.sidebar.error("The end date must fall after the start date")


# **6. Define the part of the sidebar used for tuning the details of the technical analysis**

# In[162]:


st.sidebar.header("Technical Analysis Parameters")
volume_flag = st.sidebar.checkbox(label="Add volume")


# **7. Add the expander with parameters of the SMA**

# In[163]:


exp_sma = st.sidebar.expander("SMA")
sma_flag = exp_sma.checkbox(label="Add SMA")
sma_periods= exp_sma.number_input(
    label="SMA Periods", 
    min_value=1, 
    max_value=50, 
    value=20, 
    step=1
)


# **8. Add the expander with parameters of the Bollinger bands**

# In[164]:


exp_bb = st.sidebar.expander("Bollinger Bands")
bb_flag = exp_bb.checkbox(label="Add Bollinger Bands")
bb_periods= exp_bb.number_input(label="BB Periods", 
                                min_value=1, max_value=50, 
                                value=20, step=1)
bb_std= exp_bb.number_input(label="# of standard deviations", 
                            min_value=1, max_value=4, 
                            value=2, step=1)


# **9. Add the expander with parameters of the RSI**

# In[165]:


exp_rsi = st.sidebar.expander("Relative Strength Index")
rsi_flag = exp_rsi.checkbox(label="Add RSI")
rsi_periods= exp_rsi.number_input(
    label="RSI Periods", 
    min_value=1, 
    max_value=50, 
    value=20, 
    step=1
)
rsi_upper= exp_rsi.number_input(label="RSI Upper", 
                                min_value=50, 
                                max_value=90, value=70, 
                                step=1)
rsi_lower= exp_rsi.number_input(label="RSI Lower", 
                                min_value=10, 
                                max_value=50, value=30, 
                                step=1)


# **10. Specify the title and additional text in the app’s main body**

# In[166]:


st.title("A simple web app for technical analysis")
st.write("""
    ### User manual
    * you can select any company from the S&P 500 constituents
""")


# **11. Load the historical stock prices**

# In[167]:


df = load_data(ticker, start_date, end_date)


# **12. Add the expander with a preview of the downloaded data**

# In[168]:


data_exp = st.expander("Preview data")
available_cols = df.columns.tolist()
columns_to_show = data_exp.multiselect(
    "Columns", 
    available_cols, 
    default=available_cols
)
data_exp.dataframe(df[columns_to_show])

csv_file = convert_df_to_csv(df[columns_to_show])
data_exp.download_button(
    label="Download selected as CSV",
    data=csv_file,
    file_name=f"{ticker}_stock_prices.csv",
    mime="text/csv",
)


# **13. Create the candlestick chart with the selected TA indicators**

# In[169]:


title_str = f"{tickers_companies_dict[ticker]}'s stock price"

# Create subplots
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3]
)

# =========================
# Candlestick Chart
# =========================

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ),
    row=1,
    col=1
)

# =========================
# SMA
# =========================

if sma_flag:

    if isinstance(sma_periods, int):
        sma_periods = [sma_periods]

    for period in sma_periods:

        sma = df['Close'].rolling(period).mean()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=sma,
                mode='lines',
                name=f'SMA {period}'
            ),
            row=1,
            col=1
        )

# =========================
# Bollinger Bands
# =========================

if bb_flag:

    sma_bb = df['Close'].rolling(bb_periods).mean()
    std_bb = df['Close'].rolling(bb_periods).std()

    upper_band = sma_bb + (std_bb * bb_std)
    lower_band = sma_bb - (std_bb * bb_std)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=upper_band,
            mode='lines',
            name='Upper BB'
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=lower_band,
            mode='lines',
            name='Lower BB'
        ),
        row=1,
        col=1
    )

# =========================
# RSI
# =========================

if rsi_flag:

    delta = df['Close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(rsi_periods).mean()
    avg_loss = loss.rolling(rsi_periods).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=rsi,
            mode='lines',
            name='RSI'
        ),
        row=2,
        col=1
    )

    # RSI upper band
    fig.add_hline(
        y=rsi_upper,
        line_dash="dash",
        row=2,
        col=1
    )

    # RSI lower band
    fig.add_hline(
        y=rsi_lower,
        line_dash="dash",
        row=2,
        col=1
    )

# =========================
# Layout
# =========================

fig.update_layout(
    title=title_str,
    xaxis_rangeslider_visible=False,
    height=900
)

# Axis labels
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="RSI", row=2, col=1)

# =========================
# Streamlit Display
# =========================

st.plotly_chart(fig, width="stretch")
