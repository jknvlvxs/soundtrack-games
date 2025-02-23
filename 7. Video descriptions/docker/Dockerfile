FROM nvcr.io/nvidia/pytorch:25.01-py3

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install ffmpeg

WORKDIR /app

COPY video_desc_req.txt ./

# rust compiler for transformers
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN python3 -m pip install --upgrade pip==25.0.1
RUN python3 -m pip install --upgrade setuptools==75.8.0
RUN python3 -m pip install --upgrade wheel==0.45.1

RUN python3 -m pip install flash-attn==2.7.4.post1 --no-build-isolation
RUN python3 -m pip install decord==0.6.0
RUN python3 -m pip install -r video_desc_req.txt

# docker run \
# --gpus all \
# -d \
# -it \
# --name=videollama3 \
# --name videollama3 \
# --mount type=bind,source="/home/es119256/vmdb/7. Video descriptions",target=/app/code,bind-propagation=rshared \
# --mount type=bind,source="/home/es119256/datasets/vmdb/",target=/app/dataset,bind-propagation=rshared \
# videollama3

# docker exec -it videollama3 sh