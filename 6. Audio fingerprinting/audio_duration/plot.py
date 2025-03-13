import json
import numpy as np
import matplotlib.pyplot as plt

# Carregar os dados do JSON
with open("durations.json", "r") as f:
    data = json.load(f)

duracoes = np.array(data)  # Converter para NumPy array

# Definir estatísticas
media = np.mean(duracoes)
limiar = 5  # Limiar de 5 segundos

# Criar o histograma
plt.figure(figsize=(10, 5))
plt.hist(duracoes, bins=80, color="royalblue", edgecolor="black", alpha=0.7)

# Adicionar linha da média
plt.axvline(media, color="green", linestyle="--", linewidth=2, label=f'Média ({media:.2f}s)')

# Adicionar linha do limiar
plt.axvline(limiar, color="orange", linestyle="--", linewidth=2, label=f'Limiar ({limiar}s)')

# Configuração do gráfico
plt.xlabel("Duração dos áudios (s)")
plt.ylabel("Frequência")
plt.title("Distribuição das Durações dos Arquivos de Áudio")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Exibir o gráfico
plt.savefig("grafico.png")
