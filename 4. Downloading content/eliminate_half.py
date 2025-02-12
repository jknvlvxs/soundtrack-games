import os
ROOT = '/media/ufv-ml-hp/Data/vmdb/5. Database/nintendo-snes-spc'

def eliminate_half():
    games_folders = sorted(os.listdir(ROOT))

    for game_folder in games_folders:
        if game_folder in ["bass-masters-classic-pro-edition", "fifa-soccer-98-road-to-world-cup", "galaxy-robo", "goal-[super-goal-]", "panic-in-nakayoshi-world"]:
            continue

        videos_folder = os.path.join(ROOT, game_folder, 'videos')
        videos = sorted(os.listdir(videos_folder))

        for video in videos:
            video = os.path.join(videos_folder, video)
            print(video)
            
            video_number = int(video[-9:-4])

            if video_number % 2 == 0: 
                os.remove(video)

eliminate_half()
