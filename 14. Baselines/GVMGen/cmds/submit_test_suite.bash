#!/bin/bash
#SBATCH --job-name=test_suit_gvmgen          # Nome do job
#SBATCH --mail-type=ALL                 # Opções: BEGIN, END, FAIL, ALL, etc.
#SBATCH --mail-user=felipeferreiramarra@gmail.com       # Endereço de e-mail destinatário
#SBATCH --partition=scientific          # Partição
#SBATCH --qos=scientific-qos            # QoS 
#SBATCH --nodes=1                       # Número de nós 1 de 1
#SBATCH --ntasks=1                      # Número de tarefas
#SBATCH --cpus-per-task=8               # CPUs por tarefa 8 de 128 (Max)
#SBATCH --mem=32GB                       # Memória RAM 32GB de 1007GB(Max)
#SBATCH --gres=gpu:1               # Solicitar 1 GPU de 4 (Max)
#SBATCH --time=2-00:00:00               # Tempo máximo (2 dias)
#SBATCH --output=job_%j.out        # Arquivo de saída (%j = job ID)
#SBATCH --error=job_%j.err         # Arquivo de erro

# Carregar módulos necessários
module --force purge
module load GCCcore/12.2.0 
module load CUDA/12.6.0

# Ativar ambiente
source ~/miniconda3_gvmgen/bin/activate
echo "$(conda info --envs)"

# Informações do job
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs alocadas: $CUDA_VISIBLE_DEVICES"
echo "Memória disponível: $(free -h | grep Mem:)"
echo "Limites do processo:"
ulimit -a | egrep 'virtual memory|max resident set|open files'
echo "Iniciado em: $(date)"

# Variáveis de ambiente PyTorch
export AUDIOCRAFT_TEAM=default
export USER=audiocraft_gvmgen
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export OMP_NUM_THREADS=1

export LD_LIBRARY_PATH=$HOME/miniconda3_gvmgen/lib:$LD_LIBRARY_PATH
srun python3 -u /home/es119256/dados/repos/vmdb/14.\ Baselines/GVMGen/test_suite.py --state_dict_bin_folder /home/es119256/dados/xps/audiocraft_gvmgen/xps/524c0212

echo "Memória final: $(free -h | grep Mem:)"
echo "Finalizado em: $(date)"