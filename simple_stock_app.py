import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date

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
    # Try different ARIMA orders
    orders = [(1,1,1), (1,1,2), (2,1,2), (1,2,1)]
    best_aic = np.inf
    best_model = None
    
    for order in orders:
        try:
            model = ARIMA(data, order=order)
            results = model.fit()
            if results.aic < best_aic:
                best_aic = results.aic
                best_model = results
        except:
            continue
    
    if best_model is None:
        st.error("Unable to fit a suitable ARIMA model. Please try a different stock or time range.")
        return None, None

    # Make forecast
    forecast = best_model.forecast(steps=periods)
    
    return forecast, best_model

def plot_forecast(data, forecast, periods):
    """
    Plot the original data and the forecast.
    """
    if forecast is None:
        return None
    
    start_date = data.index[-1] - timedelta(days=periods)
    plot_data = data.loc[start_date:]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(plot_data.index, plot_data, label='Observed Closing Price')
    ax.plot(pd.date_range(start=data.index[-1], periods=len(forecast)+1, freq='D')[1:],
            forecast, color='red', label='Forecast')
    ax.fill_between(pd.date_range(start=data.index[-1], periods=len(forecast)+1, freq='D')[1:],
                    forecast - forecast.std() * 2,
                    forecast + forecast.std() * 2,
                    color='pink', alpha=0.3, label='95% Confidence Interval')
    ax.set_title(f'ARIMA Forecast (Last {periods} days + {periods} days forecast)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price (Closing)')
    ax.legend()
    fig.autofmt_xdate()
    
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
    market_ticker = '^GSPC'  # S&P 500 as market proxy
    market_data = get_stock_data(market_ticker, tickerDf.index[0].strftime('%Y-%m-%d'))
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
        
    if forecast is not None:
        fig = plot_forecast(tickerDf['Close'], forecast, forecast_periods)
        if fig:
            st.pyplot(fig)
        
        st.write(f"Forecast for next {forecast_periods} days:")
        st.write(forecast)
        
        with st.expander("Understand ARIMA Forecast"):
            st.write("""
            ### ARIMA (AutoRegressive Integrated Moving Average) Forecast

            This forecast is based on the stock's closing prices. The ARIMA model attempts to capture patterns in the historical data to make predictions.

            Key points about this forecast:
            
            - The blue line shows the actual closing prices for the past {forecast_periods} days.
            - The red line shows the predicted closing prices for the next {forecast_periods} days.
            - The pink shaded area represents the 95% confidence interval for the forecast.
            - The model automatically selects the best ARIMA parameters from a predefined set.
            - If the forecast appears as a straight line, it suggests the model expects little change or is struggling to capture the stock's behavior.
            - Remember that stock prices are influenced by many external factors that cannot be predicted by past data alone.
            - Always use forecasts as one of many tools in your investment decision-making process, not as guaranteed predictions.
            """.format(forecast_periods=forecast_periods))

        # Display model summary
        with st.expander("ARIMA Model Summary"):
            st.text(results.summary())
    else:
        st.error("Unable to generate forecast. Please try a different stock or time range.")

def get_stock_data(ticker, start_date, end_date=None):
    """
    Fetch stock data from start_date to end_date (or today if not specified).
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    stock_data = yf.Ticker(ticker)
    df = stock_data.history(start=start_date, end=end_date)
    return df

today = date.today().strftime('%Y-%m-%d')

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
        "Which company stock would you like to check?",("GOOGL","AAPL","MSFT","GME"),)

    tickerSymbol = option_stock
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end=today)
    
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
            history = ticker.history(period='1d', start='2010-5-31', end=today)
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
