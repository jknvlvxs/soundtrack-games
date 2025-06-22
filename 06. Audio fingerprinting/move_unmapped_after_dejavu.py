import os
import ffmpeg
from tqdm import tqdm

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock"
UNMAPPED_DATSET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock-unmapped"

MIN_SOUNDTRACK_SIZE = 8
MIN_VIDEO_SIZE = 10 - 1 # -1 is a tolerance because many gameplay slices have nine dot something seconds of duration

DRY_RUN = True

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
                    tqdm.write(f"Video folder {video_folder_path} is EMPTY")
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

def move_unmapped_soundtracks(unmapped_sdtks:list[str]):
    # TODO:
    # Just move them to the unmapped dataset following the same structure
    # Check for empty folders
    pass

def move_unmapped_videos(unmapped_videos:list[str]):
    # TODO:
    # Move the videos, textual descriptions and csv entries to unmapped dataset
    # Check for empty folders
    pass

def remove_empty_games():
    # TODO:
    # Remove games with either no videos or soundtracks
    # If there is one of them (videos or soundtracks) move to the unmapped dataset 
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

            gb_cnt_ump_s += cnt_ump_s
            gb_cnt_total_s += cnt_total_s

        # Get Videos
        if os.path.isdir(videos_path):
            unmapped_videos, cnt_small_v, cnt_total_v = get_videos_to_unmap(videos_path)

            gb_cnt_ump_v += cnt_small_v
            gb_cnt_total_v += cnt_total_v

        print()

    print(f"{gb_cnt_ump_s} audios of {gb_cnt_total_s}, or {(gb_cnt_ump_s/gb_cnt_total_s)*100}% of the audios, will be UNMAPPED")
    print(f"{gb_cnt_ump_v} videos of {gb_cnt_total_v}, or {(gb_cnt_ump_v/gb_cnt_total_v)*100}% of the videos, will be UNMAPPED")

    move_unmapped_soundtracks(unmapped_sdtks)
    move_unmapped_videos(unmapped_videos)
    remove_empty_games()

if __name__ == "__main__":
    if not os.path.exists(UNMAPPED_DATSET_ROOT):
        os.makedirs(UNMAPPED_DATSET_ROOT)

    main(DATASET_ROOT)
