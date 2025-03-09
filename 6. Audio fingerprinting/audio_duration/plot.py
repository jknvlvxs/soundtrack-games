import json
import matplotlib.pyplot as plt
import numpy as np
import math

# Load durations from JSON file
with open("./durations.json", "r") as file:
    durations = json.load(file)

# Calculate the median
duration_median = np.median(durations)

# Plot histogram
plt.figure(figsize=(10, 5))
plt.hist(durations, bins=80, color="skyblue", edgecolor="black", alpha=0.6)
plt.axvline(duration_median, color="red", linestyle="dashed", linewidth=2, label=f"Median: {duration_median:.2f} sec")
plt.axvline(8, color="green", linestyle="dashed", linewidth=2, label="8 sec")

# Labels and title
plt.xlabel("Duration (seconds)")
plt.ylabel("Frequency")
plt.title("Histogram of Audio Durations")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Show plot
plt.show()
