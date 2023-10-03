from pathlib import Path
import appdirs as ad
CACHE_DIR = ".cache"
# Force appdirs to say that the cache dir is .cache
ad.user_cache_dir = lambda *args: CACHE_DIR
# Create the cache dir if it doesn't exist
Path(CACHE_DIR).mkdir(exist_ok=True)

import yfinance as yf

import streamlit as st
import pandas as pd
import requests

# Streamlit App title
st.title('Stock Screening from S&P 500 index')

# User-adjustable parameters
min_growth_rate = st.slider('Minimum Annual Earnings Growth Rate', 0.0, 2.0, 0.1)
max_peg_ratio = st.slider('Maximum PEG Ratio', 0.0, 4.0, 1.0)
min_free_cash_flow = st.slider('Minimum Free Cash Flow (Million USD)', 0, 1000, 10)

# Get a list of stock symbols, can be obtained from Yahoo Finance
def get_stock_symbols():
    # Here, we use getting the components of the S&P 500 index as an example
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    table = pd.read_html(response.text, header=0)
    df = table[0]
    symbols = df['Symbol'].tolist()
    return symbols

# Screen stocks that meet the criteria
def screen_stocks(symbols):
    selected_stocks = []
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        try:
            info = stock.info
            pe_ratio = info['trailingPE']
            forward_pe = info['forwardPE']
            eps_growth_next_year = info['forwardEpsEstimate'] / info['trailingEps'] - 1
            peg_ratio = forward_pe / (eps_growth_next_year*100)
            fcf = info.get('freeCashflow', 0)
            
            if eps_growth_next_year >= min_growth_rate and peg_ratio <= max_peg_ratio and fcf >= min_free_cash_flow * 1e6:
                selected_stocks.append({
                    'Symbol': symbol,
                    'PEG Ratio': peg_ratio,
                    'Free Cash Flow': fcf / 1e6
                })
        except Exception as e:
            pass

    return selected_stocks

# Get a list of stock symbols
symbols = get_stock_symbols()

# Screen stocks that meet the criteria
selected_stocks = screen_stocks(symbols)

# Convert the result to a DataFrame
selected_stocks_df = pd.DataFrame(selected_stocks)

# Display the screening results
st.write('Screening Results:')
st.write(selected_stocks_df)
