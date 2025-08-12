# Last release of a nvidia container of torch 2.4 since laion-clap depends on Torch 2.1
FROM nvcr.io/nvidia/pytorch:24.07-py3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg

RUN python3 -m pip install laion-clap

WORKDIR /app

# docker build --no-cache . -t laion_clap

# docker run \
# --gpus all \
# -d \
# -it \
# --name laion_clap \
# --volume /home/es119256/vmdb/13.\ CLAP:/app/code \
# --volume /home/es119256/dados/datasets/vmdb_2:/app/dataset \
# --volume /home/es119256/dados/xps:/app/xps \
# laion_clap

# docker exec -it laion_clap sh