import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Fetch data from Avanza API
url = "https://www.avanza.se/_api/market-guide/number-of-owners/941919"
headers = {
    "User-Agent": "Mozilla/5.0"  # Required to avoid 403 error from Avanza
}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

# Load the JSON response
data = response.json()

# Extract the 'ownersPoints' list
ownersPoints = data['ownersPoints']

# Convert data to a pandas DataFrame
df = pd.DataFrame(ownersPoints)

# Convert timestamps to datetime objects
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

# **Define the date range**
start_date = '2024-01-01'  # Start from December 1, 2023
end_date = datetime.now().strftime('%Y-%m-%d')  # Current date

# Convert strings to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# **Filter the DataFrame based on the date range**
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Check if there is data in the specified date range
if df.empty:
    print(f"No data available from {start_date.date()} to {end_date.date()}.")
else:
    # Sort the DataFrame by date
    df = df.sort_values('date')

    # Set the plot size
    plt.figure(figsize=(15, 7))

    # **Plot the data with markers (dots)**
    plt.plot(df['date'], df['numberOfOwners'], marker='o', linestyle='-')

    # Format the x-axis to show dates at data point dates
    ax = plt.gca()

    # Set the x-axis ticks to the data point dates
    ax.set_xticks(df['date'])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    plt.xticks(rotation=45)  # Rotate labels for readability

    # Optionally, reduce font size to prevent label overlap
    plt.xticks(fontsize=8)

    # **Add data labels to each dot**
    for x, y in zip(df['date'], df['numberOfOwners']):
        plt.text(x, y + 5, f'{y}', fontsize=9, ha='center', va='bottom')

    # Add titles and labels
    plt.title('Ascelia: Ägare hos Avanza från 2024')
    plt.xlabel('Datum')
    plt.ylabel('Ägare hos Avanza')

    # Add gridlines
    plt.grid(True)

    # Adjust layout to prevent clipping of tick-labels
    plt.tight_layout()

    # Display the plot
    plt.show()
