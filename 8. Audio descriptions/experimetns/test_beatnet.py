import yaml
import warnings
from BeatNet.BeatNet import BeatNet
from chord_extractor.extractors import Chordino
from utils import BeatProcessor, ChordProcessor, get_bpm, get_key
from essentia.standard import MonoLoader, KeyExtractor

warnings.filterwarnings('ignore')

config_path = "/app/code/experimetns/music_feat_extractor_config.yaml"
file_path = "/app/dataset/nintendo-snes-spc/legend-of-zelda-the-a-link-to-the-past/soundtracks/soundtrack_0003.mp3"

with open (config_path, 'r') as f:
    cfg = yaml.safe_load(f)

# BPM
beat_estimator = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)
beat_processor = BeatProcessor(beat_estimator, **cfg['beat_processor'])

# TODO how to get the time signature from the beats and tempo count
bf = beat_processor(file_path)
bpm = get_bpm(bf)

print(f"{bpm} BPM")

# Key Librosa
key, corr, altkey, altcorr=get_key(file_path)

print(f"{key}, {corr}, {altkey}, {altcorr}")

# Key Essentia
audio = MonoLoader(filename=file_path, sampleRate=16000, resampleQuality=4)()
keyex = KeyExtractor(sampleRate=16000)
detkey = keyex(audio)

print(detkey)

# Chords
chord_estimator = Chordino()  
chord_processor = ChordProcessor(chord_estimator,**cfg['chord_processor'])
chords=chord_processor(file_path)

c_type=[]
c_time=[]
for ch in chords:
    c_type.append(ch[0])
    c_time.append(ch[1])

print(c_type)
print(c_time)