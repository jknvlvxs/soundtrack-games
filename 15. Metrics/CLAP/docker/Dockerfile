FROM nvcr.io/nvidia/pytorch:24.10-py3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg

# rust compiler for transformers
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# this will ask for Enter, yes and no -> no for automatically initialize conda
# PREFIX=/root/miniconda3
RUN mkdir -p ~/miniconda3 && \
wget https://repo.anaconda.com/miniconda/Miniconda3-py310_25.7.0-2-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh && \
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 && \
rm ~/miniconda3/miniconda.sh

ENV PATH=/root/miniconda3/bin:$PATH

RUN conda init --all

WORKDIR /app

# Installl dependecies
COPY ./requirements.txt ./

RUN /root/miniconda3/bin/pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html

RUN /root/miniconda3/bin/pip install -r requirements.txt && \
    rm requirements.txt

# docker build . -t clap_tune

# docker run \
# --gpus all \
# -d \
# -it \
# --name clap_tune \
# --volume "/home/es119256/vmdb/15. Metrics/CLAP":/app/code \
# --volume /home/es119256/dados/datasets/vmdb:/app/dataset \
# --volume /home/es119256/dados/xps:/app/xps \
# --shm-size=6gb \
# clap_tune

# docker exec -it clap_tune sh