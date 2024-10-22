import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
import matplotlib.pyplot as plt

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

def perform_arima_forecast(data, periods=30):
    """
    Perform ARIMA forecast on the given time series data.
    """
    # Automatically find the best ARIMA parameters
    model = auto_arima(data, start_p=1, start_q=1, max_p=3, max_q=3, m=1,
                       start_P=0, seasonal=False, d=1, D=1, trace=True,
                       error_action='ignore', suppress_warnings=True, stepwise=True)

    # Fit the ARIMA model
    arima_model = ARIMA(data, order=model.order)
    results = arima_model.fit()

    # Make forecast
    forecast = results.forecast(steps=periods)
    
    return forecast, results

def plot_forecast(data, forecast):
    """
    Plot the original data and the forecast.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data.index, data, label='Observed')
    ax.plot(pd.date_range(start=data.index[-1], periods=len(forecast)+1, freq='D')[1:],
            forecast, color='red', label='Forecast')
    ax.set_title('ARIMA Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price')
    ax.legend()
    return fig

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

    # ARIMA Forecast
    st.write("### ARIMA Forecast")
    forecast_periods = st.slider("Forecast Periods", min_value=7, max_value=90, value=30)
    
    with st.spinner('Calculating ARIMA forecast...'):
        forecast, results = perform_arima_forecast(tickerDf['Close'], periods=forecast_periods)
        
    st.pyplot(plot_forecast(tickerDf['Close'], forecast))
    
    with st.expander("Understand ARIMA Forecast"):
        st.write("""
        ### ARIMA (AutoRegressive Integrated Moving Average) Forecast

        The ARIMA model is a popular and flexible forecasting method for time series data. It combines three components:
        
        1. **AR (AutoRegressive)**: Uses the dependent relationship between an observation and some number of lagged observations.
        2. **I (Integrated)**: Differencing of raw observations to make the time series stationary.
        3. **MA (Moving Average)**: Uses the dependency between an observation and a residual error from a moving average model applied to lagged observations.

        Key points about this forecast:
        
        - The model automatically selects the best parameters for your data.
        - The red line shows the predicted future stock prices.
        - This forecast assumes that past patterns in the stock price will continue in the future.
        - While useful, remember that stock prices are influenced by many external factors that cannot be predicted by past data alone.
        - Always use forecasts as one of many tools in your investment decision-making process.
        """)

    # Display model summary
    with st.expander("ARIMA Model Summary"):
        st.text(results.summary())

st.write("""
         # SimpleStock Price App
         Shown are the stocks of Google, Apple, Microsoft, and GameStop! You can select the data you want to see whether it is the opening price, closing price, high price, low price, or volume, whether you want to view a single stock or compare multiple stocks!
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
