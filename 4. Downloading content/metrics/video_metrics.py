import os

def contar_arquivos_na_pasta_videos(diretorio):
    # Listar todos os subdiretórios dentro do diretório raiz
    subdiretorios = [os.path.join(diretorio, subdir) for subdir in os.listdir(diretorio) 
                     if os.path.isdir(os.path.join(diretorio, subdir))]
    
    # Ordenar os subdiretórios em ordem alfabética
    subdiretorios.sort()

    # Percorrer cada subdiretório
    for subdir in subdiretorios:
        pasta_videos = os.path.join(subdir, 'videos')
        
        if os.path.isdir(pasta_videos):
            # Contar o número de arquivos dentro da pasta 'videos'
            arquivos = [f for f in os.listdir(pasta_videos) if os.path.isfile(os.path.join(pasta_videos, f))]
            num_arquivos = len(arquivos)
            
            # Extrair o nome do subdiretório (última parte do caminho)
            nome_subdiretorio = os.path.basename(subdir)
            
            # Exibir o nome do subdiretório e o número de arquivos
            print(f"{nome_subdiretorio}, {num_arquivos}")

# Caminho do diretório a ser passado como argumento
contar_arquivos_na_pasta_videos("/media/ufv-ml-hp/Data/vmdb/5. Database/nintendo-snes-spc")
