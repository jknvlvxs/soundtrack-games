###################################################################################################################################
# Pre-compute LAION-CLAP embeddings for every music caption in the dataset
# Expects clap checkpoint at /app/xps/clap/music_audioset_epoch_15_esc_90.14.pt
# Same checkpoint and configs as MusicGen https://github.com/facebookresearch/audiocraft/blob/main/docs/METRICS.md#text-consistency
###################################################################################################################################
import os
import json
import typing as tp

from tqdm import tqdm

import torch
import laion_clap

from transformers import RobertaTokenizer  # type: ignore

DATASET_ROOT = "/home/es119256/dados/datasets/mock/nintendo-snes-spc"
MODEL_PATH = '/home/es119256/dados/xps/clap/music_audioset_epoch_15_esc_90.14.pt'

def get_caps_paths(dataset_folder):
    files = []
    skiped = 0
    for game_folder in sorted(os.listdir(dataset_folder)):
        music_caps_folder = os.path.join(dataset_folder, game_folder, 'music_caps')
        music_caps_emb_folder = os.path.join(dataset_folder, game_folder, 'music_caps_clap')
        audios_emb_folder = os.path.join(dataset_folder, game_folder, 'soundtracks_clap')

        for music_caps_file in sorted(os.listdir(music_caps_folder)):
            music_caps_path = os.path.join(music_caps_folder, music_caps_file)
            music_caps_emb_path = os.path.join(music_caps_emb_folder, music_caps_file[:-4]+'pt')
            audios_emb_emb_path = os.path.join(audios_emb_folder, music_caps_file[:-4]+'pt')

            if not os.path.exists(music_caps_emb_path):
                files.append((music_caps_path, music_caps_emb_path, audios_emb_emb_path))
            else:
                print(f"SKIPING {music_caps_path}")
                skiped += 1

    print(f"SKIPED {skiped}")

    return files

def get_caps_from_path(music_caps_path) -> list[str]:
    caps:list[str] = []

    with open(music_caps_path, 'r') as f:
        json_file:dict[int, dict[str,str]] = json.load(f)

        for _, value in json_file.items():
            caps.append(value['text'])

    return caps

def main():
    model = laion_clap.CLAP_Module(enable_fusion=False, amodel='HTSAT-base')
    model.load_ckpt(MODEL_PATH)
    model.eval()

    tokenize = RobertaTokenizer.from_pretrained('roberta-base')

    def _tokenizer(texts: tp.Union[str, tp.List[str]]) -> dict:
        # we use the default params from CLAP module here as well
        return tokenize(texts, padding="max_length", truncation=True, max_length=77, return_tensors="pt")

    caps_files = get_caps_paths(DATASET_ROOT)

    for music_caps_path, music_caps_emb_path, audio_emb_path in tqdm(caps_files):
        caps = get_caps_from_path(music_caps_path)
        #print(caps)

        with torch.no_grad():
            music_caps_embs:torch.Tensor = model.get_text_embedding(caps, tokenizer=_tokenizer, use_tensor=True)
            #print('music_caps_embs.shape', music_caps_embs.shape)

            audio_emb = torch.load(audio_emb_path)
            #print('audio_emb.shape', audio_emb.shape, music_caps_embs.shape[0])
            audio_emb = audio_emb.unsqueeze(0).repeat(music_caps_embs.shape[0], 1)
            #print('audio_emb.shape', audio_emb.shape)

            cosine_sim = torch.nn.functional.cosine_similarity(audio_emb, music_caps_embs, dim=1, eps=1e-8)

            #print(cosine_sim.shape)
            cosine_sim_std = cosine_sim.std(0)
            cosine_sim_mean = cosine_sim.mean(0)
            #print(music_caps_embs.shape)
            tqdm.write(f"{cosine_sim_mean}+-{cosine_sim_std}")

            #music_caps_embs = music_caps_embs.squeeze().detach().cpu()

        # embeddings_folder = os.path.abspath(os.path.join(music_caps_emb_path, os.pardir))
        # if not os.path.exists(embeddings_folder):
        #     os.makedirs(embeddings_folder)

        #torch.save(audio_embeddings, audio_emb_path)

if __name__ == "__main__":
    main()