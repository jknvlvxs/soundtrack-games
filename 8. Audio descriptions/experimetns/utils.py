import os
import numpy as np
import soundfile as sf
from scipy.io.wavfile import write

class BeatProcessor(object):
	def __init__(self, estimator, if_aux_click, aux_click_save_path):
		self.estimator = estimator
		self.if_aux_click = if_aux_click
		self.aux_click_save_path = aux_click_save_path
	def __call__(self, path):
		Output = self.estimator.process(path)
		click_timing, click_beat = Output[:, 0], Output[:, 1]	

		if self.if_aux_click and self.aux_click_save_path:
			os.makedirs(self.aux_click_save_path, exist_ok=True)

			input_file, sr = sf.read(path)
			input_file = get_audio_mono(input_file)
			total_time = len(input_file)/sr
			click_track = create_click_track(sr, impulse_dur = 0.02, click_timing = click_timing, click_beat = click_beat, total_time = total_time)
			name = path.split("/")[-1][:-4]+"click.wav"
			write(f"{self.aux_click_save_path}/{name}", sr, (click_track+input_file).astype(np.float32))

		
		return click_timing, click_beat #each is a numpy array with an arbitrary len

class sine_creator(object):
	def __init__(self, dur, sr, amp=None):

		"""
		    gen = sine_creator(dur = 2, sr = 16000)
		    gen([440, 880, 220])
		"""
		self.dur = dur
		self.sr = sr
		self.amp = amp #between [0,1]
	def __call__(self, freqs = []):
		t = np.linspace(0., 1., int(self.dur*self.sr))
		if self.amp is None:
			self.amp = 1/len(freqs)
		sins = sum([self.amp*np.sin(2. * np.pi * f * t) for f in freqs])
		# name = "_".join([str(x) for x in freqs])+".wav"
		# write(name, self.sr, sins.astype(np.float32))

		return sins.astype(np.float32)

def create_click_track(sr, click_timing = [1, 2, 3, 4], click_beat = [1, 2, 3, 4, 1, 2], total_time = 5, impulse_dur = 0.1):
	click_track = np.zeros(int(np.ceil(total_time*sr)))
	downbeat = sine_creator(dur = impulse_dur, sr = sr, amp = 0.4)
	downbeat_click = downbeat([110, 55, 25])


	beat_ = sine_creator(dur = impulse_dur, sr = sr, amp = 0.25)
	beat_click = beat_([55, 25, 12])

	for click, beat in zip(click_timing, click_beat):

		if beat == 1:
			if click !=0:
				tmp_click = np.concatenate( (np.zeros(int((click - impulse_dur)*sr)),  downbeat_click,  np.zeros(int((total_time - click)*sr))  ) )
			else:
				tmp_click = np.concatenate( ( downbeat_click,  np.zeros(int((total_time - impulse_dur)*sr))  ) )
		else: 
			if click!=0:
				tmp_click = np.concatenate( (np.zeros(int((click - impulse_dur)*sr)),  beat_click,  np.zeros(int((total_time - click)*sr))  ) )
			else:
				tmp_click = np.concatenate( ( beat_click,  np.zeros(int((total_time - impulse_dur)*sr))  ) )

		#pad
		if len(tmp_click)>len(click_track):
			tmp_click = tmp_click[:len(click_track)]
		elif len(tmp_click)<len(click_track):
			tmp_click = np.concatenate((tmp_click, np.zeros(len(click_track)-len(tmp_click))))
		
		click_track += tmp_click

	return click_track

def get_bpm(beats):
	#get diff
	if len(beats[0])<3: #too little beats to determine bpm
		return None
	diff=np.diff(beats[0])
	loc_bpm=1/diff*60
	#median filter the diff
	loc_bpm2=np.concatenate((np.array(loc_bpm[0]).reshape(1),loc_bpm,np.array(loc_bpm[-1]).reshape(1)))
	for i in range(len(loc_bpm2)-1):
		loc_bpm2[i+1]=np.median(loc_bpm2[i:i+3])
	loc_bpm=loc_bpm2[1:-1]
	avg_bpm = np.round(np.mean(loc_bpm))
	# return (bpm, markers), avg_bpm
	return avg_bpm

def get_audio_mono(audio:np.ndarray) -> np.ndarray:
    audio = np.mean(audio, axis=1, keepdims=False) # for audio with shape [T, C]

    return audio