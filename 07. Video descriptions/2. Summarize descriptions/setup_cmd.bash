# Setup the env and container
# Execute this from the folder that contain this file
python3 -m venv env
source env/bin/activate

# rust compiler for transformers
curl https://sh.rustup.rs -sSf | bash -s -- -y
export PATH="/root/.cargo/bin:${PATH}"

python3 -m pip install -r requirements.txt

cd docker
docker build . --no-cache -t ollama
# The volume path below should be the path were one wants to download ollama models
docker run -d -it -v "/home/es119256/dados/ollama_cache":/root/.ollama -p 11434:11434 --gpus '"device=0,1"' --network host -e OLLAMA_NUM_PARALLEL=30 -e OLLAMA_FLASH_ATTENTION=1  --name ollama ollama
docker exec ollama ollama serve # gotta exec a ctr+C here, maybe using & at the end will avoid this
export OLLAMA_ADDRES=127.0.0.1:11434
docker exec -it ollama ollama run llama4:maverick "Hello, how are you?"