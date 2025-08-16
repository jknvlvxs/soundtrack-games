# Delete the audio embeddings folders
import os
import shutil

DATASET_ROOT = "/app/dataset/nintendo-snes-spc"

def remove_audio_embs(dataset_folder=DATASET_ROOT):
    for game_folder in sorted(os.listdir(dataset_folder)):
        audios_emb_folder = os.path.join(dataset_folder, game_folder, 'soundtracks_clap')

        if os.path.exists(audios_emb_folder):
            print(audios_emb_folder)
            shutil.rmtree(audios_emb_folder)

if __name__ == "__main__":
    remove_audio_embs()