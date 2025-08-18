FROM ubuntu

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install pciutils curl

RUN curl -fsSL https://ollama.com/install.sh | sh

# docker build . --no-cache -t ollama
# docker run -d -it -v "/home/es119256/dados/ollama_cache":/root/.ollama -p 11434:11434 --gpus '"device=0,1"' --shm-size=6gb --network host -e OLLAMA_GPU_OVERHEAD=536870912 -e OLLAMA_NUM_PARALLEL=1 -e OLLAMA_FLASH_ATTENTION=1  --name ollama ollama
# docker exec ollama ollama serve
# export OLLAMA_ADDRES=127.0.0.1:11434
# docker exec -it ollama ollama run llama4:scout "Hello, how are you?"