import numpy as np
import pyaudio
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use('dark_background')

BUFFER_SIZE = 1024  # Samples per buffer: How many samples to group in one buffer for processing(chunk size)
SAMPLE_RATE = 44100 # Samples per second (Hz)

dB_min = -96
dB_max = 96
p = pyaudio.PyAudio()

stream=p.open(format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,input=True,
              frames_per_buffer=BUFFER_SIZE)

time_domain = False # Plots amplitudes in time if True. Plots a spectogram if False
animate_flag = True # Plots one buffer from the mic if False. Plots mic input in real time if True

fig = plt.figure()

if time_domain:
    #time domain
    x = np.linspace(0, BUFFER_SIZE-1, BUFFER_SIZE)
    #Amplitudes can go up to 2^15 (in case of signed int16) if the MIC volume is set to max, otherwise signals will be clipped at the mic volume level.
    ax = plt.axes(xlim=(0, BUFFER_SIZE-1), ylim=(-10000, 10000))
    ax.set_ylabel('Amplitude')
    ax.set_xlabel('Samples in one buffer')

    line, = ax.plot([], [], lw=1)
else:
    #freq domain
    _, _, _, im = plt.specgram([], Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet')
    #_, _, _, im = plt.specgram([], Fs=SAMPLE_RATE)
    plt.colorbar(label = 'Intensity(dB)')
    plt.ylabel('Frequency (Hz)')

def init_time():
    line.set_data([], [])
    return line,

def animate_time(i):
    global max
    y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    line.set_data(x, y)
    return line,

def init_freq():
    _, _, _, im = plt.specgram([], Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet')
    return im,

def animate_freq(i):
    # clear previous spectrogram image otherwise animation performance suffers
    global im
    im.remove()
    y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    _, _, _, im = plt.specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet')
    return im,

if animate_flag:
    # Real time plotting: Each animation frame is one audio buffer
    anim = FuncAnimation(fig, animate_time if time_domain else animate_freq, init_func=init_time if time_domain else init_freq, interval=1, blit=True)
else:
    # Record one buffer and plot it
    y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    if time_domain:
        line.set_data(x, y)
    else:
       spec, freq, t, im = plt.specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet')
       #spec, freq, t, im = plt.specgram(y, Fs=SAMPLE_RATE)
       #dt = 0.005
       #t = np.arange(0.0, 20.0, dt)
       #x = 100 * np.sin(0.05 * t)
       #spec, freq, t, im = plt.specgram(x, NFFT=100, noverlap=0, Fs=1)
       #print(spec, freq, t, im)

plt.show()

# stop and close the audio stream
stream.stop_stream()
stream.close()
p.terminate()
