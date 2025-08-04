# Remove videos with no descriptions
# The empty description mean that there was and error reading the video, so it should be removed
# Those usually are corrupted files or videos with just one frame (the last slice of the gameplay video, that didn't get to 10s)
import os
from copy import deepcopy

GEN_EVERY = 1
ROOT = '/app/dataset/nintendo-snes-spc'
DESC_FOLDER = 'videos_descriptions_mg' # or videos_descriptions

def get_videos_paths(dataset_folder):
    files = []
    skiped = 0 
    for game_folder in sorted(os.listdir(dataset_folder)):
        videos_folder = os.path.join(dataset_folder, game_folder, 'videos')
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, DESC_FOLDER)

        count = 0
        videos_in_folder = [] # to get the videos if video_or_folder_path is a folder
        for video_or_folder in os.listdir(videos_folder):
            # If it isn't a video, it will be a folder of videos with the name of the soundtrack identified in those videos
            video_or_folder_path = os.path.join(videos_folder, video_or_folder)

            if os.path.isdir(video_or_folder_path):
                for video_in_folder in os.listdir(video_or_folder_path):
                    video_in_folder_path = os.path.join(video_or_folder_path, video_in_folder)
                    result_txt_path = os.path.join(videos_descriptions_folder, video_in_folder)[:-3]+"txt"

                    videos_in_folder.append((video_in_folder_path, result_txt_path))
            else:
                result_txt_path = os.path.join(videos_descriptions_folder, video_or_folder)[:-3]+"txt"
                videos_in_folder.append((video_or_folder_path, result_txt_path))

        # Sort the videos
        sort_videos_in_folder = deepcopy(videos_in_folder)
        for idx in range(len(sort_videos_in_folder)):
            sort_videos_in_folder[idx] = sort_videos_in_folder[idx][0].split('/')[-1]

        videos_in_folder = [val for _, val in sorted(zip(sort_videos_in_folder, videos_in_folder))]

        # Select with GEN_EVERY
        for video_path_tuple in videos_in_folder:
            video_path, result_txt_path = video_path_tuple

            if count % GEN_EVERY == 0:
                if os.path.exists(result_txt_path):
                    #print(f"Skiped {video_path.split('/')[-1]}")
                    skiped+=1
                else:
                    files.append((video_path, result_txt_path))

            count+=1

    #g_loger.warning(f"SKIPED {skiped}")

    return files

def eliminate_videos_w_no_dec(vide_desc_pairs):
    videos_folders = []

    for video_path, description_path in vide_desc_pairs:
        video_folder = os.path.abspath(os.path.join(video_path, os.path.pardir))
        video_exists = os.path.exists(video_path)
        description_dont = not os.path.exists(description_path)

        if video_exists and description_dont:
            videos_folders.append(video_folder)

            print(f"removing video {video_path}")
            print(f"since desc: {description_path} dont exist")
            print()

            #os.remove(video_path) #TODO: remove if you really want to execute

    return videos_folders

def elminate_no_video_games():
    for game_folder in sorted(os.listdir(ROOT)):
        videos_folder = os.path.join(ROOT, game_folder, 'videos')

        if len(os.listdir(videos_folder)) == 0:
            #TODO: If you want to, you can eliminate the whole game, but that woudnt make much sence if you want to use the audios
            print(videos_folder)
            print()

if __name__ == "__main__":
    vide_desc_pairs = get_videos_paths(ROOT)
    processed_videos_folders = eliminate_videos_w_no_dec(vide_desc_pairs)
    print("\n#################################################\n")
    elminate_no_video_games()

# for game_folder in sorted(os.listdir(ROOT)):
#     videos_folder = os.path.join(ROOT, game_folder, 'videos')
#     videos_descriptions_folder = os.path.join(ROOT, game_folder, DESC_FOLDER)

#     if os.path.exists(videos_descriptions_folder):
#         for description_file in sorted(os.listdir(videos_descriptions_folder)):

#             description_path = os.path.join(videos_descriptions_folder, description_file)
#             with open(description_path, mode='r') as f:
#                 description_text = f.read()
#                 if description_text == '':
#                     #os.remove(description_path)
#                     print(description_path)