FROM python:3.7

RUN apt-get update && \
    apt-get -y upgrade

WORKDIR /app

COPY requirements.txt ./

RUN python3.7 -m pip install --upgrade pip==24.0
RUN python3.7 -m pip install -r requirements.txt

# docker build -t vmdb .

# docker run \
# -d \
# -it \
# --name vmdb \
# --mount type=bind,source="/home/julio/Área de Trabalho/TCC/SOUNDTRACK-GAMES/11. Split dataset",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/julio/Área de Trabalho/TCC/datasets/vmdb",target=/app/dataset,bind-propagation=rshared \
# vmdb

# docker run \
# -d \
# -it \
# --name vmdb \
# --mount type=bind,source="/home/es119256/dejavu-vmdb/11. Split dataset",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/es119256/dados/datasets/vmdb",target=/app/dataset,bind-propagation=rshared \
# vmdb

# docker exec -it vmdb sh