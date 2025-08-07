docker build . --no-cache -t ollama

docker run -d -it -v ollama:/root/.ollama -p 11434:11434 --gpus '"device=0, 1"' --network host -e OLLAMA_NUM_PARALLEL=15 -e OLLAMA_FLASH_ATTENTION=1  --name ollama ollama

# docker run -d -it -v ollama:/root/.ollama -p 11434:11434 --gpus '"device=2"' --network host -e OLLAMA_FLASH_ATTENTION=1  --name ollama ollama

docker exec ollama ollama serve &
export OLLAMA_ADDRES=127.0.0.1:11434
docker exec -it ollama ollama run deepseek-r1:70b "Hello, how are you?"