from huggingface_hub import snapshot_download

# Downlaod MusicGeen snapshot
repo_path = snapshot_download(repo_id="facebook/musicgen-small", local_dir='/app/code/checkpoints')
print(f"Downloaded repository to: {repo_path}")