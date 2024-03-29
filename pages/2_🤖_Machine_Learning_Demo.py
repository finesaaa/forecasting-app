import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import plotly.graph_objs as go

# Function to load and process the default dataset
def load_default_data():
    df = pd.read_csv('data_input/office_monthly_sales.csv')
    return df

# Function to convert the dataset to the required format (ds and y)
def convert_to_prophet_format(df, date_column=None, target_column=None):
    if date_column is None:
        date_column = 'Order Month'
    if target_column is None:
        target_column = 'Total Quantity'
    
    # Check if the selected date column exists in the DataFrame
    if date_column not in df.columns:
        st.error(f'Selected date column "{date_column}" not found in the dataset.')
        return None
    
    df = df[[date_column, target_column]].rename(
        columns={date_column: 'ds',
                 target_column: 'y'})
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# Function to perform forecasting using Prophet
def forecast(df):
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=12, freq='MS')
    forecast = model.predict(future)
    return forecast, model

def main():
    st.set_page_config(page_title='Time Series Forecasting App', layout='wide')
    st.title('📈 Time Series Forecasting App')

    # Load the default dataset
    df = load_default_data()

    st.sidebar.title('📋 Menu')

    # Rules and Usage Instructions
    st.sidebar.subheader('📜 Rules and Usage Instructions')
    st.sidebar.write("This app allows you to perform time series forecasting using Prophet.")
    st.sidebar.write("To use this app, follow these steps:")
    st.sidebar.write("1. The default dataset will be automatically loaded.")
    st.sidebar.write("2. You can select the target column (y) and the date column for ds.")
    st.sidebar.write("3. The forecast will be displayed automatically.")

    # Allow users to select the target column (y)
    target_column_default = 'Total Quantity'
    date_column = 'Order Month'

    # Get list of column names
    column_names = df.columns.to_list()

    # Remove 'Order Month' from the list
    if date_column in column_names:
        column_names.remove(date_column)

    target_column = st.sidebar.selectbox('Select Target Column (`y`) 👇', options=column_names, index=df.columns.get_loc(target_column_default))

    if target_column == 'Total Quantity':
        st.subheader('🛍️ Monthly Demand Forecasting - Walmart Retail Stores')
    elif target_column == 'Total Sales':
        st.subheader('🛍️ Monthly Sales Forecasting - Walmart Retail Stores')
    if target_column == 'Total Profit':
        st.subheader('🛍️ Monthly Profit Forecasting - Walmart Retail Stores')
        

    # Convert the dataset to the required format (ds and y)
    df_prophet = convert_to_prophet_format(df, date_column, target_column)
    if df_prophet is None:
        return  # Exit early if date column is not found
    
    # Perform forecasting using Prophet
    forecast_data, model = forecast(df_prophet)

    # Display the forecast output
    st.plotly_chart(plot_plotly(model, forecast_data), use_container_width=True)
    st.plotly_chart(plot_components_plotly(model, forecast_data), use_container_width=True)

    # Date range selection
    st.subheader('📅 Date Range Selection')
    min_date = pd.to_datetime(df_prophet['ds'].max())
    max_date = pd.to_datetime(forecast_data['ds'].max())
    date_range = st.date_input('Select a date for the forecast (only 1st of Month, example `01-01-2023`):', min_value=min_date, max_value=max_date, value=(min_date, max_date))

    # Filter forecast data based on selected date range
    filtered_forecast_data = forecast_data[(forecast_data['ds'] >= date_range[0].strftime('%Y-%m-%d')) & (forecast_data['ds'] <= date_range[1].strftime('%Y-%m-%d'))]

    # Display the filtered forecast data
    st.subheader('📊 Forecast Data for Selected Date Range:')
    st.write(filtered_forecast_data[['ds','yhat','yhat_upper', 'yhat_lower','trend']])

    # Copyright notice
    st.sidebar.write('---')
    st.sidebar.write("© Product Team Algoritma, 2024")

if __name__ == '__main__':
    main()
