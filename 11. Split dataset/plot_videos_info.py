import os
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

# Load CSV
df = pd.read_csv("selected_videos_info.csv")

# Segments per game_id
segments_per_game = df["game_id"].value_counts().reset_index()
segments_per_game.columns = ["game_id", "segments"]

table_str = tabulate(segments_per_game, headers="keys", tablefmt="github")

os.makedirs("plots", exist_ok=True)

# Save to file
with open("plots/games_by_number_of_segments.txt", "w") as f:
    f.write(table_str)

# Segments per genre
segments_per_genre = df["genre"].value_counts()
print("\nSegments per genre:")
print(segments_per_genre)

# Percentage of segments per genre
percentage_per_genre = df["genre"].value_counts(normalize=True) * 100
print("\nPercentage of segments per genre:")
print(percentage_per_genre.round(2))

# --- Plots ---

# 1. Segments per game_id (Top 20 for readability)
top_n = 20
plt.figure(figsize=(12, 6))
segments_per_game.head(top_n).plot(kind="bar", color="skyblue")
plt.title(f"Top {top_n} Games by Number of Segments")
plt.xlabel("Game ID")
plt.ylabel("Number of Segments")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
# plt.show()
plt.savefig("plots/games_by_number_of_segments.png", bbox_inches="tight")

# 2. Segments per genre
plt.figure(figsize=(6, 6))
segments_per_genre.plot(kind="bar", color="salmon")
plt.title("Segments per Genre")
plt.xlabel("Genre")
plt.ylabel("Number of Segments")
plt.tight_layout()
# plt.show()
plt.savefig("plots/segments_per_genre.png", bbox_inches="tight")

# 3. Percentage of segments per genre (as bar chart)
plt.figure(figsize=(6, 6))
percentage_per_genre.plot(kind="bar", color="seagreen")
plt.title("Percentage of Segments per Genre")
plt.xlabel("Genre")
plt.ylabel("Percentage (%)")
plt.tight_layout()
# plt.show()
plt.savefig("plots/percentage_of_segments_per_genre.png", bbox_inches="tight")
