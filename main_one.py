import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Read data from 'data.json'
with open('data.json', 'r') as file:
    data = json.load(file)

# Extract the 'ownersPoints' list from the JSON data
ownersPoints = data['ownersPoints']

# Convert data to a pandas DataFrame
df = pd.DataFrame(ownersPoints)

# Convert timestamps to datetime objects
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

# **Remove the Filtering Step to Include All Years**
# Comment out or remove the lines that filter by year
# current_year = 2024
# df = df[df['date'].dt.year == current_year]

# Sort the DataFrame by date
df = df.sort_values('date')

# Set the plot size
plt.figure(figsize=(15, 7))

# **Plot the data with markers (dots)**
plt.plot(df['date'], df['numberOfOwners'], marker='o', linestyle='-')

# Format the x-axis to show dates properly
ax = plt.gca()

# **Adjust x-axis ticks for multiple years**
# Set major ticks to every year
ax.xaxis.set_major_locator(mdates.YearLocator())
# Set minor ticks to every month or quarter
ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))  # Every 3 months
# Format major tick labels as years
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# **Add data labels to each dot (optional)**
# Be cautious: adding labels to every point can clutter the plot
for i, (x, y) in enumerate(zip(df['date'], df['numberOfOwners'])):
    if i % 10 == 0:  # Adjust this value as needed
        plt.text(x, y + 5, f'{y}', fontsize=8, ha='center', va='bottom')

# Add titles and labels
plt.title('Ascelia: Ägare hos Avanza Over Time')
plt.xlabel('Datum')
plt.ylabel('Ägare hos Avanza')

# Add gridlines
plt.grid(True)

# Adjust layout to prevent clipping of tick-labels
plt.tight_layout()

# Display the plot
plt.show()
