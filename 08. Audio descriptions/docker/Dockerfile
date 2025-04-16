FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install wget curl git
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install ffmpeg libsndfile1 libsndfile1-dev

WORKDIR /app

COPY audio_desc_req.txt ./

# Essentia needs python 3.11
# Other requirements need 3.9, but I building them from source solves it
RUN apt install software-properties-common -y && \
    add-apt-repository 'ppa:deadsnakes/ppa' && \
    apt update && \
    apt-get -y install python3.11 python3.11-distutils && \
    apt install -y python3-pip

RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install --upgrade wheel

RUN apt-get -y install portaudio19-dev python3-pyaudio

RUN python3 -m pip install numpy

RUN python3 -m pip install -r audio_desc_req.txt

#TODO: the next RUN works if executed inside the container after it is running, 
# but for some reason installing it here in the Dockerfile dont work 
RUN git clone --recursive https://github.com/FelipeMarra/madmom &&\
    cd madmom &&\
    git reset --hard 82b9118 && \
    python3 setup.py develop --user

# docker run \
# --gpus all \
# -d \
# -it \
# --name audio_descriptions \
# --mount type=bind,source="/home/es119256/vmdb/8. Audio descriptions",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/es119256/datasets/vmdb/",target=/app/dataset,bind-propagation=rshared \
# audio_descriptions

# docker exec -it audio_descriptions sh