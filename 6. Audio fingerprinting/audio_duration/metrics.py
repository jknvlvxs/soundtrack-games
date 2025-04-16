import json
import numpy as np

# Carregar os dados do JSON
with open("durations.json", "r") as f:
    duracoes = json.load(f)

duracoes = np.sort(np.array(duracoes))  # Converter para NumPy array

# Definir estatísticas
media = np.mean(duracoes)

# Printar estatísticas
print(f"Tamanho: {len(duracoes)} arquivos .mp3")
print(f"Média: {media} de duração em segundos")
print(f"5 menores durações: {duracoes[:5]}")
print(f"5 maiores durações: {duracoes[-5:]}")
print(f"Durações maiores que 350 segundos: {len(duracoes[duracoes > 350])}")