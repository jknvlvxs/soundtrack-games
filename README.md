# Dataset for the paper Video-to-Music Generation for Gameplay Videos

## Introduction
This repo contains the code for generating the dataset for the paper Video-to-Music Generation for Gameplay Videos. We call it **VMDB** (Video-Music Database) and it is bases on the [NES-VMDB](https://github.com/rubensolv/NES-VMDB). The code goes through the steps to create a dataset containing pairs (audio, video) where audio is a soundtrack track from the game's original score, and video is a gameplay video where that specific track plays.

## 1. Scraping Data
This step collects HTML pages from [Zophar.net](https://www.zophar.net/music), a website that archives video game music downloads organized by console system.

### Listing Game System Tracks
`systems.py` iterate over a list of 21 game systems (e.g., SNES, NES, GBA, PS1, Sega Genesis). For each system, it navigates through all paginated listing pages on Zophar.net and saves the resulting HTML to `systems/{system}/{page}.html`.

```
python3 '01. Scrapping data/systems.py'
```

### Collecting Individual Game Pages
`scrapping.py` reads the saved system listing HTML files, extracts individual game links, then request and save each game's detail page to `data/{system}/{game}.html`. These pages contain the game metadata and soundtrack download links used in the next step.

```
python '01. Scrapping data/scrapping.py'
```

## 2. Generating Data
`generate.py` reads all the game HTML files collected in first step and parses them to extract game metadata: name, console, developer, cover image URL, emulator, release date, soundtrack archive size, and download URL. It deduplicates entries, sorts them alphabetically by name, and saves the result to `data.json`.

```
python3 '02. Generating data/generate.py'
```

The resulting `data.json` contains objects with the following fields:
- `slug`, `name`, `console`, `system`, `developer`, `cover`, `emulator`, `release_date`, `size`, `url`

## 3. Collecting YouTube Links
This step searches YouTube for a gameplay longplay video for each game in `data.json` and augments it with that information. Start by copying the file generated in the second step:

```
cp "2. Generating data/data.json" "3. Collecting youtube links/metadata.json"
```

### Collect from Youtube
`collect_youtube.py` reads `metadata.json` and searches YouTube for each game using the `youtubesearchpython` library, using the game name, console, and the query term "Longplay". Among the top 5 results, it prefers videos from the "World of Longplays" channel; otherwise it selects the first result. The `youtube.url`, `youtube.channel`, `youtube.title`, and `youtube.duration` fields are added to each entry. Progress is saved after every 100 entries. Games for which no video is found are logged in `not_found.log`.

```
python3 '03. Collecting youtube links/collect_youtube.py'
```

### Metrics

- `03. Collecting youtube links/metrics/metrics.py`: Prints the total count of entries with YouTube links, total soundtrack archive size in MB, and a breakdown of entries per console.
- `03. Collecting youtube links/metrics/duration.py`: Finds and displays the entry whose YouTube video has the longest duration.
- `03. Collecting youtube links/metrics/plots.py`: Generates bar charts showing the number of games per console and per release year.

## 4. Downloading Content

This step downloads the actual data and organizes them into the database directory structure under `5. Database/`.

`download_content.py` accepts a console slug as a command-line argument and processes all entries in `metadata.json` that match that system and already have a YouTube link. For each game it:
1. Downloads the soundtrack archive (`.zip` or `.7z`) from Zophar.net and extracts it, renaming each track to `soundtrack_XXXX.mp3`.
2. Downloads the YouTube gameplay video.
3. Slices the video into 10-second segments using `ffmpeg`.

All files are stored under `5. Database/{console}/{game}/soundtracks/` and `5. Database/{console}/{game}/videos/`. Soundtrack and video downloads run concurrently within each game, and up to two games are processed in parallel.

```
python3 '04. Downloading content/download_content.py' <console_slug>
```

Available console slugs include `nintendo-snes-spc` and others found in `metadata.json`.

### Utility Scripts

- `eliminate_half.py`: Removes even-numbered video segments from the dataset, halving the number of video clips per game.
- `remove_short_mp3.py`: Scans the soundtracks folder and removes any `.mp3` file shorter than 8 seconds.
- `metrics/video_metrics.py`: Counts and prints the number of video files in each game's `videos/` subdirectory.

## 5. Database

The `5. Database/` directory is the storage location for all content downloaded in fourth step. Its structure is:

```
1. Database/
└── {console}/
    └── {game}/
        ├── soundtracks/
        │   └── soundtrack_XXXX.mp3
        └── videos/
            └── {game}_XXXXX.mp4
```

## 6. Audio Fingerprinting

Audio fingerprinting is used to automatically map each 10-second video clip to the soundtrack track playing in it. This is done with the [Dejavu](https://github.com/worldveil/dejavu) library, which fingerprints audio using spectrogram peak pairs and matches query audio against a database of known fingerprints.

For each game, `mapping.py` creates a dedicated MySQL database, fingerprints all of the game's tracks, then extracts audio from each video clip and runs it through Dejavu's recognizer. The recognized soundtrack name and confidence scores (`input_confidence` and `fingerprinted_confidence`) are written to `mapping_log.csv` in the game folder. 

If a match is found, the video is moved into a subfolder named after the matched soundtrack (e.g., `videos/soundtrack_0001/`).

### Running the Mapping

#### With docker-compose

```
docker-compose up
```

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 mapping.py --console console_slug
```

#### Building Containers

```
docker network create vmdb_network

cd docker/mysql
docker build -t mysql .

cd docker/python
docker build -t dejavu .
```

The run command for each container is specified inside its respective Dockerfile.

### Tuning Dejavu

The following Dejavu parameters were adjusted from their defaults to improve matching accuracy on game soundtracks:

```
DEFAULT_FAN_VALUE = 10  # 15 was the original value.
DEFAULT_AMP_MIN = 7
PEAK_NEIGHBORHOOD_SIZE = 7  # 20 was the original value.
```

### Audio Duration Analysis

The `audio_duration/` folder contains scripts to inspect the duration distribution of the collected soundtracks before fingerprinting:

- `audio_duration.py`: Iterates over all soundtrack MP3s in the dataset and saves their durations (in seconds) to `durations.json`.
- `metrics.py`: Reads `durations.json` and prints summary statistics: total count, mean duration, the 5 shortest and 5 longest files, and the count of files longer than 350 seconds.
- `plot.py`: Plots a histogram of soundtrack durations, capping values at 360 seconds, and saves it as `grafico.png`.

### Utility Scripts

- `restore_dataset.py`: Reverts the mapping performed by `mapping.py`. Moves all video files from their `videos/soundtrack_XXXX/` subfolders back to the flat `videos/` directory, removes temporary MP3 extracts, and deletes `mapping_log.csv`. Useful for re-running the fingerprinting step from scratch.
- `drop_database.py`: Drops all MySQL databases created during the mapping step and then calls the same restore logic as `restore_dataset.py`.

## 7. Videos Descriptions
[Task 7](./07.%20Video%20descriptions/) leverages [VideoLLaMA 3](https://arxiv.org/abs/2501.13106) to generate descriptions for the videos. As usual, we ran the code inside a [container](07.%20Video%20descriptions/docker/). There is also the [cmd.bahs](./07.%20Video%20descriptions/cmd.bash) that sets the GPUs to use and tells HuggingFace to run the models in total offline mode. This last part is quite important to avoid a "too many requests" error.

There are two versions of our scripts, with their difference being in the prompt fo VideoLLaMA. [videollama3.py](07.%20Video%20descriptions/videollama3.py) only asks for a single genre in the game, while [videollama3_multi_gen.py](./07.%20Video%20descriptions/videollama3_multi_gen.py) lets the model talk freely about all the possible genres the game might have. The first model will store descriptions into the folder "videos_descriptions" while the second will store them in the folder "videos_descriptions_mg".

If you check your logs after getting your descriptions, you'll notice that the `try except` block in the code wasn't in vain. Here is when [remove_buggy_videos.py](./07.%20Video%20descriptions/remove_utils/remove_buggy_videos.py) come in handy. It will search for videos that got no descriptions and remove them. It is wise to check why those videos raised errors when generating the descriptions, but that is usually due to the last videos of the 10 seconds splits not having more than just a single frame. If the errors were generated by other reasons, that might indicate problems with previous steps in creting your dataset, like corrupted files and etc. The script has an option to eliminate games with no videos left, but that implicates in loosing the soundtracks of that game.

Quick debugging tip: If you just run the script to generate the descriptions again, the logs will list all the videos that raised an error.

## 08/09 Audio & Music Descriptions
We started those tasks but they didn't make into the final datasset or into the paper.

## 10. Games Genres
To get the games genres, we first make use of the WikiData API in order to try to obtain the genres directly from it. The script for such task is [get_games_genres_wikidata.py](./10.%20Games%20genres/1.%20from_wiki/get_games_genres_wikidata.py) and it will generate the `wiki_genres.json`.

Then, we use a combination of the WikiData genres with the videos descriptions as input to DeepSeek R1. The script for such task is [get_genres_deepseek.py](./10.%20Games%20genres/2.%20wiki_descriptions_and_deepseek/get_genres_deepseek.py). Again, there are two possibilities, one is to use the single genre descriptions and get a single genre for each game, and the other is to use the multi genre descriptions, and get multiple genres in a priority order. In both cases, DeepSeek's task is to map the input to the following genres: Shooters, Sports, Platform, RPG, Puzzle, Action, Fighting, Strategy, Simulation, Adventure and Racing. The output will be a json saved in every game folder, but [get_csv.py](./10.%20Games%20genres/4.%20analysing/get_csv.py) can be used to join the information into a single csv file.

In order to run [get_genres_deepseek.py](./10.%20Games%20genres/2.%20wiki_descriptions_and_deepseek/get_genres_deepseek.py) the DeepSeek R1 model needs to be available in the Ollama API, with the endpoint exposed to the environment variable `OLLAMA_ADDRES`. In order to do so, one can use [this container](./10.%20Games%20genres/2.%20wiki_descriptions_and_deepseek/docker/Dockerfile), following the commands at [cmd.bash](./10.%20Games%20genres/2.%20wiki_descriptions_and_deepseek/cmd.bash) (commands were only tested copying and pasting line by line).

## Back to 6.
### Selecting Dejavu Confidence
After generating videos descriptions, we are going to split the dataset in two. One will be the normal or mapped dataset, and the other will be the unmapped one. This split is made according to the values of confidence outputed by Dejavu when mapping videos and soundtracks. Low confidence valus indicate that the mapping is wrong, therefore it would be just noise when training any Video2Music model. With that being said, if you are just concerned with audio, as in our [Genre Classifier](https://github.com/FelipeMarra/passt-on-vmdb), then you may want to use both mapped and unmapped audios.

The code for this is at `06. Audio fingerprinting/select_confidence`

Confidence values are usually small, but there are ones like $input\_confidence=3$.  A typical input confidence value would be something around $0.35$, and a typical fingerprinted confidence is much smaller, like $0.02$. It makes no sense to put our threshold at 0, because it would be what we were already doing, that is, just accepting every map. Neither it does to put it at 3, because we would cut off almost every map.

A good plan to obtain such value is to rank the mappings from the lowest to the highest confidence, and look at from what confidence values the mappings start to get right. To do so, we might perform the following steps:

1. Rank the games from the worst mapped to the best one. 
2. Since we are looking inside the worst-mapped games, we order the videos from the best to the worst mapped, because there will be a small number of videos with high confidence values in such games. 
3. Annotate the mappings until they start to get wrong, attributing the correct soundtrack to the video in case Dejavu is right, and None otherwise. In this way, when the confidence is above the threshold, the Dejavu mapping must be the same as the annotated one, and it will be, since we only annotate the mappings when Dejavu is right. And when the confidence is below the threshold, the annotation must be None.
4. Run a search to know which confidence values maximize the Dejavu mapping accuracy in relation to the annotated data. 

In practice, a single confidence value, let us call it $total\_confidence$, was used to rank the games and videos, given by

$total\_confidence = input\_confidence + 10*fingerprinted\_confidence$

the $10*fingerprinted\_confidence$ was needed to compensate for the fact that the fingerprinted confidence is usually an order of magnitude smaller. The $total\_confidence$ value not only aggregates both confidences, but also forces the same weight for both, which is desirable since we don’t know if one is more important than the other. 

To rank the games, the mean of the input and fingerprinted confidence was taken across all the mappings of the game, and then the total confidence was calculated. This was done at [get_games_with_lowest_confidence.py](./06.%20Audio%20fingerprinting/select_confidence/get_games_with_lowest_confidence.py).

Since it makes no sense to start annotating from the first games, because at least the first few tens will be just 100% wrong mappings, this was verified empirically, we skipped games where total confidence was below $0.2$, that is, the first 456 games.

We manually annotated 109 videos in [videos_gt.json](./06.%20Audio%20fingerprinting/select_confidence/videos_gt.json) - the goal was 100, but by using the following annotation methodology, we ended up with 109. For each game, we order its videos by total confidence values in descending order. From this list, we listen to the examples until we find the first right one. From the first right onwards, we annotate until we reach 3 examples incorrectly mapped by Dejavu. Then, we go on to the next game. If the top 3 examples are wrongly classified, we skip to the next game. We proceed until we have 100 annotated examples. Whenever Dejavu mismatches the video, the soundtrack is labeled with "NaN".

If a soundtrack appears more than once, only the last annotation, that is, the one with the lowest total confidence, will be kept. Examples that look more like sound effects, like the battle-submarine's soundtrack 8, were skipped. Videos containing two soundtracks, with no clear dominance of one of them, like bishoujo-janshi-suchie-pai video 00001, were skipped. Videos with a few seconds, like jleague-soccer-prime-goal-2 video 00017, were skipped.

As an empirical proof of how much this method of annotation works, in the game Alddin, 108 videos were annotated until the 3 errors. If one continues on annotating, only 4 more songs will be right, and then it will be in very low confidence values, attributing songs to silent videos and etc.

Finally, we use [grid_search_confidence.py](06.%20Audio%20fingerprinting/select_confidence/grid_search_confidence.py) to run a grid search that aims at maximizing the accuracy of Dejavu matches by setting a threshold on input and fingerprinted confidence metrics, taking as ground truth the annotations in videos_gt.json. Examples with values below such thresholds will be "discarded", as they are probably wrong mappings, including videos with no music at all.

Results show that $input\_confidence=0.0$ and $fingerprinted\_confidence=0.01$ yield the best accuracy on the annotated data, of $83\%$, while losing $16\%$ of the mapped videos. The videos below the threshold were unmapped by [apply_confidence_filter.py](./06.%20Audio%20fingerprinting/select_confidence/apply_confidence_filter.py).

Fun fact: Running the grid search on the total confidence, instead of separated input and fingerprinted confidences, bumps the accuracy by 1% while losing another 1% of the data.

### Move Unmpaed Soundtracks and Videos
We run `06. Audio fingerprinting/move_unmapped_after_dejavu.py` to move all the following files:

* soundtracks smaller than 8 seconds
* videos smaller than 10 seconds (9 seconds in practice because many videos have nine dot something seconds)
* sounstracks with no corresponding videos
* videos with no corresponding soundtracks

to a separated folder, a "parallel" dataset with data that is not useful for our training purposes. One can run the TODO script to merge both of this datasets.

## 11. Split Dataset

This step organizes the mapped dataset into a tabular index, optionally downsamples it for genre balance, and produces train/eval/test splits.

### 11.1. Get videos info

`get_videos_info.py` traverses the dataset directory and collects every mapped video segment (i.e., files inside `videos/soundtrack_XXXX/` subfolders). It cross-references each game against `deepseek_genres.csv` to attach a genre label, and writes the result to `videos_info.csv` with columns: `index`, `game_id`, `soundtrack`, `segment`, and `genre`.

```
python3 '11. Split dataset/1. get_videos_info/get_videos_info.py' --dataset_root <path> --console <console_slug>
```

### 11.2. Downsample

`downsample.py` reads the `videos_info.csv` produced in the previous step and performs genre-balanced downsampling. It:
1. Computes a target video segment count for each genre based on `smallest_genre_count × 1.5`, to approximate a uniform distribution without discarding too much data.
2. For each game, derives a per-soundtrack target video segment count proportional to the genre weight.
3. Selects segments at linearly spaced indices within each soundtrack, skipping the first and last to avoid opening and ending screens.

The result is saved as `videos_info.csv` inside the `2. downsample/` folder.

```
python3 '11. Split dataset/2. downsample/downsample.py'
```

### Plots

`plots/plot_videos_info.py` generates distribution statistics and bar charts for both the full and downsampled datasets. It reports soundtracks per game and genre, videos per game, genre, and soundtrack, and per-split breakdowns once splits are available. Output files (`.txt` tables and `.png` charts) are written to `plots/full/` or `plots/downsample/` depending on the `--downsampled` flag.

```
# On the full dataset
python plot_videos_info.py

# On the downsampled dataset
python plot_videos_info.py --downsampled
```

### 11.3. Split

`split.py` splits the dataset at the game level using [Priority Grouped Stratified Split](https://github.com/jpmedras/grouped_stratified_split), which assigns games to partitions while preserving the genre distribution across splits. The default ratio is 50% train / 40% eval / 10% test, since we used the eval dataset to train evaluation models. The resulting lists of game IDs are saved as `splits/train.txt`, `splits/eval.txt`, and `splits/test.txt`.

```
python3 '11. Split dataset/3. split/split.py'
```

## 12. Convert to Audioset
Scripts used to create the metadata in the [Audiocraft](https://github.com/facebookresearch/audiocraft) format. This is the format expected to train our models and baselines.