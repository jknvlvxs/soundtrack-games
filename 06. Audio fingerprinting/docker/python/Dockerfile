FROM python:3.7

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg
RUN apt-get -y install portaudio19-dev python3-pyaudio

WORKDIR /app

COPY requirements.txt ./

RUN python3.7 -m pip install --upgrade pip==24.0
RUN python3.7 -m pip install -r requirements.txt

# docker run \
# -d \
# -it \
# --network=vmdb_network \
# --name=dejavu \
# --name dejavu \
# --mount type=bind,source="/home/julio/Área de Trabalho/TCC/SOUNDTRACK-GAMES/6. Audio fingerprinting",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/julio/Área de Trabalho/TCC/datasets/vmdb",target=/app/dataset,bind-propagation=rshared \
# dejavu

# docker run \
# -d \
# -it \
# --network=vmdb_network \
# --name=dejavu \
# --name dejavu \
# --mount type=bind,source="/home/es119256/dejavu-vmdb/6. Audio fingerprinting",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/es119256/datasets/vmdb",target=/app/dataset,bind-propagation=rshared \
# dejavu

# docker exec -it dejavu sh