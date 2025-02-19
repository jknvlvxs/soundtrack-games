from BeatNet.BeatNet import BeatNet

estimator = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)

output = estimator.process("/app/dataset/nintendo-snes-spc/legend-of-zelda-the-a-link-to-the-past/soundtracks/soundtrack_0003.mp3")

print(output)

#TODO https://github.com/AMAAI-Lab/mustango/blob/main/utils/extract_features.py