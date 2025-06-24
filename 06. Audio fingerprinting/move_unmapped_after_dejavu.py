import os
import ffmpeg
import pandas as pd
from tqdm import tqdm

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock"
UNMAPPED_DATSET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock-unmapped"

MIN_SOUNDTRACK_SIZE = 8
MIN_VIDEO_SIZE = 10 - 1 # -1 is a tolerance because many gameplay slices have nine dot something seconds of duration

DRY_RUN = False
VERBOSE = True

def move_videos_out(video_sdtk_path:str):
    """
        When a soundtrack is smaller than MIN_SOUNDTRACK_SIZE, it will be treated as unmapped
        therefore we need to move the videos mapped to it, if any, to the game/videos folder,
        that is, out of the game/videos/sountrack folder

        Args:
            video_sdtk_path: path to the game/videos/sountrack folder
    """
    if os.path.exists(video_sdtk_path):
        dir_list = os.listdir(video_sdtk_path)

        if len(dir_list) > 0:
            videos_folder_path = os.path.abspath(os.path.join(video_sdtk_path, os.pardir)) # game/videos

            for video in dir_list:
                current_vid_path = os.path.join(video_sdtk_path, video)
                tgt_vid_pathj = os.path.join(videos_folder_path, video)

                os.rename(current_vid_path, tgt_vid_pathj)

            os.rmdir(video_sdtk_path)
            if VERBOSE: tqdm.write(f"Video folder {video_sdtk_path} was EMPTY, so it was REMOVED")

def get_sdtks_to_unmap(soundtracks_path:str, videos_path:str):
    """
    For each soundctrack in the soundtracks folder
        If the corresponding folder to that soundtrack in the videos folder is empty or non-existent:
            Add to unmapped soundtracks
            Remove folder if empty

        If audio smaller than MIN_SOUNDTRACK_SIZE
            Add to unmapped soundtracks
            Move videos related to that soundtrack ou to the game/videos/soundtrack folder and remove such folder
    """
    count_total = 0
    count_unmapped = 0
    mapped_sdtks:list[str] = []
    unmapped_sdtks:list[str] = []

    # Get soundtracks mapped to videos and add unmapped to unmapped_sdtks
    for vid_or_folder in sorted(os.listdir(videos_path)):
        video_folder_path = os.path.join(videos_path, vid_or_folder)
        soundtrack_path = os.path.join(soundtracks_path, vid_or_folder+'.mp3')

        if os.path.isdir(video_folder_path):
            if len(os.listdir(video_folder_path)) > 0:
                mapped_sdtks.append(soundtrack_path)
            # If the corresponding folder to that soundtrack in the videos folder is empty or non-existent
            else:
                count_unmapped += 1
                unmapped_sdtks.append(soundtrack_path)

                if DRY_RUN:
                    if VERBOSE: tqdm.write(f"Video folder {video_folder_path} is EMPTY")
                else:
                    os.rmdir(video_folder_path)
                    if VERBOSE: tqdm.write(f"Video folder {video_folder_path} was EMPTY, so it was REMOVED")

    # For each soundtrack
    for soundtrack_file in sorted(os.listdir(soundtracks_path)):
        count_total += 1
        soundtrack_path = os.path.join(soundtracks_path, soundtrack_file)

        # If already unmaped, continue. 
        if soundtrack_path in unmapped_sdtks:
            continue

        # A soundtrack might not even have a folder at the videos folder,
        # so we still need to check if it isn't in the mapped_sdtks
        if soundtrack_path not in mapped_sdtks:
            count_unmapped += 1
            unmapped_sdtks.append(soundtrack_path)
            continue

        # If audio smaller than MIN_SOUNDTRACK_SIZE
        probe = ffmpeg.probe(soundtrack_path)
        sdtk_duration = float(probe['format']['duration'])

        if sdtk_duration < MIN_SOUNDTRACK_SIZE:
            count_unmapped += 1
            unmapped_sdtks.append(soundtrack_path)

            # Move all videos corresponding to that soundtrack out of the game/videos/soundtrack folder
            video_sdtk_path = os.path.join(videos_path, soundtrack_file.split('.')[0])
            if not DRY_RUN: move_videos_out(video_sdtk_path)

    return unmapped_sdtks, count_unmapped, count_total

def get_videos_to_unmap(videos_path:str, unmapped_sdtks:list[str]):
    """
        To get the videos outside any soundtrack folder or with duration smaller than MIN_VIDEO_SIZE
    """
    count_total = 0
    count_unmapped = 0
    cnt_ump_s = 0
    unmapped_videos:list[str] = []

    for vid_or_folder in sorted(os.listdir(videos_path)): # game/videos
        video_or_folder_path = os.path.join(videos_path, vid_or_folder)

        if not os.path.isdir(video_or_folder_path):
            count_total += 1
            count_unmapped += 1
            unmapped_videos.append(video_or_folder_path)
            continue

        folder_path = video_or_folder_path
        for video_file in os.listdir(folder_path): # game/videos/soundtrack
            count_total += 1

            # Since DRY_RUN will not execute move_videos_out
            if DRY_RUN:
                soundtrack_path = os.path.abspath(os.path.join(videos_path, os.pardir, 'soundtracks', vid_or_folder+'.mp3'))
                if soundtrack_path in unmapped_sdtks:
                    count_unmapped += 1
                    unmapped_videos.append(video_file_path)
                    continue

            video_file_path = os.path.join(folder_path, video_file)

            probe = ffmpeg.probe(video_file_path)
            video_duration = float(probe['format']['duration'])

            if video_duration < MIN_VIDEO_SIZE:
                count_unmapped += 1

                # Move video out the soundtrack path
                tgt_video_file_path = os.path.join(videos_path, video_file)
                if not DRY_RUN:
                    os.rename(video_file_path, tgt_video_file_path)

                    if len(os.listdir(folder_path)) == 0:
                        cnt_ump_s += 1
                        os.rmdir(folder_path)

                        sdtk_path = os.path.abspath(os.path.join(videos_path, os.pardir))
                        sdtk_path = os.path.join(sdtk_path, 'soundtracks', vid_or_folder+'.mp3')
                        unmapped_sdtks.append(sdtk_path)

                unmapped_videos.append(tgt_video_file_path)

    return unmapped_videos, unmapped_sdtks, count_unmapped, count_total, cnt_ump_s

def move_unmapped_soundtracks(unmapped_sdtks:list[str]):
    """
        Moves the unmapped_sdtks to the unmapped dataset following the same structure
    """
    for unmapped_sdtk in unmapped_sdtks:
        if not os.path.exists(unmapped_sdtk):
            if VERBOSE: tqdm.write(f"move_unmapped_soundtracks: Skipping: {unmapped_sdtk}")
            continue

        splited_sdtk = unmapped_sdtk.split("/")
        sdtk_file = splited_sdtk[-1]
        game = splited_sdtk[-3]

        # Move soundtrack mp3 file
        sdtk_dest_folder = os.path.join(UNMAPPED_DATSET_ROOT, game, 'soundtracks')
        if not os.path.exists(sdtk_dest_folder):
            os.makedirs(sdtk_dest_folder)

        sdtk_dest_path = os.path.join(sdtk_dest_folder, sdtk_file)
        os.rename(unmapped_sdtk, sdtk_dest_path)

def move_unmapped_videos(unmapped_videos:list[str]):
    """
        Move unmapped videos, textual descriptions and csv entries to unmapped dataset 
        according to unmapped_videos and following the same dataset structure
    """
    for unmapped_video in unmapped_videos:
        if not os.path.exists(unmapped_video):
            if VERBOSE: tqdm.write(f"move_unmapped_videos: Skipping: {unmapped_video}")
            continue

        splited_video = unmapped_video.split("/")
        video_file = splited_video[-1]
        game = splited_video[-3]

        # Move video mp4 file
        vid_dest_folder = os.path.join(UNMAPPED_DATSET_ROOT, game, 'videos')
        if not os.path.exists(vid_dest_folder):
            os.makedirs(vid_dest_folder)

        vid_dest_path = os.path.join(vid_dest_folder, video_file)
        os.rename(unmapped_video, vid_dest_path)

        # Move video description file
        desc_orig_folder = os.path.join(DATASET_ROOT, game, 'videos_descriptions')
        desc_dest_folder = os.path.join(UNMAPPED_DATSET_ROOT, game, 'videos_descriptions')
        if not os.path.exists(desc_dest_folder):
            os.makedirs(desc_dest_folder)

        desc_file = video_file.split('.')[0]+'.txt'
        desc_orig_path = os.path.join(desc_orig_folder, desc_file)
        desc_dest_path = os.path.join(desc_dest_folder, desc_file)
        os.rename(desc_orig_path, desc_dest_path)

        # Move csv entries
        mapping_file = 'mapping_log.csv'
        mapping_orig_path = os.path.join(DATASET_ROOT, game, mapping_file)
        mapping_dest_path = os.path.join(UNMAPPED_DATSET_ROOT, game, mapping_file)

        mapping_df = pd.read_csv(mapping_orig_path)

        mapping_df_entry = mapping_df[mapping_df['video'] == video_file]
        mapping_df = mapping_df.drop(mapping_df_entry.index)

        mapping_df.to_csv(mapping_orig_path, index=False)

        if not os.path.exists(mapping_dest_path):
            mapping_df_entry.to_csv(mapping_dest_path, index=False)
        else:
            dest_mapping_df = pd.read_csv(mapping_dest_path)
            dest_mapping_df = pd.concat([dest_mapping_df, mapping_df_entry], ignore_index=True)
            dest_mapping_df.to_csv(mapping_dest_path, index=False)

def main(base_dir):
    gb_cnt_ump_s = 0 # global count unmapped soundtracks
    gb_cnt_total_s = 0 # global count total soundtracks
    gb_cnt_ump_v = 0 # global count unmapped videos
    gb_cnt_total_v = 0 # global count total videos
    unmapped_games = []

    for game in tqdm(sorted(os.listdir(base_dir))):
        game_path = os.path.join(base_dir, game)
        videos_path = os.path.join(game_path, "videos")
        soundtracks_path = os.path.join(game_path, "soundtracks")

        # Get Soundtracks
        unmapped_sdtks, cnt_ump_s, cnt_total_s = get_sdtks_to_unmap(soundtracks_path, videos_path)

        gb_cnt_ump_s += cnt_ump_s
        gb_cnt_total_s += cnt_total_s

        if cnt_ump_s == cnt_total_s:
            tqdm.write(f"################ GAME {game} HAVE NO MAPPED SOUNTRACKS {cnt_ump_s} unmapped ###################")

            if not DRY_RUN:
                tqdm.write(f"################ MOVING THE WHOLE GAME {game} ###################\n")
                tgt_game_path = os.path.join(UNMAPPED_DATSET_ROOT, game)
                os.rename(game_path, tgt_game_path)
                unmapped_games.append(game)
                continue

        # Get Videos
        unmapped_videos, unmapped_sdtks, cnt_ump_v, cnt_total_v, cnt_ump_s = get_videos_to_unmap(videos_path, unmapped_sdtks)

        gb_cnt_ump_v += cnt_ump_v
        gb_cnt_total_v += cnt_total_v

        gb_cnt_ump_s += cnt_ump_s

        if cnt_ump_v == cnt_total_v:
            tqdm.write(f"################ GAME {game} HAVE NO MAPPED VIDEOS {cnt_ump_v} unmapped ###################\n")

            if not DRY_RUN:
                tqdm.write(f"################ MOVING THE WHOLE GAME {game} ###################\n") # belive me, this case exists
                tgt_game_path = os.path.join(UNMAPPED_DATSET_ROOT, game)
                os.rename(game_path, tgt_game_path)
                unmapped_games.append(game)
                continue

        # Unmap soundtracks and videos
        if not DRY_RUN:
            move_unmapped_soundtracks(unmapped_sdtks)
            move_unmapped_videos(unmapped_videos)

    print(f"{gb_cnt_ump_s} audios of {gb_cnt_total_s}, or {(gb_cnt_ump_s/gb_cnt_total_s)*100}% of the audios, will be UNMAPPED")
    print(f"{gb_cnt_ump_v} videos of {gb_cnt_total_v}, or {(gb_cnt_ump_v/gb_cnt_total_v)*100}% of the videos, will be UNMAPPED")
    print(f"Unmaped games:\n{unmapped_games}")

if __name__ == "__main__":
    if not DRY_RUN and not os.path.exists(UNMAPPED_DATSET_ROOT):
        os.makedirs(UNMAPPED_DATSET_ROOT)

    main(DATASET_ROOT)
