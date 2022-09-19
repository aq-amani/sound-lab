import numpy as np
import pyaudio
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import wave
plt.style.use('dark_background')

BUFFER_SIZE = 1024  # Samples per buffer: How many samples to group in one buffer for processing(chunk size)
SAMPLE_RATE = 44100 # Samples per second (Hz)
SAMPLE_TIME = 1/SAMPLE_RATE # Sec per sample

PLOT_WINDOW_SIZE = BUFFER_SIZE*120

dB_min = -96
dB_max = 96 # For 16bit audio. 20* log(2^16 - 1)
p = pyaudio.PyAudio()

stream=p.open(format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,input=True,
              frames_per_buffer=BUFFER_SIZE)

live_mode = True # Plots mic input in real time True

fig, ax = plt.subplots(2, 1, figsize=(8,6))

#time domain
t = 0
#x = np.linspace(0, BUFFER_SIZE-1, BUFFER_SIZE)
x = np.linspace(t, t + SAMPLE_TIME * (BUFFER_SIZE-1), BUFFER_SIZE)
y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)

#Amplitudes can go up to 2^15 (in case of signed int16) if the MIC volume is set to max
#otherwise signals will be clipped at the mic volume level.
ax[0].set_ylim((-2**15, 2**15))

if live_mode:
    ax[0].set_xlim(0, t + SAMPLE_TIME * (PLOT_WINDOW_SIZE-1))
#else:
# setting for one buffer plotting
#    ax[0].set_xlim(0, t + SAMPLE_TIME * (BUFFER_SIZE-1))

ax[0].set_ylabel('Amplitude')
ax[0].tick_params(labelbottom=False)
ax[1].tick_params(labelbottom=False)

line, = ax[0].plot([], [], lw=1)
#freq domain
_, _, _, im = ax[1].specgram([], Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')

# workaround to avoid reducing plot size due to colorbar..
fig.subplots_adjust(right=0.85, hspace=0.1)  # hspace is to give enough spacing between the two plots
# getting the lower left (x0,y0) and upper right (x1,y1) corners:
[[x10,y10],[x11,y11]] = ax[1].get_position().get_points()
pad = 0.03; width = 0.02
cbar_ax = fig.add_axes([x11+pad, y10, width, y11-y10])
fig.colorbar(im, cax=cbar_ax, label = 'Intensity(dB)')

ax[1].set_ylabel('Frequency (Hz)')
ax[1].set_xlabel('Time')

def init():
    _, _, _, im = ax[1].specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')
    line.set_data(x, y)
    return line, im,

def animate(i):
    global im
    global t
    global x
    global y
    global ax
    im.remove()
    ax[0].set_xlim(x[0],x[-1])
    line.set_data(x, y)
    _, _, _, im = ax[1].specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')

    t += SAMPLE_TIME * (BUFFER_SIZE)
    x_new = np.linspace(t, t + SAMPLE_TIME * (BUFFER_SIZE-1), BUFFER_SIZE)
    y_new = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    x = np.hstack([x,x_new])[-PLOT_WINDOW_SIZE:]
    y = np.hstack([y,y_new])[-PLOT_WINDOW_SIZE:]
    return line, im,

def extract_data_from_file(filename):
    """
    Returns numpy arrays containing left/right channels, time data and sample rate.
    """
    wav_obj = wave.open(filename, 'rb')
    sample_rate = wav_obj.getframerate()

    sample_count = wav_obj.getnframes()
    file_length = sample_count/sample_rate

    n_channels = wav_obj.getnchannels()

    file_buffer = wav_obj.readframes(sample_count)

    signal_np = np.frombuffer(file_buffer, dtype=np.int16)

    l_channel = signal_np[0::2]
    r_channel = signal_np[1::2]

    times = np.linspace(0, file_length-1, num=sample_count)
    return l_channel, r_channel, times, sample_rate

if live_mode:
    # Real time plotting with scrolling
    anim = FuncAnimation(fig, animate, init_func=init, interval=1, blit=True)
else:
    # Plot a wav file
    #y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    #line.set_data(x, y)
    #spec, freq, t, im = ax[1].specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')
    #print(t[-1], x[-1], t.shape, x.shape,"\n", t)
    l, r, t, sample_rate = extract_data_from_file('./gtr-dist-yes.wav')
    ax[0].set_xlim(0, t[-1])
    line.set_data(t, l)
    spec, freq, t, im = ax[1].specgram(l, Fs=sample_rate, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')

plt.show()

# stop and close the audio stream
stream.stop_stream()
stream.close()
p.terminate()
