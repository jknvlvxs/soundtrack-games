FROM ubuntu

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install pciutils curl

RUN curl -fsSL https://ollama.com/install.sh | sh

# docker build . -t ollama
# docker run -d -it -v ollama:/root/.ollama -p 11434:11434 --gpus '"device=2,3,4"' --network host -e OLLAMA_MAX_LOADED_MODELS=5 -e OLLAMA_FLASH_ATTENTION=1 -e OLLAMA_NUM_PARALLEL=1 --name ollama ollama
# docker exec ollama ollama serve
# export OLLAMA_ADDRES=127.0.0.1:11434
# docker exec -it ollama ollama run deepseek-r1:70b "Hello, how are you?"