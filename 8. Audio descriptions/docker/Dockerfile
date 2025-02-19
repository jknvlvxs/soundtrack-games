FROM nvcr.io/nvidia/pytorch:25.01-py3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg

WORKDIR /app

COPY audio_desc_req.txt ./

RUN python3 -m pip install --upgrade pip==25.0.1
RUN python3 -m pip install --upgrade setuptools==75.8.0
RUN python3 -m pip install --upgrade wheel==0.45.1

RUN apt-get -y install portaudio19-dev python3-pyaudio
#TODO: the next RUN works if the commands are executed inside the container after it is running, 
# but for some reason installing it here in the Dockerfile dont work 
RUN git clone --recursive https://github.com/CPJKU/madmom.git &&\
    cd madmom &&\
    git reset --hard 27f032e && \
    python setup.py develop --user
RUN python3 -m pip install -r audio_desc_req.txt

# docker run \
# --gpus all \
# -d \
# -it \
# --name audio_process \
# --mount type=bind,source="/home/es119256/vmdb/8. Audio descriptions",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/es119256/datasets/vmdb/",target=/app/dataset,bind-propagation=rshared \
# audio_process

# docker exec -it audio_process sh