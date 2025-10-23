FROM continuumio/miniconda3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get install -y build-essential wget libsndfile-dev libgl1-mesa-glx

# CUDA 
# Debian 12.x (x ≤ 12) 6.1.148-1 12.2.0 2.36

WORKDIR /app

COPY ./environment.yml .
COPY ./setup.py .
COPY ./requirements.txt .

# Create sonique env
RUN conda env create -f ./environment.yml

# # Activate sonique env
# ENV PATH=/root/miniconda3/envs/sonique/bin:$PATH
# RUN echo "source activate sonique" > ~/.bashrc

# #RUN conda install "ffmpeg<5" -c conda-forge

RUN /opt/conda/envs/sonique/bin/python3 -m pip install --upgrade pip

RUN /opt/conda/envs/sonique/bin/python3 -m pip install setuptools

RUN /opt/conda/envs/sonique/bin/python3 -m pip install .

RUN rm ./environment.yml
RUN rm ./setup.py
RUN rm ./requirements.txt

# docker build . -t sonique

# docker run \
# --gpus all \
# -d \
# -it \
# --name sonique \
# --volume "/home/es119256/vmdb/14. Baselines/sonique":/app/code \
# --volume /home/es119256/dados/datasets/vmdb:/app/dataset \
# --volume /home/es119256/dados/xps:/app/xps \
# --shm-size=6gb \
# sonique

# docker exec -it sonique sh

# conda activate sonique
# Crate link to ckpts folder
# ln -s /app/xps/sonique/original/ckpts /app/code/