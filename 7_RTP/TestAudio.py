#You can run and play around with this test program to check if your pydub and pyaudio modules work correctly.
#If everything is alright, when you run this program, you should hear an audio segment of "TheGall.mp3".

from pydub import AudioSegment
from pydub import playback
import pyaudio

#You can change the audio file.
#AudioSegment automatically converts whatever supported audio format into PCM/WAV audio data.
pcm_audio = AudioSegment.from_file("TheGall.mp3")
#If you want to change channels, frame rate, and sample width, uncomment the following 3 lines.
#pcm_audio = pcm_audio.set_channels(1)
#pcm_audio = pcm_audio.set_frame_rate(8000)
#pcm_audio = pcm_audio.set_sample_width(1)
frame_rate = pcm_audio.frame_rate
data = pcm_audio.raw_data

#Just try to extract an audio segment from raw data and create another AudioSegment object.
audio2 = AudioSegment(data[220000*pcm_audio.sample_width*pcm_audio.channels:1000000*pcm_audio.sample_width*pcm_audio.channels], sample_width=pcm_audio.sample_width, frame_rate=pcm_audio.frame_rate, channels=pcm_audio.channels)
print(len(audio2._data))
print(type(data))
print(len(data[10:1000]))
print(audio2.frame_width)
print(audio2.sample_width)
#Uncomment the following line if you want to play audio2.
#playback.play(audio2)

#Try playing raw audio by using PyAudio's steam playback.
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(pcm_audio.sample_width),
                channels=2,
                rate=pcm_audio.frame_rate,
                output=True)
for i in range(220000*pcm_audio.sample_width*pcm_audio.channels, 1000000*pcm_audio.sample_width*pcm_audio.channels, 2*pcm_audio.sample_width):
    stream.write(data[i : i+2*pcm_audio.sample_width])
    #print("i: {}".format(i))
stream.stop_stream()
stream.close()

p.terminate()
