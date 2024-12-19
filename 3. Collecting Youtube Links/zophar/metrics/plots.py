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
systems = [game["console"] for game in data]

years = []
for game in data:
    try:
        if(game["release_date"]):
            year = int(game["release_date"][-4:])
            years.append(year)
    except ValueError as e:
        print(f"Error extracting year from date '{game['release_date']}': {e}")

# Count occurrences for graphs
system_counts = Counter(systems)
year_counts = Counter(years)

# Create graphs
# Graph 1: Games per System
plt.figure(figsize=(16, 8))
plt.bar(system_counts.keys(), system_counts.values(), color="skyblue")
plt.title("Number of Games per System")
plt.xlabel("System")
plt.ylabel("Number of Games")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.show()

filtered_year_counts = {year: count for year, count in year_counts.items() if 1900 <= year <= 2025}

# Graph 2: Games per Year
average_games = sum(filtered_year_counts.values()) / len(filtered_year_counts)
plt.figure(figsize=(16, 8))
plt.bar(filtered_year_counts.keys(), filtered_year_counts.values(), color="lightgreen")
plt.axhline(y=average_games, color='red', linestyle=':', label=f'Average: {average_games:.2f}')
plt.title("Number of Games per Year")
plt.xlabel("Year")
plt.ylabel("Number of Games")
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.show()