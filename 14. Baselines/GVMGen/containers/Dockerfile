# Last release of a nvidia container of torch 2.4 since laion-clap depends on Torch 2.1
FROM nvcr.io/nvidia/pytorch:23.05-py3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg

# this will ask for Enter, yes and no -> no for automatically initialize conda
# PREFIX=/root/miniconda3
RUN mkdir -p ~/miniconda3 && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-py39_25.3.1-1-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh && \
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 && \
    rm ~/miniconda3/miniconda.sh

ENV PATH=/root/miniconda3/bin:$PATH

RUN conda init --all

WORKDIR /app

RUN conda install av==11.0.0 -c conda-forge && \
/root/miniconda3/bin/pip install 'torch==2.1.0'

COPY ./requirements.txt ./

RUN /root/miniconda3/bin/pip install -r requirements.txt && \
    rm requirements.txt

# docker build . -t gvm_gen

# docker run \
# --gpus all \
# -d \
# -it \
# --name gvm_gen \
# --volume "/home/es119256/vmdb/14. Baselines/GVMGen":/app/code \
# --volume /home/es119256/dados/datasets/vmdb:/app/dataset \
# --volume /home/es119256/dados/xps:/app/xps \
# --shm-size=6gb \
# gvm_gen

# docker exec -it gvm_gen sh