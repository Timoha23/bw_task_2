import math
import os
import struct
import wave


class BeepGenerator:
    def __init__(self):
        self.audio = []
        self.sample_rate = 44100.0

    def append_silence(self, duration_milliseconds=500):
        """
        Adding silence is easy - we add zeros to the end of our array
        """
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)

        for x in range(int(num_samples)):
            self.audio.append(0.0)

        return

    def append_sinewave(
        self,
        freq=440.0,
        duration_milliseconds=500,
        volume=1.0
    ):
        num_samples = duration_milliseconds * (self.sample_rate / 1000.0)

        for x in range(int(num_samples)):
            self.audio.append(
                volume * math.sin(2 * math.pi * freq * (x/self.sample_rate))
            )

        return

    def save_wav(self, file_name):
        # Open up a wav file
        wav_file = wave.open(file_name, "w")

        # wav params
        nchannels = 1

        sampwidth = 2

        nframes = len(self.audio)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((
            nchannels, sampwidth, self.sample_rate, nframes, comptype, compname
        ))

        for sample in self.audio:
            wav_file.writeframes(struct.pack('h', int(sample*32767.0)))

        wav_file.close()

        return


def create_wav() -> str:
    filename = "output.wav"
    bg = BeepGenerator()
    bg.append_sinewave(volume=0.25, duration_milliseconds=100)
    bg.append_silence()
    bg.append_sinewave(volume=0.5, duration_milliseconds=700)
    bg.append_silence()
    path_to_save = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
    bg.save_wav(path_to_save)
    return path_to_save
