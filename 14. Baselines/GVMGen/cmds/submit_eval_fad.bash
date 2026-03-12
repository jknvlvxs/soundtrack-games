#!/bin/bash
#SBATCH --job-name=tune_gvmgen          # Nome do job
#SBATCH --mail-type=ALL                 # Opções: BEGIN, END, FAIL, ALL, etc.
#SBATCH --mail-user=felipe.marra@ufv.br       # Endereço de e-mail destinatário
#SBATCH --partition=scientific          # Partição
#SBATCH --qos=scientific-qos            # QoS 
#SBATCH --nodes=1                       # Número de nós 1 de 1
#SBATCH --ntasks=1                      # Número de tarefas
#SBATCH --cpus-per-task=16               # CPUs por tarefa 8 de 128 (Max)
#SBATCH --mem=128G                       # Memória RAM 32GB de 1007GB(Max)
#SBATCH --gres=gpu:1               # Solicitar 1 GPU de 4 (Max)
#SBATCH --time=2-00:00:00               # Tempo máximo (2 dias)
#SBATCH --output=job_%j.out        # Arquivo de saída (%j = job ID)
#SBATCH --error=job_%j.err         # Arquivo de erro

# Carregar módulos necessários
module --force purge
module load GCCcore/12.2.0 
module load CUDA/12.6.0
module load Apptainer/1.2.2

# Informações do job
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs alocadas: $CUDA_VISIBLE_DEVICES"
echo "Memória disponível: $(free -h | grep Mem:)"
echo "Limites do processo:"
ulimit -a | egrep 'virtual memory|max resident set|open files'
echo "Iniciado em: $(date)"

# Bind host folder to the container. In this way I'm only working on the host files
# The container will be just like an isoladed env to run the code
export APPTAINER_BIND="/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen:/app/code,/home/es119256/dados/xps:/app/xps,/home/es119256/dados/datasets/vmdb_3:/app/dataset"


singularity exec --nv "/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen/containers/gvmgen_singularity" \
    bash -c """
set -x
set -eo pipefail

source /root/miniconda3/bin/activate
conda activate fad

export PYTHONPATH="/app/xps/fad/google-research"

/home/es119256/.conda/envs/fad/bin/python -m frechet_audio_distance.create_embeddings_main --model_ckpt /app/xps/fad/vggish_model.ckpt --input_files /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/files_tests.cvs --stats /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/stats_tests --batch_size 1
/home/es119256/.conda/envs/fad/bin/python -m frechet_audio_distance.create_embeddings_main --model_ckpt /app/xps/fad/vggish_model.ckpt --input_files /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/files_background.cvs --stats /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/stats_background --batch_size 1
/home/es119256/.conda/envs/fad/bin/python -m frechet_audio_distance.compute_fad --test_stats /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/stats_tests --background_stats /app/xps/audiocraft_gvmgen/xps/710f6de3/fad/stats_background
"""

echo "Memória final: $(free -h | grep Mem:)"
echo "Finalizado em: $(date)"