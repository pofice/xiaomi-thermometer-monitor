import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set the page layout to wide
st.set_page_config(layout="wide")

# Read the data from the JSON file
data = []
with open("data.json", "r") as file:
    for line in file:
        data.append(json.loads(line.replace(": ", ":")))

# Extract the time, temperature, and humidity values
times = [entry["currentTime"] for entry in data]
temperatures = [entry["temperature"] for entry in data]
humidity = [entry["humidity"] for entry in data]

# Create a DataFrame from the extracted data
df = pd.DataFrame({"Time": times, "Temperature": temperatures, "Humidity": humidity})

# Plot the temperature line graph using Streamlit
st.subheader("温度")
st.line_chart(df.set_index("Time")["Temperature"])

# Plot the humidity line graph using Streamlit
st.subheader("湿度")
st.line_chart(df.set_index("Time")["Humidity"])

# Show the DataFrame as a table
st.write(df)
