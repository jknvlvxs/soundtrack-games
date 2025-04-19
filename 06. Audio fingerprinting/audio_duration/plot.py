import json
import numpy as np
import matplotlib.pyplot as plt

# Carregar os dados do arquivo JSON
with open("durations.json", "r") as f:
    durations = json.load(f)

# Substituir valores maiores que 360 por 360
durations = [min(d, 360) for d in durations]

# Criar os bins (de 5 em 5 até o maior valor dos dados)
bins = np.arange(0, max(durations) + 5, 5)  # Intervalos de 5 em 5 até o máximo valor encontrado

# Criar o histograma
plt.figure(figsize=(16, 8))
plt.hist(durations, bins=bins, edgecolor="black", alpha=0.8)

# Personalizar o gráfico
plt.xlabel("Duração (segundos)")
plt.ylabel("Quantidade de arquivos")
plt.title("Distribuição das Durações dos Arquivos de Áudio")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Criar os ticks do eixo X a cada 50 unidades
xticks = np.arange(0, max(durations) + 60, 60)

# Verificar se 360 está nos ticks e adicionar se necessário
if 355 not in xticks:
    xticks = np.append(xticks, 355)

# Adicionar o label ">= 360" no último tick
xtick_labels = [str(tick) if tick < 355 else (">= 360" if tick == 355 else "") for tick in xticks]

# Aplicar os ticks e labels no eixo X
plt.xticks(xticks, xtick_labels, rotation=45)

# Exibir o gráfico
plt.savefig("grafico.png")