# VMDB - Video-Music Database
VMDB (Video-Music Database) is a repository aimed at demonstrating the steps to create a dataset containing a list of n pairs (a, v) for a specific game. In this dataset, a represents an audio track from the game’s soundtrack, and v is a gameplay video of the game where the specific audio track plays. 

## Getting Extensions to Download Using ffmpeg

In the `1. Scraping VGM Data/extensions/` directory, you will find `extensions.json`, which is collected from `extensions.html`. This file contains all extensions gathered from the VGM website.

To extract data from the `.html` file and create `extensions.json`, run:
```
python extensions.py
```

Next, you need to check which of these extensions can be converted to `.mp3` using **ffmpeg**. In the `/ffmpeg` directory, there are 3 `.txt` files with the output of **ffmpeg** commands that list supported extensions.

To verify if each format in `extensions.json` is supported by **ffmpeg**, run:
```
python convert.py
```

This will generate the `convert.json` file, which will be used later in the data scraping process.

## Running the Scraping Script on the VGM Site

To collect data, you need to search for game consoles/systems on the VGM website. We have collected this data manually, and you can find it in `1. Scraping VGM Data/systems/`.

Now, run the script to collect all data. This process will take some time, so please be patient:
```
python scraping.py
```

This script will search every page for all systems listed in `systems.json` and all extensions in `convert.json`, then download the `.html` files. The data will be saved in `1. Scraping VGM Data/data/`.

## Cleaning Up HTML Files Without Soundtrack Links

Now, we need to clean up `.html` files that do not contain soundtrack links by running:
```
python cleaning.py
```

## Generating `data.json`

In the `2. Generating data/` directory, we will run script that organizes the collected data into a file.

To organize the data, there's a script to create a `.json` file that merges all collected links and games. Run:
```
python generate.py
```

This will generate the `data.json` file, which includes information such as:
- Name
- Date
- System
- Size
- URL
- YouTube  
  - URL
  - Title
  - Channel
  - Duration

## Viewing Collected Data Metrics

To view the amount of raw data collected, run:
```
python metrics.py
```

## Collecting Youtube Videos
Copy the data file to the step 3, to collect youtube links
```
cp 2.\ Generating\ data/data.json 3.\ Collecting\ Youtube\ Links/
```

Now, the code is ready to collect youtube links
```
python collect_youtube.py | tee -a youtube.txt
```

## Downloading Content
```
python download_content.py console_slug
```

The list of consoles slugs are:
- `nintendo-snes-spc`

## Audio Fingerprinting

### Create mysql database for dejavu using docker
6. Audio fingerprinting
  
```
docker-compose up
```

```
python3.7 -m venv env
source env/bin/activate
pip install -r requirements.txt
<!-- python3.7 dejavu_mapping.py -->
python3.7 mapping.py --console console_slug
```

### Running in container
```
docker network create vmdb_network

cd docker/mysql
docker build -t mysql .

cd docker/python
docker build -t dejavu .
```

The running command is on each Dockerfile

### Tuning Dejavu
```
DEFAULT_FAN_VALUE = 10  # 15 was the original value.
DEFAULT_AMP_MIN = 7
PEAK_NEIGHBORHOOD_SIZE = 7  # 20 was the original value.
```

### Selecting Dejavu Confidence
First we used `get_games_with_lowest_confidence.py` to get the games with the lowest input and fingerprinted confidences. This is done by averaging those mestrics across all videos of the game, than suming the results of both and getting the games with the lowest values. Fingerprinted confidence mean is multiplied by 10 since its values are usually much smalled than the input confidence ones.

Top 10 games with lower confidence, by the above calculation, were:
1. cute-angela-great-journey
2. honkakuha-taikyoku-shougi-shougi-club
3. frognes
4. classic-road
5. john-madden-football-93-1992
6. hungry-dinosaurs
7. cyber-knight-ii-chikyuu-teikoku-no-yabou
8. james-pond-3-operation-starfish
9. international-superstar-soccer
10. international-superstar-soccer-deluxe

Unsurprisingly, the top 4 games of the list above had to be **removed from the dataset**, beucause on all of them there wasn't a single correct match.

Than, we manually annotate 100 videos in `videos_gt.json`. To choose the videos, we follow the list of games with lower confidence. For each game we order it's videos by confidence values, obtained by summing `input_confidence + 10*fingerprinted_confidence`. This is done in `get_ordered_videos_by_confidence.py`. From this list, we manually go from the lower confidence to the higher one until we find the first example FE were Dejavu's match is right. We annotate the 5 examples below FE and the 5 examples from FE up. If the first example is right already, then we would only anotate 5 examples, that is, the 5 from FE up. We repeat this for each game until we reach 100 annotated examples. This was done in order to obtain the lower input and fingerprinted confidences from which Dejavu's matches start to get accurate.

Finally, we use `grid_search_confidence.py` to run a grid search that aims at maximizing the accuracy of Dejavu matches by setting a threshold on input and fingerprinted confidences metrics, taking as groundtruth the annotations at `videos_gt.json`. Examples with values below such thresholds will be "discarted", as they are probably videos with no music at all.

## Games genres

Generates deepseek_genres.csv to the next step

## Split dataset

### get_videos_info
```
python get_videos_info.py

will generate file videos_info.csv with all dataset
```

### load_downsample
```
get selected_videos.jsonl from step 07 to assert that every soundtrack will have at least one video selected

filter videos_info.csv with the selected_videos.jsonl will generate a new videos_info.csv
```

> python downsample.py && cd ../plots && python plot_videos_info.py --downsampled && cd ../load_downsample

> rm -rf videos_info.csv && rm -rf ../plots/downsample


### plots
```
run plots to get dataset info
```

### split
```
run split with selected_videos_info.csv
```