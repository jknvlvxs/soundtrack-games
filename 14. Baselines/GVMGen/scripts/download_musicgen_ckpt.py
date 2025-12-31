from huggingface_hub import snapshot_download

# Downlaod MusicGeen snapshot
repo_path = snapshot_download(repo_id="facebook/musicgen-medium", local_dir='/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen/checkpoints')
print(f"Downloaded repository to: {repo_path}")