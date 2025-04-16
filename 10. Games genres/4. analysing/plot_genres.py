import pandas as pd
import matplotlib.pyplot as plt

GENRES_CSV = '/home/es119256/datasets/vmdb/deepseek_genres.csv'

df = pd.read_csv(GENRES_CSV, sep=',')

df['game_genre'].value_counts().plot(kind='bar')


plt.ylabel('Frequency')
plt.xlabel('Genres')

plt.savefig('./genres_hist.png', bbox_inches='tight')