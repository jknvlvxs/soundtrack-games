import json
import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "..")

data_file = os.path.join(base_dir, "metadata.json")

# Load JSON data
with open(data_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Process data
systems = [game["system"] for game in data]

years = []
for game in data:
    try:
        year = int(
            game["date"][:4]
        )  # Get the first 4 characters and convert to integer
        years.append(year)
    except ValueError as e:
        print(f"Error extracting year from date '{game['date']}': {e}")

# Count occurrences for graphs
system_counts = Counter(systems)
year_counts = Counter(years)

# Create graphs
# Graph 1: Games per System
plt.figure(figsize=(10, 5))
plt.bar(system_counts.keys(), system_counts.values(), color="skyblue")
plt.title("Number of Games per System")
plt.xlabel("System")
plt.ylabel("Number of Games")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print(year for year in year_counts.items() if year >= 2025)

filtered_year_counts = {
    year: count for year, count in year_counts.items() if 1900 <= year <= 2025
}

# Graph 2: Games per Year
plt.figure(figsize=(10, 5))
plt.bar(filtered_year_counts.keys(), filtered_year_counts.values(), color="lightgreen")
plt.title("Number of Games per Year")
plt.xlabel("Year")
plt.ylabel("Number of Games")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
