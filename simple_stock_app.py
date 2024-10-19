import streamlit as st
import yfinance as yf
import pandas as pd

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
