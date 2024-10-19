import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats

def calculate_returns(data):
    """Calculate daily and annualized returns."""
    daily_returns = data['Close'].pct_change()
    annualized_return = ((1 + daily_returns.mean()) ** 252) - 1
    return daily_returns, annualized_return

def calculate_volatility(daily_returns):
    """Calculate annualized volatility."""
    return daily_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe Ratio."""
    return (returns - risk_free_rate) / calculate_volatility(returns)

def perform_stock_analysis(tickerDf):
    st.write("### Stock Analysis")

    # Calculate returns
    daily_returns, annualized_return = calculate_returns(tickerDf)
    
    # Calculate volatility
    volatility = calculate_volatility(daily_returns)
    
    # Calculate Sharpe Ratio
    sharpe_ratio = calculate_sharpe_ratio(annualized_return)
    
    # Calculate beta
    market_ticker = yf.Ticker('^GSPC')  # S&P 500 as market proxy
    market_data = market_ticker.history(period='1d', start='2010-5-31', end='2024-5-31')
    market_returns = market_data['Close'].pct_change()
    beta, alpha, r_value, p_value, std_err = stats.linregress(market_returns[1:], daily_returns[1:])

    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Annualized Return", f"{annualized_return:.2%}")
        st.metric("Annualized Volatility", f"{volatility:.2%}")
    with col2:
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
        st.metric("Beta", f"{beta:.2f}")

    # Add explanations
    with st.expander("Understand these metrics"):
        st.write("""
        ### Annualized Return
        Represents the average yearly return of the stock over the analyzed period, assuming returns are compounded. A positive value indicates the stock has gained value over time.

        ### Annualized Volatility
        Measures the degree of variation in the stock's returns over a year. Higher volatility indicates greater risk and potential for both gains and losses.

        ### Sharpe Ratio
        A measure of risk-adjusted return, calculated as (return - risk-free rate) / volatility. A higher Sharpe Ratio indicates better risk-adjusted performance. Typically, ratios above 1 are considered good, above 2 very good, and above 3 excellent.

        ### Beta
        Measures the stock's volatility in relation to the overall market (usually compared to a benchmark like the S&P 500). A beta of 1.0 indicates the stock moves in line with the market. Beta > 1 suggests the stock is more volatile than the market, while Beta < 1 indicates lower volatility compared to the market.
        """)

    # Plot returns distribution
    st.write("### Returns Distribution")
    st.line_chart(daily_returns)

    

st.write("""
         # SimpleStock Price App
         Shown are the stock **closing price** and **volume** of Google!
         """)

st.write("""
         |Symbol|Name|Sector|
         |------|----|------|
         |GOOGL|Alphabet Inc.|Technology|
         |AAPL|Apple Inc.|Technology|
         |MSFT|Microsoft Corporation|Technology|
         |GME|GameStop Corp.|Consumer Discretionary|
         """)

view_option = st.selectbox("View Options:",("Single","Compare"),)
if view_option == "Single":
    option_stock = st.selectbox(
        "Which compaany stock would you like to check?",("GOOGL","AAPL","MSFT","GME"),)

    tickerSymbol = option_stock
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2024-5-31')
    
    opening_price = st.checkbox("Opening Price")
    high_price = st.checkbox("High Price")
    low_price = st.checkbox("Low Price")
    closing_price = st.checkbox("Closing Price")
    volume = st.checkbox("Volume")

    if opening_price:
        st.write("""
                ### Opening Price
                """)
        st.line_chart(tickerDf.Open)
        
    if high_price:
        st.write("""
                ### High Price
                """)
        st.line_chart(tickerDf.High)
        
    if low_price:
        st.write("""
                ### Low Price
                """)
        st.line_chart(tickerDf.Low)

    if closing_price:
        st.write("""
                ### Closing Price
                """)
        st.line_chart(tickerDf.Close)

    if volume:
        st.write("""
            ### Volume
            """)
        st.line_chart(tickerDf.Volume)

    perform_stock_analysis(tickerDf)

if view_option == "Compare":
    st.write("How would you like to compare the stocks?")
    
    stocks = {
        "Google": "GOOGL",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "GameStop": "GME"
    }
    
    selected_stocks = [stock for stock, selected in 
                       [(name, st.checkbox(f"{name} Stock")) for name in stocks.keys()] 
                       if selected]
    
    if selected_stocks:
        data = {}
        for stock in selected_stocks:
            ticker = yf.Ticker(stocks[stock])
            history = ticker.history(period='1d', start='2010-5-31', end='2024-5-31')
            data[stock] = {
                "Opening Price": history.Open,
                "Closing Price": history.Close,
                "Volume": history.Volume
            }
        
        st.write("***Which data would you like to compare?***")
        compare_option = st.selectbox("Compare Option:", ("Opening Price", "Closing Price", "Volume"))
        
        if compare_option:
            chart_data = {stock: data[stock][compare_option] for stock in selected_stocks}
            st.line_chart(chart_data)
 
    else:
        st.write("Please select at least one stock to compare.")
