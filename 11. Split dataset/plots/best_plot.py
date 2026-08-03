import matplotlib.pyplot as plt
import numpy as np

# Data
genres = [
        'RPG', 'Platform', 'Action', 'Strategy', 'Fighting', 'Sports', 'Shooters', 'Puzzle', 'Racing', 'Adventure', 'Simulation', ]

before = [89573, 45628,    25396,     19703,      19492,     17455,      15758,     10310,    9269,      8427,         7770]
after  = [9582,  9506,      8692,      6340,      7889,       7581,      8112,      5990,     6272,      4629,         3753]

# Standard width for a single column in a two-column academic paper is ~3.5 to 4.5 inches.
fig, ax = plt.subplots(figsize=(9, 8)) 

# Plotting 'before' first so it's in the background
ax.bar(genres, before, label='Before Downsample', color='lightsteelblue', 
       edgecolor='black', linewidth=0.5)

# Plotting 'after' on top
ax.bar(genres, after, label='After Downsample', color='royalblue', 
       edgecolor='black', linewidth=0.5)

# Formatting for academic paper (clear, readable fonts)
ax.set_ylabel('Number of Videos', fontsize=16)
ax.set_xlabel('Genre', fontsize=16)

# Rotating the x-labels so they don't overlap in a narrow column layout
plt.xticks(rotation=45, ha='right', fontsize=16)
plt.yticks(fontsize=16)

# Legend
ax.legend(fontsize=16)

# Add a subtle grid behind the bars for easier value tracking
ax.set_axisbelow(True)
ax.yaxis.grid(True, linestyle='--', alpha=0.7)

# Adjust layout so nothing gets cut off
plt.tight_layout()

# Save as a high-resolution PNG (300 DPI is standard for publications)
plt.savefig('genre_downsample.png', dpi=600)
plt.show()