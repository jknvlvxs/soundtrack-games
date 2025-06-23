import os
import ffmpeg
import pandas as pd
from tqdm import tqdm

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc"
UNMAPPED_DATSET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock-unmapped"

MIN_SOUNDTRACK_SIZE = 8
MIN_VIDEO_SIZE = 10 - 1 # -1 is a tolerance because many gameplay slices have nine dot something seconds of duration

DRY_RUN = True
VERBOSE = False

def get_sdtks_to_unmap(soundtracks_path:str, videos_path:str):
    """
    For each soundctrack in the soundtracks folder
        If the corresponding folder to that soundtrack in the videos folder is empty or non-existent:
            Add to unmapped soundtracks
            Remove folder if empty

        If audio smaller than MIN_SOUNDTRACK_SIZE
            Add to unmapped soundtracks
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
                    tqdm.write(f"Video folder {video_folder_path} was EMPTY, so it was REMOVED")

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
            #tqdm.write(f"Soundtrack {soundtrack_path} wasn't mapped to any video")
            count_unmapped += 1
            unmapped_sdtks.append(soundtrack_path)
            continue

        # If audio smaller than MIN_SOUNDTRACK_SIZE
        try:
            probe = ffmpeg.probe(soundtrack_path)
            sdtk_duration = float(probe['format']['duration'])

            if sdtk_duration < MIN_SOUNDTRACK_SIZE:
                count_unmapped += 1
                # tqdm.write(f"Soundtrack {soundtrack_file}:\nprobe:{sdtk_duration}\n")
                unmapped_sdtks.append(soundtrack_path)
        except Exception as e:
            tqdm.write(f"Error on probing {soundtrack_path}: {e}")

    return unmapped_sdtks, count_unmapped, count_total

def get_videos_to_unmap(videos_path):
    """
        To get the videos outside any soundtrack folder or with duration smaller than MIN_VIDEO_SIZE
    """
    count_total = 0
    count_unmapped = 0
    unmapped_videos:list[str] = []

    for vid_or_folder in sorted(os.listdir(videos_path)):
        video_or_folder_path = os.path.join(videos_path, vid_or_folder)

        if not os.path.isdir(video_or_folder_path):
            #tqdm.write(f"Video {video_or_folder_path} is unmapped")
            count_total += 1
            count_unmapped += 1
            unmapped_videos.append(video_or_folder_path)
            continue

        folder_path = video_or_folder_path

        for video_file in os.listdir(folder_path):
            count_total += 1

            video_file_path = os.path.join(folder_path, video_file)
            try:
                probe = ffmpeg.probe(video_file_path)
                video_duration = float(probe['format']['duration'])

                if video_duration < MIN_VIDEO_SIZE:
                    count_unmapped += 1
                    #tqdm.write(f"Video {video_file_path}:\nprobe:{video_duration}\n")
                    unmapped_videos.append(video_file_path)

            except Exception as e:
                tqdm.write(f"Error on probing {unmapped_videos}: {e}")

    return unmapped_videos, count_unmapped, count_total

def move_unmapped_soundtracks(unmapped_sdtks:list[str]) -> list[str]:
    """
        Moves the unmapped_sdtks to the unmapped dataset following the same structure

        Retuns:
            unmapped_sdtks: list containing paths to folders that became empty aftermoving the unmapped soundtracks
    """
    empty_sdtk_folders:list[str] = []

    for unmapped_sdtk in unmapped_sdtks:
        if not os.path.exists(unmapped_sdtk):
            print("move_unmapped_soundtracks: Skipping:", unmapped_sdtk)
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

        # Check for empty game soundtracks folder
        original_sdtk_folder = os.path.join(DATASET_ROOT, game, 'soundtracks')
        if len(os.listdir(original_sdtk_folder)) == 0:
            if VERBOSE: tqdm.write(f"Soundtracks folder {original_sdtk_folder} is EMPTY")
            empty_sdtk_folders.append(original_sdtk_folder)

    return empty_sdtk_folders

def move_unmapped_videos(unmapped_videos:list[str]) -> tuple[list[str], list[str], list[str]]:
    """
        Move unmapped videos, textual descriptions and csv entries to unmapped dataset 
        according to unmapped_videos and following the same dataset structure

        Retuns:
            A list containing paths to folders or csv files that became empty aftermoving the unmapped data
            the lists follow the order: videos, videos descriptions, csv files
    """
    empty_videos_folders:list[str] = []
    empty_desc_folders:list[str] = []
    empty_csv_files:list[str] = []

    for unmapped_video in unmapped_videos:
        if not os.path.exists(unmapped_video):
            print("move_unmapped_soundtracks: Skipping:", unmapped_video)
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

        # Check for empty game videos
        original_video_folder = os.path.join(DATASET_ROOT, game, 'videos')
        if len(os.listdir(original_video_folder)) == 0:
            if VERBOSE: tqdm.write(f"Video folder {original_video_folder} is EMPTY")
            empty_videos_folders.append(original_video_folder)

        # Move video description file
        desc_orig_folder = os.path.join(DATASET_ROOT, game, 'videos_descriptions')
        desc_dest_folder = os.path.join(UNMAPPED_DATSET_ROOT, game, 'videos_descriptions')
        if not os.path.exists(desc_dest_folder):
            os.makedirs(desc_dest_folder)

        desc_file = video_file.split('.')[0]+'.txt'
        desc_orig_path = os.path.join(desc_orig_folder, desc_file)
        desc_dest_path = os.path.join(desc_dest_folder, desc_file)
        os.rename(desc_orig_path, desc_dest_path)

        # Check for empty videos descriptions folders
        if len(os.listdir(desc_orig_folder)) == 0:
            if VERBOSE: tqdm.write(f"Descriptions folder {desc_orig_folder} is EMPTY")
            empty_desc_folders.append(desc_orig_folder)

        # Move csv entries
        mapping_file = 'mapping_log.csv'
        mapping_orig_path = os.path.join(DATASET_ROOT, game, mapping_file)
        mapping_dest_path = os.path.join(UNMAPPED_DATSET_ROOT, game, mapping_file)

        mapping_df = pd.read_csv(mapping_orig_path)

        mapping_df_entry = mapping_df[mapping_df['video'] == video_file]

        mapping_df = mapping_df.drop(mapping_df_entry.index)
        mapping_df.to_csv(mapping_orig_path)

        if not os.path.exists(mapping_dest_path):
            mapping_df_entry.to_csv(mapping_dest_path)
        else:
            dest_mapping_df = pd.read_csv(mapping_dest_path)
            dest_mapping_df = pd.concat([dest_mapping_df, mapping_df_entry], ignore_index=True)
            dest_mapping_df.to_csv(mapping_dest_path)

        # Check for empty csv files
        if mapping_df.empty:
            if VERBOSE: tqdm.write(f"CSV file {mapping_orig_path} is EMPTY")
            empty_csv_files.append(mapping_orig_path)

    return empty_videos_folders, empty_desc_folders, empty_csv_files

def remove_empty_games(base_dir):
    # TODO:
    # Remove games with either no mapped videos or soundtracks

    # Should be better to check this first and just move the whole folder
    # Because we might move every video and than verify that we need to move all therest too
    # Or move every audio and verify we have to move all the rest
    # for game in tqdm(sorted(os.listdir(base_dir))):
    #     game_path = os.path.join(base_dir, game)
    #     videos_path = os.path.join(game_path, "videos")
    pass

def main(base_dir):
    gb_cnt_ump_s = 0 # global count unmapped soundtracks
    gb_cnt_total_s = 0 # global count total soundtracks
    gb_cnt_ump_v = 0 # global count unmapped videos
    gb_cnt_total_v = 0 # global count total videos

    for game in tqdm(sorted(os.listdir(base_dir))):
        game_path = os.path.join(base_dir, game)
        videos_path = os.path.join(game_path, "videos")
        soundtracks_path = os.path.join(game_path, "soundtracks")

        # Get Soundtracks
        if os.path.isdir(soundtracks_path):
            unmapped_sdtks, cnt_ump_s, cnt_total_s = get_sdtks_to_unmap(soundtracks_path, videos_path)

            if cnt_ump_s == cnt_total_s:
                tqdm.write(f"################ GAME {game} HAVE NO MAPPED SOUNTRACKS {cnt_ump_s} unmapped ###################")

            gb_cnt_ump_s += cnt_ump_s
            gb_cnt_total_s += cnt_total_s

        # Get Videos
        if os.path.isdir(videos_path):
            unmapped_videos, cnt_ump_v, cnt_total_v = get_videos_to_unmap(videos_path)

            if cnt_ump_v == cnt_total_v:
                tqdm.write(f"################ GAME {game} HAVE NO MAPPED VIDEOS {cnt_ump_v} unmapped ###################")

            gb_cnt_ump_v += cnt_ump_v
            gb_cnt_total_v += cnt_total_v

    print(f"{gb_cnt_ump_s} audios of {gb_cnt_total_s}, or {(gb_cnt_ump_s/gb_cnt_total_s)*100}% of the audios, will be UNMAPPED")
    print(f"{gb_cnt_ump_v} videos of {gb_cnt_total_v}, or {(gb_cnt_ump_v/gb_cnt_total_v)*100}% of the videos, will be UNMAPPED")

    move_unmapped_soundtracks(unmapped_sdtks)
    move_unmapped_videos(unmapped_videos)

if __name__ == "__main__":
    if not os.path.exists(UNMAPPED_DATSET_ROOT):
        os.makedirs(UNMAPPED_DATSET_ROOT)

    main(DATASET_ROOT)
