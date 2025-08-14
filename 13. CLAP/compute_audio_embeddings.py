###################################################################################################################################
# Pre-compute LAION-CLAP embeddings for every audio in the dataset
# Expects clap checkpoint at /app/xps/clap/music_audioset_epoch_15_esc_90.14.pt
# Same checkpoint and configs as MusicGen https://github.com/facebookresearch/audiocraft/blob/main/docs/METRICS.md#text-consistency
###################################################################################################################################
import os

from tqdm import tqdm

import torch
import torchaudio
import laion_clap

DATASET_ROOT = "/app/dataset/nintendo-snes-spc"
MODEL_PATH = '/app/xps/clap/music_audioset_epoch_15_esc_90.14.pt'

def get_audios_paths(dataset_folder):
    files = []
    skiped = 0
    for game_folder in sorted(os.listdir(dataset_folder)):
        audios_folder = os.path.join(dataset_folder, game_folder, 'soundtracks')
        audios_emb_folder = os.path.join(dataset_folder, game_folder, 'soundtracks_clap')

        if os.path.exists(audios_folder):
            for audio_file in sorted(os.listdir(audios_folder)):
                audio_file_path = os.path.join(audios_folder, audio_file)
                audios_emb_file_path = os.path.join(audios_emb_folder, audio_file[:-3]+'pt')

                if not os.path.exists(audios_emb_file_path):
                    files.append((audio_file_path, audios_emb_file_path))
                else:
                    print(f"SKIPING {audio_file_path}")
                    skiped += 1

    print(f"SKIPED {skiped}")

    return files

def mono_and_resample(audio:torch.Tensor, orig_freq:int, new_freq:int):
    audio = torch.mean(audio, dim=0, keepdim=True)

    resample = torchaudio.transforms.Resample(orig_freq=orig_freq, new_freq=new_freq)
    audio = resample(audio)

    return audio

def main():
    model = laion_clap.CLAP_Module(enable_fusion=False, amodel='HTSAT-base')
    model.load_ckpt(MODEL_PATH)
    model.eval()

    audios_files = get_audios_paths(DATASET_ROOT)

    for audio_path, audio_emb_path in tqdm(audios_files):
        audio, sr = torchaudio.load(audio_path)
        audio = mono_and_resample(audio, orig_freq=sr, new_freq=48_000)

        audio_embeddings = model.get_audio_embedding_from_data(audio, use_tensor=True).squeeze()

        embeddings_folder = os.path.abspath(os.path.join(audio_emb_path, os.pardir))
        if not os.path.exists(embeddings_folder):
            os.makedirs(embeddings_folder)

        torch.save(audio_embeddings, audio_emb_path)

if __name__ == "__main__":
    main()