import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# Plot the line graph using Streamlit
st.line_chart(df.set_index("Time"))

# Show the DataFrame as a table
st.write(df)
