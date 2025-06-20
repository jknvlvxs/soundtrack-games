import os
import ffmpeg
from tqdm import tqdm

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

DRY_RUN = True

def main(base_dir):
    count_small = 0
    count_total = 0

    for game in tqdm(sorted(os.listdir(base_dir))):
        game_path = os.path.join(base_dir, game)
        soundtracks_path = os.path.join(game_path, "soundtracks")

        if os.path.isdir(soundtracks_path):
            for soundtrack_file in os.listdir(soundtracks_path):
                #print(arquivo)
                count_total += 1
                file_path = os.path.join(soundtracks_path, soundtrack_file)
                try:
                    probe = ffmpeg.probe(file_path)
                    probe_duration = float(probe['format']['duration'])

                    if probe_duration < 8:
                        count_small += 1
                        #print(f"{game}/soundtracks/{soundtrack_file}:\nprobe:{probe_duration}\n")

                        if not DRY_RUN:
                            os.remove(file_path)
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")

    print(f"REMOVED {count_small} audios of {count_total}, or {(count_small/count_total)*100}% of the audios")

if __name__ == "__main__":
    main(DATASET_ROOT)
