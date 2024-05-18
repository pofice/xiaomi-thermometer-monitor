import streamlit as st
import pandas as pd
import pymysql

# Set the page layout to wide
st.set_page_config(layout="wide")

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='pofice',
                             password='your_password',
                             db='weather_data')

# Execute the SQL command
sql = "SELECT currentTime, temperature, humidity FROM temp_table;"
df = pd.read_sql_query(sql, connection)

# Close the connection
connection.close()

# Set the index to the 'Time' column
df.set_index('currentTime', inplace=True)

# Plot the temperature line graph using Streamlit
st.subheader("温度")
st.line_chart(df["temperature"])

# Plot the humidity line graph using Streamlit
st.subheader("湿度")
st.line_chart(df["humidity"])

# Show the DataFrame as a table
st.write(df)