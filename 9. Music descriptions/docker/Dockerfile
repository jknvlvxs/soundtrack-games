FROM ubuntu

RUN apt-get update && \
    apt-get -y upgrade

RUN apt-get -y install pciutils curl

RUN curl -fsSL https://ollama.com/install.sh | sh

# docker build . -t ollama
# docker run -d -it -v ollama:/root/.ollama -p 11434:11434 --gpus '"device=3"' --network host --name ollama ollama && docker exec ollama ollama serve &
# docker exec -it ollama ollama run deepseek-r1:70b "Hello, how are you?"
# export OLLAMA_ADDRES=127.0.0.1:11434