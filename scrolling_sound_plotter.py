import numpy as np
import pyaudio
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import wave
plt.style.use('dark_background')

BUFFER_SIZE = 1024  # Samples per buffer: How many samples to group in one buffer for processing(chunk size)
SAMPLE_RATE = 44100 # Samples per second (Hz)
SAMPLE_TIME = 1/SAMPLE_RATE # Sec per sample

# For live mode with scrolling
PLOT_WINDOW_SIZE = BUFFER_SIZE*100

dB_min = -96
dB_max = 96 # For 16bit audio. 20* log(2^16 - 1)

live_mode = True # Plots mic input in real time if True. Otherwise plots a wav file.
scrolling = True # Used with live mode to scroll older time samples to the left. Otherwise, the realtime plot only shows one buffer data at a time.

# PyAudio and stream global variables to use in case of live mode
p = None
stream = None

# t, x, y global variables to use in case of live mode
t = None
x = None
y = None

# Two rows each with one subplot
fig, ax = plt.subplots(2, 1, figsize=(8,6))
#Time domain plot and freq domain spectrogram initialization
line, = ax[0].plot([], [], lw=1)
_, _, _, im = ax[1].specgram([], Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')

# workaround to avoid reducing the plot size due to colorbar..
# hspace is to control the spacing between the two plots
fig.subplots_adjust(right=0.85, hspace=0.1)
# getting the lower left (x0,y0) and upper right (x1,y1) corners:
[[x10,y10],[x11,y11]] = ax[1].get_position().get_points()
pad = 0.03; width = 0.02
# Colorbar
cbar_ax = fig.add_axes([x11+pad, y10, width, y11-y10])
fig.colorbar(im, cax=cbar_ax, label = 'Intensity(dB)')

#Amplitudes can go up to 2^15 (in case of signed int16) if the MIC volume is set to max
#otherwise signals will be clipped at the mic volume level.
ax[0].set_ylim((-2**15, 2**15))
ax[0].set_ylabel('Amplitude')
ax[1].set_ylabel('Frequency (Hz)')
ax[1].set_xlabel('Time')

def init():
    _, _, _, im = ax[1].specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')
    line.set_data(x, y)
    return line, im,

def animate(i):
    global im
    global x, y, t
    global p, stream
    global ax
    global scrolling
    im.remove()
    ax[0].set_xlim(x[0],x[-1])
    line.set_data(x, y)
    _, _, _, im = ax[1].specgram(y, Fs=SAMPLE_RATE, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')

    t += SAMPLE_TIME * (BUFFER_SIZE)
    prev_x = x
    prev_y = y
    # Read a new buffer
    x = np.linspace(t, t + SAMPLE_TIME * (BUFFER_SIZE-1), BUFFER_SIZE)
    y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)
    if scrolling:
        # Stack buffer to older data within the plot window size if in scroll mode
        x = np.hstack([prev_x,x])[-PLOT_WINDOW_SIZE:]
        y = np.hstack([prev_y,y])[-PLOT_WINDOW_SIZE:]
    return line, im,

def extract_data_from_file(filename, channel=0):
    """
    Returns numpy arrays containing the specified channel data, time data and sample rate.
    """
    wav_obj = wave.open(filename, 'rb')
    sample_rate = wav_obj.getframerate()

    sample_count = wav_obj.getnframes()
    file_length = sample_count/sample_rate

    n_channels = wav_obj.getnchannels()
    print(f'This file has {n_channels} channels. Returning the {channel}th channel data')

    file_buffer = wav_obj.readframes(sample_count)

    signal_np = np.frombuffer(file_buffer, dtype=np.int16)
    channel_data = signal_np[channel::n_channels]
    times = np.linspace(0, file_length-1, num=sample_count)
    return channel_data, times, sample_rate

def main():
    global x, y, t
    global p, stream
    #parser = argparse.ArgumentParser(description='sound_visualizer.py: A script to visualize sound in time and frequency domains')
    #parser.add_argument('-f','--file', help='Show a reference piano keyboard', action ='store_true', metavar = '')
    #parser.add_argument('-s','--scroll', help='Runs live mode with scrolling over time', action ='store_true', metavar = '')
    if live_mode:
        # PyAudio and stream setup
        p = pyaudio.PyAudio()
        stream=p.open(format=pyaudio.paInt16,channels=1,rate=SAMPLE_RATE,input=True,
                      frames_per_buffer=BUFFER_SIZE)
        t = 0
        # Prepare and read the first buffer
        x = np.linspace(t, t + SAMPLE_TIME * (BUFFER_SIZE-1), BUFFER_SIZE)
        y = np.frombuffer(stream.read(BUFFER_SIZE), dtype=np.int16)

        fig.canvas.manager.set_window_title(f'Sound visualizer: Live mode(Mic) {"with scrolling" if scrolling else "one buffer at a time"}')
        # Hide the time axis ticks. Can't blit animate updating the time ticks without a major slow down.
        ax[0].tick_params(labelbottom=False)
        ax[1].tick_params(labelbottom=False)
        if scrolling:
            ax[0].set_xlim(0, t + SAMPLE_TIME * (PLOT_WINDOW_SIZE-1))
        else:
            ax[0].set_xlim(0, t + SAMPLE_TIME * (BUFFER_SIZE-1))
        anim = FuncAnimation(fig, animate, init_func=init, interval=1, blit=True)
        plt.show()
        # stop and close the audio stream
        stream.stop_stream()
        stream.close()
        p.terminate()
    else:
        # File mode
        fig.canvas.manager.set_window_title('Sound visualizer: File mode')
        amplitudes, times, sample_rate = extract_data_from_file('./gtr-dist-yes.wav')
        ax[0].set_xlim(0, times[-1])
        line.set_data(times, amplitudes)
        spec, freq, t, im = ax[1].specgram(amplitudes, Fs=sample_rate, vmin=dB_min, vmax=dB_max, cmap='jet', mode='magnitude')
        plt.show()

if __name__ == '__main__':
    main()
