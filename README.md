# About
A repo to play around with audio and DSP in general.

Currently includes:
- A script to read audio in real time from the mic and plot it both in time and frequency (spectrogram) domains

## :hammer_and_wrench:Setup/ Preparation
1) Make sure you have
```bash
sudo apt-get install python3.9-tk # for matplotlib GUI backend
sudo apt-get install python3.9-dev # needed to pip install PyAudio
sudo apt-get install portaudio19-dev python-pyaudio # Might also be needed for PyAudio
```
2) Setup the pipenv as follows
```bash
pipenv install --ignore-pipfile --python 3.9
pipenv shell
```

## Usage examples
WIP
