import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read data from 'data.json'
with open('data.json', 'r') as file:
    data = json.load(file)

# Extract the 'ownersPoints' list from the JSON data
ownersPoints = data['ownersPoints']

# Convert data to a pandas DataFrame
df = pd.DataFrame(ownersPoints)

# Convert timestamps to datetime objects
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

# Define the date range
start_date = '2024-01-01'
end_date = datetime.now().strftime('%Y-%m-%d')

# Convert strings to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter DataFrame by date range
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Check if there is data
if df.empty:
    print(f"No data available from {start_date.date()} to {end_date.date()}.")
else:
    # Sort the DataFrame
    df = df.sort_values('date')

    # Create a complete date range
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Reindex DataFrame to include all dates
    df = df.set_index('date').reindex(all_dates).rename_axis('date').reset_index()

    # Fill missing values
    df['numberOfOwners'] = df['numberOfOwners'].ffill()  # Forward-fill missing values

    # Ensure no NaN remains
    df['numberOfOwners'] = df['numberOfOwners'].fillna(0).astype(int)  # Replace NaN with 0 and convert to int

    # Set the plot size
    plt.figure(figsize=(15, 7))

    # Plot the data with markers (dots)
    plt.plot(df['date'], df['numberOfOwners'], marker='o', linestyle='-')

    # Format x-axis to show all dates
    ax = plt.gca()
    ax.set_xticks(df['date'])  # Set all dates as ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    # Rotate x-axis labels for readability
    plt.xticks(rotation=90, fontsize=8)

    # Add data labels to each dot
    for x, y in zip(df['date'], df['numberOfOwners']):
        plt.text(x, y + 5, f'{y}', fontsize=9, ha='center', va='bottom')

    # Add titles and labels
    plt.title('Ascelia: Ägare hos Avanza från 2024')
    plt.xlabel('Datum')
    plt.ylabel('Ägare hos Avanza')

    # Add gridlines
    plt.grid(True)

    # Adjust layout
    plt.tight_layout()

    # Show the plot
    plt.show()
