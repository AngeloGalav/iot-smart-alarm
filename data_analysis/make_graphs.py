import pandas as pd
import matplotlib.pyplot as plt

# Read the data into a DataFrame
data = pd.read_csv("delay_data_bak.csv")

# Read the data into a DataFrame
data['time'] = pd.to_datetime(data['time'])
data['minute'] = data['time'].dt.minute
data['second_group'] = (data['time'].dt.minute * 60 + data['time'].dt.second) // 10

# Remove outliers
data = data[data['delay'] <= 2000]

# Compute cumulative average of delay
data['cum_avg'] = data['delay'].expanding().mean()

# Filter the rows where the minute changes
filtered_data = data[data['second_group'] != data['second_group'].shift()]
filtered_data = filtered_data.reset_index(drop=True)  # Reset index for plotting

print(data['cum_avg'].mean())

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(filtered_data.index, filtered_data['delay'], label='Delay', color="navy")
plt.plot(filtered_data.index, filtered_data['cum_avg'], label='Cumulative Average', color="red")

# Customize the graph
plt.title('Cumulative Average and Delay over Time')
plt.xlabel('t')
plt.ylabel('Values')
plt.legend()
plt.grid(True)

# Save the graph
plt.tight_layout()
plt.savefig('cumulative_average_delay_graph.png')
