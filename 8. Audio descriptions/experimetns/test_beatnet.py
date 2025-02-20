import yaml
from BeatNet.BeatNet import BeatNet
from utils import BeatProcessor, get_bpm

config_path = "/app/code/experimetns/music_feat_extractor_config.yaml"

with open (config_path, 'r') as f:
    cfg = yaml.safe_load(f)

beat_estimator = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)
beat_processor = BeatProcessor(beat_estimator, **cfg['beat_processor'])

#output = beat_estimator.process()
file_path = "/app/dataset/nintendo-snes-spc/legend-of-zelda-the-a-link-to-the-past/soundtracks/soundtrack_0003.mp3"
bf=beat_processor(file_path)
bpm=get_bpm(bf)

print(bpm)